OLLAMA_URL = "http://localhost:11434/api/generate"

# ComfyUI is optional and is only contacted by the AI image generation route.
COMFYUI_URL = "http://127.0.0.1:8188"

DEFAULT_MODEL = "qwen3:8b"

SUPPORTED_MODELS = (
    DEFAULT_MODEL,
    "gemma3:4b",
    "qwen2.5-coder:14b",
)
