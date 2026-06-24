"""
multilingual.py
================
Provides language detection so the chatbot can identify the language of an
incoming user query and instruct the LLM to respond in the same language.

Uses ``langdetect`` (a lightweight, offline-capable library) rather than a
paid API, keeping multilingual support fast and free for a demo
deployment. English, Tamil and Hindi are explicitly supported as
first-class languages per the project requirements, with graceful fallback
for any other language ``langdetect`` recognizes.
"""

from typing import Optional

from langdetect import DetectorFactory, LangDetectException, detect

from src.utils import get_logger

logger = get_logger(__name__)

# Make language detection deterministic across runs (langdetect uses a
# probabilistic algorithm seeded randomly by default).
DetectorFactory.seed = 0

# Human-readable names for common language codes, prioritizing the
# languages explicitly required by the project plus other major languages.
LANGUAGE_NAMES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "ur": "Urdu",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh-cn": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "ru": "Russian",
    "pt": "Portuguese",
    "it": "Italian",
}

DEFAULT_LANGUAGE_CODE = "en"


class LanguageDetector:
    """
    Detects the language of user input text and exposes helpers for
    building language-aware LLM instructions.
    """

    def detect_language(self, text: str) -> str:
        """
        Detect the ISO 639-1 language code of the given text.

        Args:
            text: Input text (typically a user query).

        Returns:
            ISO language code (e.g. ``"en"``, ``"ta"``, ``"hi"``). Falls
            back to ``DEFAULT_LANGUAGE_CODE`` if detection fails or the
            text is too short to reliably classify.
        """
        if not text or len(text.strip()) < 2:
            return DEFAULT_LANGUAGE_CODE

        try:
            code = detect(text)
            return code
        except LangDetectException:
            logger.warning("Language detection failed; defaulting to English.")
            return DEFAULT_LANGUAGE_CODE

    def get_language_name(self, language_code: str) -> str:
        """
        Convert a language code into a human-readable name.

        Args:
            language_code: ISO language code.

        Returns:
            Human-readable language name, or the code itself if unknown.
        """
        return LANGUAGE_NAMES.get(language_code, language_code)

    def detect_with_name(self, text: str) -> tuple:
        """
        Detect language and return both the code and human-readable name.

        Args:
            text: Input text to analyze.

        Returns:
            Tuple of ``(language_code, language_name)``.
        """
        code = self.detect_language(text)
        name = self.get_language_name(code)
        return code, name

    def build_language_instruction(self, language_code: str) -> str:
        """
        Build a natural-language instruction for the LLM directing it to
        respond in the detected language.

        Args:
            language_code: ISO language code detected from the user query.

        Returns:
            Instruction string to append to the system prompt.
        """
        language_name = self.get_language_name(language_code)
        if language_code == DEFAULT_LANGUAGE_CODE:
            return "Respond in English."
        return (
            f"The user's message is written in {language_name}. "
            f"You MUST respond entirely in {language_name}, using natural, "
            f"fluent, native-quality phrasing. Do not mix in English unless "
            f"the user used an English technical term with no equivalent."
        )
