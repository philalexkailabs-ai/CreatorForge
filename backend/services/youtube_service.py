from __future__ import annotations

import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.services.project_service import (
    get_project as get_saved_project,
    get_video_path,
    save_youtube_metadata,
    save_youtube_upload_artifact,
)


YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
PRIVATE_PRIVACY_STATUS = "private"
DEFAULT_CATEGORY_ID = "22"
DEFAULT_CLIENT_SECRETS_PATH = Path("local_config/youtube-client-secret.json")
DEFAULT_TOKEN_PATH = Path("local_config/youtube-token.json")
logger = logging.getLogger(__name__)


class YouTubeServiceError(RuntimeError):
    pass


def upload_project_video(project_id: str) -> dict[str, object]:
    """Upload an existing project video after an explicit creator action."""
    logger.info("Starting creator-approved YouTube upload project_id=%s", project_id)
    project = get_saved_project(project_id)
    video_path = get_video_path(project_id)
    upload_metadata = _build_upload_metadata(project)
    youtube = _get_authenticated_youtube()

    response = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": upload_metadata["title"],
                "description": upload_metadata["description"],
                "tags": upload_metadata["tags"],
                "categoryId": upload_metadata["category_id"],
            },
            "status": {"privacyStatus": PRIVATE_PRIVACY_STATUS},
        },
        media_body=_build_media_upload(video_path),
    ).execute(num_retries=3)

    video_id = response.get("id") if isinstance(response, dict) else None
    if not isinstance(video_id, str) or not video_id:
        raise YouTubeServiceError("YouTube did not return an uploaded video ID.")

    metadata = {
        "video_id": video_id,
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
        "upload_status": "uploaded",
        "processing_status": _get_processing_status(youtube, video_id),
        "privacy_status": PRIVATE_PRIVACY_STATUS,
        "uploaded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        **upload_metadata,
    }
    save_youtube_metadata(project_id, metadata)
    save_youtube_upload_artifact(
        project_id,
        {
            "upload_timestamp": metadata["uploaded_at"],
            "privacy": PRIVATE_PRIVACY_STATUS,
            "video_id": metadata["video_id"],
            "url": metadata["video_url"],
            "processing_status": metadata["processing_status"],
        },
    )
    return metadata


def retry_upload_project_video(project_id: str) -> dict[str, object]:
    """Explicitly retry a failed or interrupted creator-approved upload."""
    return upload_project_video(project_id)


def _get_authenticated_youtube() -> Any:
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as error:
        raise YouTubeServiceError(
            "YouTube upload dependencies are unavailable. Install the project "
            "requirements and try again."
        ) from error

    client_secrets_path = _configured_path(
        "CREATORFORGE_YOUTUBE_CLIENT_SECRETS",
        DEFAULT_CLIENT_SECRETS_PATH,
    )
    token_path = _configured_path("CREATORFORGE_YOUTUBE_TOKEN", DEFAULT_TOKEN_PATH)
    if not client_secrets_path.is_file():
        raise YouTubeServiceError(
            "YouTube OAuth client secrets are missing. Configure "
            "CREATORFORGE_YOUTUBE_CLIENT_SECRETS with a local OAuth client file."
        )

    credentials = None
    if token_path.is_file():
        credentials = Credentials.from_authorized_user_file(
            str(token_path),
            [YOUTUBE_UPLOAD_SCOPE],
        )

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    elif not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secrets_path),
            [YOUTUBE_UPLOAD_SCOPE],
        )
        credentials = flow.run_local_server(port=0)

    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(credentials.to_json(), encoding="utf-8")
    try:
        token_path.chmod(0o600)
    except OSError:
        pass

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)


def _build_media_upload(video_path: Path) -> Any:
    try:
        from googleapiclient.http import MediaFileUpload
    except ImportError as error:
        raise YouTubeServiceError(
            "YouTube upload dependencies are unavailable. Install the project "
            "requirements and try again."
        ) from error

    return MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)


def _build_upload_metadata(project: dict[str, object]) -> dict[str, object]:
    titles = project.get("titles")
    title = titles[0].strip() if isinstance(titles, list) and titles else ""
    description = project.get("description")
    tags = project.get("tags")
    thumbnail_prompt = project.get("thumbnail_prompt")

    if not title:
        raise YouTubeServiceError("A project title is required before upload.")
    if not isinstance(description, str):
        raise YouTubeServiceError("A project description is required before upload.")
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise YouTubeServiceError("Project tags are required before upload.")

    return {
        "title": title,
        "description": description,
        "tags": tags,
        "thumbnail_prompt": thumbnail_prompt
        if isinstance(thumbnail_prompt, str)
        else "",
        "category_id": DEFAULT_CATEGORY_ID,
    }


def _get_processing_status(youtube: Any, video_id: str) -> str:
    response = youtube.videos().list(
        part="processingDetails",
        id=video_id,
    ).execute()
    if not isinstance(response, dict):
        return "processing"

    items = response.get("items")
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        return "processing"
    processing_details = items[0].get("processingDetails")
    if not isinstance(processing_details, dict):
        return "processing"
    status = processing_details.get("processingStatus")
    return status if isinstance(status, str) and status else "processing"


def _configured_path(environment_name: str, default_path: Path) -> Path:
    return Path(os.getenv(environment_name, str(default_path))).expanduser()
