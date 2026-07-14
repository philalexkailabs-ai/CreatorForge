import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from backend.services import video_service


class VideoServiceTests(unittest.TestCase):
    def test_render_project_video_creates_mp4_and_persists_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            images_directory = project_directory / "images"
            images_directory.mkdir()
            (images_directory / "01.png").write_bytes(b"image")
            (images_directory / "02.jpg").write_bytes(b"image")
            voice_path = project_directory / "voice.wav"
            with wave.open(str(voice_path), "wb") as audio_file:
                audio_file.setnchannels(1)
                audio_file.setsampwidth(2)
                audio_file.setframerate(8000)
                audio_file.writeframes(b"\x00\x00" * 16000)

            def fake_ffmpeg(command: list[str]) -> None:
                Path(command[-1]).write_bytes(b"mp4")

            with (
                patch.object(
                    video_service,
                    "get_saved_project",
                    return_value={"id": "project-1"},
                ),
                patch.object(
                    video_service,
                    "get_project_directory",
                    return_value=project_directory,
                ),
                patch.object(
                    video_service,
                    "get_voice_path",
                    return_value=voice_path,
                ),
                patch.object(video_service, "_run_ffmpeg", side_effect=fake_ffmpeg) as run_ffmpeg,
                patch.object(video_service, "save_video_metadata") as save_metadata,
            ):
                metadata = video_service.render_project_video("project-1")

            self.assertTrue((project_directory / "video.mp4").is_file())
            self.assertEqual(metadata["visual_mode"], "user_images")
            self.assertEqual(metadata["width"], 1920)
            self.assertEqual(metadata["height"], 1080)
            self.assertEqual(metadata["fps"], 30)
            self.assertEqual(metadata["duration_seconds"], 2.0)
            self.assertEqual(metadata["image_count"], 2)
            save_metadata.assert_called_once_with("project-1", metadata)
            command = run_ffmpeg.call_args.args[0]
            self.assertIn("libx264", command)
            self.assertIn("aac", command)
            self.assertIn("-shortest", command)
            self.assertFalse(list(project_directory.glob("*.ffconcat")))

    def test_render_project_video_requires_user_images(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            with (
                patch.object(
                    video_service,
                    "get_saved_project",
                    return_value={"id": "project-1"},
                ),
                patch.object(
                    video_service,
                    "get_project_directory",
                    return_value=project_directory,
                ),
                patch.object(video_service, "get_voice_path"),
            ):
                with self.assertRaises(video_service.VideoServiceError):
                    video_service.render_project_video("project-1")


if __name__ == "__main__":
    unittest.main()
