import json
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from backend.services import project_service


class ProjectVoiceTests(unittest.TestCase):
    def test_voice_metadata_is_persisted_and_reopened(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            project_directory = output_directory / "project"
            project_directory.mkdir()
            project_data = {
                "id": "project-1",
                "topic": "Voice test",
                "created": "2026-07-14T00:00:00Z",
                "last_modified": "2026-07-14T00:00:00Z",
                "generator_version": "0.6.0",
                "titles": [],
                "script": "Script",
                "description": "",
                "tags": [],
                "research": "",
                "research_summary": "",
                "outline": "",
                "thumbnail_prompt": "",
            }
            (project_directory / "project.json").write_text(
                json.dumps(project_data),
                encoding="utf-8",
            )
            with wave.open(str(project_directory / "voice.wav"), "wb") as audio_file:
                audio_file.setnchannels(1)
                audio_file.setsampwidth(2)
                audio_file.setframerate(8000)
                audio_file.writeframes(b"\x00\x00")

            voice = {
                "path": "voice.wav",
                "provider": "fake",
                "sample_rate": 8000,
                "duration_seconds": 0.0,
            }
            with patch.object(project_service, "OUTPUT_DIR", str(output_directory)):
                project_service.save_voice_metadata("project-1", voice)
                reopened_project = project_service.get_project("project-1")
                voice_path = project_service.get_voice_path("project-1")

            self.assertEqual(reopened_project["voice"], voice)
            self.assertEqual(voice_path.name, "voice.wav")

    def test_legacy_project_has_no_voice_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            project_directory = output_directory / "legacy"
            project_directory.mkdir()
            (project_directory / "project.json").write_text(
                json.dumps({"id": "legacy", "topic": "Legacy"}),
                encoding="utf-8",
            )

            with patch.object(project_service, "OUTPUT_DIR", str(output_directory)):
                project = project_service.get_project("legacy")

            self.assertIsNone(project["voice"])

    def test_video_metadata_is_persisted_and_reopened(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            project_directory = output_directory / "project"
            project_directory.mkdir()
            project_data = {
                "id": "project-1",
                "topic": "Video test",
                "created": "2026-07-14T00:00:00Z",
                "last_modified": "2026-07-14T00:00:00Z",
                "generator_version": "0.6.0",
            }
            (project_directory / "project.json").write_text(
                json.dumps(project_data),
                encoding="utf-8",
            )
            (project_directory / "video.mp4").write_bytes(b"mp4")
            video = {
                "path": "video.mp4",
                "visual_mode": "user_images",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "video_codec": "h264",
                "audio_codec": "aac",
                "duration_seconds": 1.0,
                "image_count": 1,
            }

            with patch.object(project_service, "OUTPUT_DIR", str(output_directory)):
                project_service.save_video_metadata("project-1", video)
                reopened_project = project_service.get_project("project-1")
                video_path = project_service.get_video_path("project-1")

            self.assertEqual(reopened_project["video"], video)
            self.assertEqual(video_path.name, "video.mp4")

    def test_youtube_metadata_is_persisted_and_reopened(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            project_directory = output_directory / "project"
            project_directory.mkdir()
            project_data = {
                "id": "project-1",
                "topic": "Upload test",
                "created": "2026-07-14T00:00:00Z",
                "last_modified": "2026-07-14T00:00:00Z",
                "generator_version": "0.6.0",
            }
            (project_directory / "project.json").write_text(
                json.dumps(project_data),
                encoding="utf-8",
            )
            youtube = {
                "video_id": "youtube-video-1",
                "video_url": "https://www.youtube.com/watch?v=youtube-video-1",
                "upload_status": "uploaded",
                "processing_status": "processing",
                "privacy_status": "private",
                "title": "Upload test",
                "description": "Description",
                "tags": ["tag"],
                "thumbnail_prompt": "Thumbnail",
                "category_id": "22",
            }

            with patch.object(project_service, "OUTPUT_DIR", str(output_directory)):
                project_service.save_youtube_metadata("project-1", youtube)
                reopened_project = project_service.get_project("project-1")

            self.assertEqual(reopened_project["youtube"], youtube)


if __name__ == "__main__":
    unittest.main()
