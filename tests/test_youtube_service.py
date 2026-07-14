import unittest
from pathlib import Path
from unittest.mock import patch

from backend.services import youtube_service


class FakeRequest:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response

    def execute(self, **kwargs: object) -> dict[str, object]:
        return self.response


class FakeVideosResource:
    def __init__(self) -> None:
        self.insert_kwargs: dict[str, object] | None = None

    def insert(self, **kwargs: object) -> FakeRequest:
        self.insert_kwargs = kwargs
        return FakeRequest({"id": "youtube-video-1"})

    def list(self, **kwargs: object) -> FakeRequest:
        return FakeRequest(
            {"items": [{"processingDetails": {"processingStatus": "processing"}}]}
        )


class FakeYouTube:
    def __init__(self) -> None:
        self.videos_resource = FakeVideosResource()

    def videos(self) -> FakeVideosResource:
        return self.videos_resource


class YouTubeServiceTests(unittest.TestCase):
    def test_upload_maps_private_metadata_and_persists_result(self) -> None:
        project = {
            "titles": ["CreatorForge video title"],
            "description": "CreatorForge description",
            "tags": ["creatorforge", "local-ai"],
            "thumbnail_prompt": "Bright creator thumbnail",
        }
        fake_youtube = FakeYouTube()
        video_path = Path("C:/projects/video.mp4")
        media_upload = object()

        with (
            patch.object(
                youtube_service,
                "get_saved_project",
                return_value=project,
            ),
            patch.object(youtube_service, "get_video_path", return_value=video_path),
            patch.object(
                youtube_service,
                "_get_authenticated_youtube",
                return_value=fake_youtube,
            ) as authenticate,
            patch.object(
                youtube_service,
                "_build_media_upload",
                return_value=media_upload,
            ),
            patch.object(youtube_service, "save_youtube_metadata") as save_metadata,
            patch.object(youtube_service, "save_youtube_upload_artifact") as save_artifact,
        ):
            result = youtube_service.upload_project_video("project-1")

        authenticate.assert_called_once_with()
        self.assertEqual(result["video_id"], "youtube-video-1")
        self.assertEqual(result["privacy_status"], "private")
        self.assertEqual(result["processing_status"], "processing")
        self.assertEqual(result["category_id"], "22")
        self.assertEqual(result["thumbnail_prompt"], "Bright creator thumbnail")
        save_metadata.assert_called_once_with("project-1", result)
        upload_receipt = save_artifact.call_args.args[1]
        self.assertEqual(upload_receipt["privacy"], "private")
        self.assertEqual(upload_receipt["video_id"], "youtube-video-1")

        insert_kwargs = fake_youtube.videos_resource.insert_kwargs
        self.assertIsNotNone(insert_kwargs)
        self.assertEqual(insert_kwargs["part"], "snippet,status")
        self.assertEqual(insert_kwargs["media_body"], media_upload)
        self.assertEqual(insert_kwargs["body"]["status"]["privacyStatus"], "private")
        self.assertEqual(
            insert_kwargs["body"]["snippet"]["title"],
            "CreatorForge video title",
        )
        self.assertEqual(
            insert_kwargs["body"]["snippet"]["tags"],
            ["creatorforge", "local-ai"],
        )

    def test_missing_title_stops_before_oauth(self) -> None:
        with (
            patch.object(
                youtube_service,
                "get_saved_project",
                return_value={"titles": [], "description": "", "tags": []},
            ),
            patch.object(youtube_service, "get_video_path"),
            patch.object(youtube_service, "_get_authenticated_youtube") as authenticate,
        ):
            with self.assertRaises(youtube_service.YouTubeServiceError):
                youtube_service.upload_project_video("project-1")

        authenticate.assert_not_called()

    def test_retry_delegates_to_normal_explicit_upload(self) -> None:
        with patch.object(youtube_service, "upload_project_video", return_value={"video_id": "retry"}) as upload:
            result = youtube_service.retry_upload_project_video("project-1")
        self.assertEqual(result["video_id"], "retry")
        upload.assert_called_once_with("project-1")


if __name__ == "__main__":
    unittest.main()
