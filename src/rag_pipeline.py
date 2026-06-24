"""
rag_pipeline.py — supports OpenAI, Anthropic, and Google Gemini (via REST).
"""

from dataclasses import dataclass, field
from typing import List, Optional
import requests

from src.multilingual import LanguageDetector
from src.retriever import Retriever, RetrievedChunk
from src.utils import get_env_var, get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are a professional, friendly customer support assistant. \
Answer customer questions using ONLY the context below from the company knowledge base.

Rules:
1. Base answers strictly on the provided context only.
2. If context lacks the answer, say you don't have that information.
3. Be concise, warm, and professional.
4. {language_instruction}

Context:
---
{context}
---
"""

NO_CONTEXT_FALLBACK = (
    "I don't have information about that in our knowledge base. "
    "Could you rephrase, or contact our human support team?"
)


@dataclass
class ChatResponse:
    answer: str
    sources: List[RetrievedChunk] = field(default_factory=list)
    language_code: str = "en"
    language_name: str = "English"
    used_context: bool = False
    error: Optional[str] = None


class LLMProviderError(Exception):
    pass


class RAGPipeline:
    def __init__(self, retriever: Retriever, provider: Optional[str] = None,
                 model_name: Optional[str] = None, temperature: float = 0.3) -> None:
        self.retriever = retriever
        self.language_detector = LanguageDetector()
        self.temperature = temperature
        self.provider = (provider or get_env_var("LLM_PROVIDER", "gemini")).lower()

        if self.provider not in {"openai", "anthropic", "gemini"}:
            self.provider = "gemini"

        default_models = {
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-5",
            "gemini": "gemini-2.5-flash",
        }
        self.model_name = model_name or default_models[self.provider]
        self._client = self._init_client()

    def _init_client(self):
        if self.provider == "openai":
            api_key = get_env_var("OPENAI_API_KEY")
            if not api_key:
                raise LLMProviderError("OPENAI_API_KEY is not set.")
            from openai import OpenAI
            return OpenAI(api_key=api_key)

        elif self.provider == "anthropic":
            api_key = get_env_var("ANTHROPIC_API_KEY")
            if not api_key:
                raise LLMProviderError("ANTHROPIC_API_KEY is not set.")
            import anthropic
            return anthropic.Anthropic(api_key=api_key)

        else:
            api_key = get_env_var("GEMINI_API_KEY")
            if not api_key:
                raise LLMProviderError("GEMINI_API_KEY is not set.")
            return {"api_key": api_key}

    def generate_response(self, query: str,
                          chat_history: Optional[List[dict]] = None) -> ChatResponse:
        chat_history = chat_history or []
        language_code, language_name = self.language_detector.detect_with_name(query)

        try:
            context, chunks = self.retriever.retrieve_and_build_context(query)
        except Exception as exc:
            logger.error("Retrieval failed: %s", exc)
            return ChatResponse(
                answer="I'm having trouble accessing the knowledge base. Please try again.",
                language_code=language_code, language_name=language_name, error=str(exc))

        if not context:
            return ChatResponse(answer=NO_CONTEXT_FALLBACK, sources=[],
                                language_code=language_code, language_name=language_name)

        language_instruction = self.language_detector.build_language_instruction(language_code)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            context=context, language_instruction=language_instruction)

        try:
            answer = self._call_llm(system_prompt, query, chat_history)
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            return ChatResponse(
                answer="I'm sorry, I encountered an error. Please try again.",
                sources=chunks, language_code=language_code,
                language_name=language_name, used_context=True, error=str(exc))

        return ChatResponse(answer=answer.strip(), sources=chunks,
                            language_code=language_code, language_name=language_name,
                            used_context=True)

    def _call_llm(self, system_prompt: str, query: str, chat_history: List[dict]) -> str:
        trimmed = chat_history[-8:]
        if self.provider == "openai":
            return self._call_openai(system_prompt, query, trimmed)
        elif self.provider == "anthropic":
            return self._call_anthropic(system_prompt, query, trimmed)
        else:
            return self._call_gemini(system_prompt, query, trimmed)

    def _call_openai(self, system_prompt, query, history):
        messages = [{"role": "system", "content": system_prompt}]
        for t in history:
            messages.append({"role": t["role"], "content": t["content"]})
        messages.append({"role": "user", "content": query})
        r = self._client.chat.completions.create(
            model=self.model_name, messages=messages,
            temperature=self.temperature, max_tokens=800)
        return r.choices[0].message.content

    def _call_anthropic(self, system_prompt, query, history):
        messages = [{"role": t["role"], "content": t["content"]} for t in history]
        messages.append({"role": "user", "content": query})
        r = self._client.messages.create(
            model=self.model_name, system=system_prompt,
            messages=messages, temperature=self.temperature, max_tokens=800)
        return "".join(b.text for b in r.content if hasattr(b, "text"))

    def _call_gemini(self, system_prompt, query, history):
        api_key = self._client["api_key"]

        history_text = ""
        for t in history[-4:]:
            role = "Customer" if t["role"] == "user" else "Assistant"
            history_text += f"{role}: {t['content']}\n"

        full_prompt = f"{system_prompt}\n\n{history_text}Customer: {query}\nAssistant:"

        url = url = f"https://generativelanguage.googleapis.com/v1/models/{self.model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": 800,
            }
        }

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code != 200:
            raise LLMProviderError(f"Gemini API error {response.status_code}: {response.text}")

        result = response.json()
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise LLMProviderError(f"Unexpected Gemini response: {result}") from e