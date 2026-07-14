import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.services import diagnostics_service, settings_service


class OperationsServiceTests(unittest.TestCase):
    def test_settings_round_trip_validates_theme(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch.object(settings_service, "SETTINGS_PATH", Path(temporary_directory) / "settings.json"):
                saved = settings_service.save_settings({"theme": "light", "ffmpeg_path": "custom-ffmpeg"})
                self.assertEqual(saved["theme"], "light")
                self.assertEqual(settings_service.get_settings()["ffmpeg_path"], "custom-ffmpeg")
                with self.assertRaises(ValueError):
                    settings_service.save_settings({"theme": "invalid"})

    def test_diagnostics_returns_all_required_checks(self) -> None:
        with patch.object(diagnostics_service, "get_settings", return_value={
            "ollama_url": "http://localhost:11434", "comfyui_url": "http://localhost:8188",
            "ffmpeg_path": "missing", "youtube_client_secrets": "", "tts_provider": "kokoro",
            "default_model": "model", "workflow_template": "sdxl_turbo.json", "theme": "dark",
        }):
            result = diagnostics_service.get_diagnostics()
        self.assertEqual(set(result), {"ollama", "comfyui", "ffmpeg", "kokoro", "cuda", "youtube_credentials"})
        self.assertIn(result["ollama"]["status"], {"green", "yellow", "red"})
