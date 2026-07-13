import requests
import os
import json

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

for model in ["models/text-embedding-004", "models/embedding-001"]:
    url = f"https://generativelanguage.googleapis.com/v1beta/{model}:batchEmbedContents?key={api_key}"
    payload = {
        "requests": [
            {
                "model": model,
                "content": {"parts": [{"text": "Hello world"}]}
            }
        ]
    }
    res = requests.post(url, json=payload)
    print(f"Model: {model}")
    print(f"Status: {res.status_code}")
    print(res.text[:300])
    print("-" * 50)
