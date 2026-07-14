import unittest
from pathlib import Path


class VoiceFrontendTests(unittest.TestCase):
    def test_play_voice_button_and_endpoint_wiring_exist(self) -> None:
        root = Path(__file__).resolve().parents[1]
        html = (root / "frontend" / "index.html").read_text(encoding="utf-8")
        javascript = (root / "frontend" / "js" / "app.js").read_text(
            encoding="utf-8"
        )

        self.assertIn('id="play-voice"', html)
        self.assertIn("function playVoice()", javascript)
        self.assertIn("/projects/${encodeURIComponent(projectId)}/voice", javascript)
        self.assertIn("narration.play()", javascript)


if __name__ == "__main__":
    unittest.main()
