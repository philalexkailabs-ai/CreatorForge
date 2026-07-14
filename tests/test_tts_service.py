import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from backend.services import tts_service


class FakeNarrationProvider:
    name = "fake"

    def synthesize(self, script: str, output_path: Path) -> None:
        with wave.open(str(output_path), "wb") as audio_file:
            audio_file.setnchannels(1)
            audio_file.setsampwidth(2)
            audio_file.setframerate(8000)
            audio_file.writeframes(b"\x00\x00" * 8000)


class TTSServiceTests(unittest.TestCase):
    def test_generate_voice_creates_wav_and_persists_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            with (
                patch.object(
                    tts_service,
                    "get_saved_project",
                    return_value={"script": "A creator-ready script."},
                ),
                patch.object(
                    tts_service,
                    "get_project_directory",
                    return_value=project_directory,
                ),
                patch.object(
                    tts_service,
                    "_get_provider",
                    return_value=FakeNarrationProvider(),
                ),
                patch.object(tts_service, "save_voice_metadata") as save_metadata,
            ):
                metadata = tts_service.generate_voice("project-1")

            self.assertTrue((project_directory / "voice.wav").is_file())
            self.assertEqual(metadata["provider"], "fake")
            self.assertEqual(metadata["sample_rate"], 8000)
            self.assertEqual(metadata["duration_seconds"], 1.0)
            save_metadata.assert_called_once_with("project-1", metadata)

    def test_generate_voice_rejects_projects_without_scripts(self) -> None:
        with patch.object(
            tts_service,
            "get_saved_project",
            return_value={"script": ""},
        ):
            with self.assertRaises(tts_service.TTSServiceError):
                tts_service.generate_voice("project-1")


if __name__ == "__main__":
    unittest.main()
