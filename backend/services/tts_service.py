from __future__ import annotations

import os
import wave
from pathlib import Path
from typing import Protocol

from backend.services.project_service import (
    get_project as get_saved_project,
    get_project_directory,
    save_voice_metadata,
)


VOICE_FILENAME = "voice.wav"
KOKORO_SAMPLE_RATE = 24000


class TTSServiceError(RuntimeError):
    pass


class TTSProviderUnavailableError(TTSServiceError):
    pass


class NarrationProvider(Protocol):
    name: str

    def synthesize(self, script: str, output_path: Path) -> None:
        """Write one WAV narration for the supplied script."""


class KokoroProvider:
    name = "kokoro"

    def synthesize(self, script: str, output_path: Path) -> None:
        try:
            import numpy as np
            import soundfile as sound_file
            from kokoro import KPipeline
        except ImportError as error:
            raise TTSProviderUnavailableError(
                "Kokoro narration is unavailable. Install the local TTS "
                "dependencies and espeak-ng, then try again."
            ) from error

        pipeline = KPipeline(lang_code="a")
        audio_chunks = [
            audio
            for _, _, audio in pipeline(script, voice="af_heart", speed=1)
        ]
        if not audio_chunks:
            raise TTSServiceError("Kokoro did not produce narration audio.")

        sound_file.write(
            output_path,
            np.concatenate(audio_chunks),
            KOKORO_SAMPLE_RATE,
        )


def generate_voice(project_id: str) -> dict[str, object]:
    """Generate and persist local narration for an existing project script."""
    project = get_saved_project(project_id)
    script = project.get("script")
    if not isinstance(script, str) or not script.strip():
        raise TTSServiceError("Project script is required before narration.")

    output_path = get_project_directory(project_id) / VOICE_FILENAME
    provider = _get_provider()
    provider.synthesize(script, output_path)

    metadata = _read_voice_metadata(output_path, provider.name)
    save_voice_metadata(project_id, metadata)
    return metadata


def _get_provider() -> NarrationProvider:
    provider_name = os.getenv("CREATORFORGE_TTS_PROVIDER", "kokoro").casefold()
    if provider_name == "kokoro":
        return KokoroProvider()

    raise TTSProviderUnavailableError(
        f"Unsupported local TTS provider: {provider_name}."
    )


def _read_voice_metadata(
    output_path: Path,
    provider_name: str,
) -> dict[str, object]:
    if not output_path.is_file():
        raise TTSServiceError("The narration provider did not create voice.wav.")

    try:
        with wave.open(str(output_path), "rb") as audio_file:
            sample_rate = audio_file.getframerate()
            frame_count = audio_file.getnframes()
    except wave.Error as error:
        raise TTSServiceError("The narration provider created an invalid WAV file.") from error

    return {
        "path": VOICE_FILENAME,
        "provider": provider_name,
        "sample_rate": sample_rate,
        "duration_seconds": round(frame_count / sample_rate, 3)
        if sample_rate
        else None,
    }
