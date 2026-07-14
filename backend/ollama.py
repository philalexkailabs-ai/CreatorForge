import os
import requests

from backend.config import DEFAULT_MODEL, OLLAMA_URL, SUPPORTED_MODELS


class UnsupportedModelError(ValueError):
    def __init__(self, model: str):
        self.model = model
        super().__init__(f"Unsupported model: {model}")


def ask_ollama(prompt: str, model: str | None = None) -> str:
    selected_model = model or DEFAULT_MODEL

    if selected_model not in SUPPORTED_MODELS:
        raise UnsupportedModelError(selected_model)

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        os.getenv("CREATORFORGE_OLLAMA_URL", OLLAMA_URL),
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["response"]
