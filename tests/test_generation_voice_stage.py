import unittest
from unittest.mock import patch

from backend import main


class GenerationVoiceStageTests(unittest.TestCase):
    def test_project_generation_runs_voice_after_script_without_ollama(self) -> None:
        saved_project = {
            "id": "project-1",
            "created": "2026-07-14T00:00:00Z",
        }
        voice = {
            "path": "voice.wav",
            "provider": "fake",
            "sample_rate": 8000,
            "duration_seconds": 1.0,
        }
        with (
            patch.object(main, "generate_research_content", return_value="Research"),
            patch.object(main, "generate_research_summary_content", return_value="Summary"),
            patch.object(main, "generate_outline_content", return_value="Outline"),
            patch.object(
                main,
                "generate_titles_content",
                return_value=[f"Title {index}" for index in range(10)],
            ),
            patch.object(main, "generate_script_content", return_value="word " * 100),
            patch.object(main, "generate_description_content", return_value="Description"),
            patch.object(
                main,
                "generate_tags_content",
                return_value=[f"tag-{index}" for index in range(20)],
            ),
            patch.object(main, "generate_thumbnail_content", return_value="Thumbnail"),
            patch.object(main, "save_project", side_effect=[saved_project, saved_project]) as save_project,
            patch.object(main, "generate_voice", return_value=voice) as generate_voice,
        ):
            result = main.generate_project(main.TopicRequest(topic="Voice test"))

        self.assertEqual(result["script"], "word " * 100)
        self.assertEqual(save_project.call_count, 2)
        generate_voice.assert_called_once_with("project-1")

    def test_full_pipeline_records_media_failure_without_losing_project(self) -> None:
        saved_project = {"id": "project-1", "created": "2026-07-14T00:00:00Z"}
        with (
            patch.object(main, "generate_research_content", return_value="Research"),
            patch.object(main, "generate_research_summary_content", return_value="Summary"),
            patch.object(main, "generate_outline_content", return_value="Outline"),
            patch.object(main, "generate_titles_content", return_value=["Title"]),
            patch.object(main, "generate_script_content", return_value="Script"),
            patch.object(main, "generate_description_content", return_value="Description"),
            patch.object(main, "generate_tags_content", return_value=["tag"]),
            patch.object(main, "generate_thumbnail_content", return_value="Thumbnail"),
            patch.object(main, "save_project", side_effect=[saved_project, saved_project]),
            patch.object(main, "generate_voice", return_value={}),
            patch.object(main, "generate_project_images", side_effect=main.ImageServiceError("ComfyUI unavailable")),
            patch.object(main, "render_project_video") as video,
            patch.object(main, "upload_project_video") as upload,
        ):
            result = main.generate_project(main.TopicRequest(topic="Test", full_pipeline=True))
        self.assertIn("ComfyUI unavailable", result["pipeline"]["images"])
        video.assert_called_once()
        upload.assert_called_once()


if __name__ == "__main__":
    unittest.main()
