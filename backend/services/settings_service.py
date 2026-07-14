"""Local, non-secret CreatorForge runtime preferences."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SETTINGS_PATH = Path("local_config/creatorforge-settings.json")
DEFAULTS: dict[str, object] = {
    "ollama_url": "http://localhost:11434/api/generate",
    "comfyui_url": "http://127.0.0.1:8188",
    "ffmpeg_path": "ffmpeg",
    "tts_provider": "kokoro",
    "default_model": "qwen3:8b",
    "workflow_template": "sdxl_turbo.json",
    "theme": "dark",
    "youtube_client_secrets": "",
}


def get_settings() -> dict[str, object]:
    try:
        saved = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        saved = {}
    return {**DEFAULTS, **(saved if isinstance(saved, dict) else {})}


def save_settings(settings: dict[str, object]) -> dict[str, object]:
    unknown = set(settings) - set(DEFAULTS)
    if unknown:
        raise ValueError("Unsupported settings were supplied.")
    merged = {**get_settings(), **settings}
    if merged["theme"] not in {"dark", "light"}:
        raise ValueError("Theme must be dark or light.")
    if not isinstance(merged["default_model"], str) or not merged["default_model"].strip():
        raise ValueError("A default model is required.")
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    return merged
