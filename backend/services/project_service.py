import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from backend.services.project_saver import OUTPUT_DIR


class ProjectNotFoundError(Exception):
    pass


class ProjectMetadataError(Exception):
    pass


class ProjectVoiceNotFoundError(Exception):
    pass


class ProjectVideoNotFoundError(Exception):
    pass


def list_projects() -> list[dict[str, str]]:
    projects = [
        _project_summary(project_path, _read_metadata(project_path))
        for project_path in _project_paths()
    ]

    return [project for _, project in sorted(projects, reverse=True, key=lambda item: item[0])]


def get_project(project_id: str) -> dict[str, object]:
    for project_path in _project_paths():
        _, summary = _project_summary(project_path, _read_metadata(project_path))

        if summary["id"] == project_id:
            project = _read_project_data(project_path)
            _validate_project_data(project)

            return {
                "id": summary["id"],
                "topic": _metadata_text(project.get("topic"), summary["topic"]),
                "created": summary["created"],
                "last_modified": summary["last_modified"],
                "generator_version": _metadata_text(
                    project.get("generator_version"),
                    "legacy",
                ),
                "titles": project.get("titles", []),
                "script": project.get("script", ""),
                "description": project.get("description", ""),
                "tags": project.get("tags", []),
                "research": project.get("research", ""),
                "research_summary": project.get("research_summary", ""),
                "outline": project.get("outline", ""),
                "thumbnail_prompt": project.get("thumbnail_prompt", ""),
                "voice": project.get("voice"),
                "video": project.get("video"),
                "youtube": project.get("youtube"),
            }

    raise ProjectNotFoundError("Project not found.")


def get_project_directory(project_id: str) -> Path:
    for project_path in _project_paths():
        _, summary = _project_summary(project_path, _read_metadata(project_path))
        if summary["id"] == project_id:
            return project_path

    raise ProjectNotFoundError("Project not found.")


def get_voice_path(project_id: str) -> Path:
    project = get_project(project_id)
    voice = project.get("voice")
    if not isinstance(voice, dict) or voice.get("path") != "voice.wav":
        raise ProjectVoiceNotFoundError("Project narration is not available.")

    voice_path = get_project_directory(project_id) / "voice.wav"
    if not voice_path.is_file():
        raise ProjectVoiceNotFoundError("Project narration is not available.")

    return voice_path


def save_voice_metadata(project_id: str, voice: dict[str, object]) -> None:
    _save_media_metadata(project_id, "voice", voice)


def get_video_path(project_id: str) -> Path:
    project = get_project(project_id)
    video = project.get("video")
    if not isinstance(video, dict) or video.get("path") != "video.mp4":
        raise ProjectVideoNotFoundError("Project video is not available.")

    video_path = get_project_directory(project_id) / "video.mp4"
    if not video_path.is_file():
        raise ProjectVideoNotFoundError("Project video is not available.")

    return video_path


def save_video_metadata(project_id: str, video: dict[str, object]) -> None:
    _save_media_metadata(project_id, "video", video)


def save_youtube_metadata(project_id: str, youtube: dict[str, object]) -> None:
    _save_media_metadata(project_id, "youtube", youtube)


def save_youtube_upload_artifact(project_id: str, upload: dict[str, object]) -> None:
    """Persist the creator-safe YouTube upload receipt beside project artifacts."""
    project_path = get_project_directory(project_id)
    with (project_path / "youtube_upload.json").open("w", encoding="utf-8") as upload_file:
        json.dump(upload, upload_file, indent=2, ensure_ascii=False)


def _save_media_metadata(
    project_id: str,
    field: str,
    metadata: dict[str, object],
) -> None:
    project_path = get_project_directory(project_id)
    project = _read_project_data(project_path)
    _validate_project_data(project)
    project[field] = metadata
    project["last_modified"] = datetime.now(timezone.utc).isoformat().replace(
        "+00:00",
        "Z",
    )

    with (project_path / "project.json").open("w", encoding="utf-8") as project_file:
        json.dump(project, project_file, indent=4, ensure_ascii=False)


def _project_paths() -> list[Path]:
    output_path = Path(OUTPUT_DIR)

    if not output_path.is_dir():
        return []

    return [path for path in output_path.iterdir() if path.is_dir()]


def _project_summary(
    project_path: Path,
    metadata: dict[str, object],
) -> tuple[datetime, dict[str, str]]:
    fallback_time = _fallback_timestamp(project_path)
    created, created_time = _metadata_timestamp(
        metadata.get("created"),
        fallback_time,
    )
    last_modified, _ = _metadata_timestamp(
        metadata.get("last_modified"),
        fallback_time,
    )
    topic = _metadata_text(
        metadata.get("topic"),
        project_path.name.replace("_", " "),
    )

    return created_time, {
        "id": _metadata_text(
            metadata.get("id"),
            str(uuid5(NAMESPACE_URL, project_path.as_posix())),
        ),
        "name": _metadata_text(metadata.get("name"), topic),
        "topic": topic,
        "created": created,
        "last_modified": last_modified,
        "path": project_path.as_posix(),
    }


def _read_metadata(project_path: Path) -> dict[str, object]:
    try:
        with (project_path / "project.json").open(encoding="utf-8") as project_file:
            metadata = json.load(project_file)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}

    return metadata if isinstance(metadata, dict) else {}


def _read_project_data(project_path: Path) -> dict[str, object]:
    try:
        with (project_path / "project.json").open(encoding="utf-8") as project_file:
            project = json.load(project_file)
    except FileNotFoundError as error:
        raise ProjectMetadataError("Project data is missing.") from error
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProjectMetadataError("Project metadata is malformed.") from error

    if not isinstance(project, dict):
        raise ProjectMetadataError("Project metadata must be a JSON object.")

    return project


def _validate_project_data(project: dict[str, object]) -> None:
    for field in ("id", "topic", "created", "last_modified", "generator_version"):
        if field in project and not isinstance(project[field], str):
            raise ProjectMetadataError(f"Project metadata field '{field}' is invalid.")

    for field in ("created", "last_modified"):
        if field in project and isinstance(project[field], str):
            try:
                datetime.fromisoformat(project[field].replace("Z", "+00:00"))
            except ValueError as error:
                raise ProjectMetadataError(
                    f"Project metadata field '{field}' is invalid."
                ) from error

    for field in ("titles", "tags"):
        if field in project and (
            not isinstance(project[field], list)
            or not all(isinstance(item, str) for item in project[field])
        ):
            raise ProjectMetadataError(f"Project field '{field}' is invalid.")

    for field in (
        "script",
        "description",
        "research",
        "research_summary",
        "outline",
        "thumbnail_prompt",
    ):
        if field in project and not isinstance(project[field], str):
            raise ProjectMetadataError(f"Project field '{field}' is invalid.")

    voice = project.get("voice")
    if voice is not None:
        if not isinstance(voice, dict):
            raise ProjectMetadataError("Project voice metadata is invalid.")
        if voice.get("path") != "voice.wav":
            raise ProjectMetadataError("Project voice path is invalid.")
        if not isinstance(voice.get("provider"), str):
            raise ProjectMetadataError("Project voice provider is invalid.")
        if not isinstance(voice.get("sample_rate"), int):
            raise ProjectMetadataError("Project voice sample rate is invalid.")
        duration = voice.get("duration_seconds")
        if duration is not None and not isinstance(duration, (int, float)):
            raise ProjectMetadataError("Project voice duration is invalid.")

    video = project.get("video")
    if video is not None:
        if not isinstance(video, dict):
            raise ProjectMetadataError("Project video metadata is invalid.")
        if video.get("path") != "video.mp4":
            raise ProjectMetadataError("Project video path is invalid.")
        if video.get("visual_mode") not in {"user_images", "ai_images", "mixed"}:
            raise ProjectMetadataError("Project video visual mode is invalid.")
        for field in ("width", "height", "fps", "image_count"):
            if not isinstance(video.get(field), int):
                raise ProjectMetadataError(f"Project video field '{field}' is invalid.")
        for field in ("video_codec", "audio_codec"):
            if not isinstance(video.get(field), str):
                raise ProjectMetadataError(f"Project video field '{field}' is invalid.")
        duration = video.get("duration_seconds")
        if not isinstance(duration, (int, float)):
            raise ProjectMetadataError("Project video duration is invalid.")

    youtube = project.get("youtube")
    if youtube is not None:
        if not isinstance(youtube, dict):
            raise ProjectMetadataError("Project YouTube metadata is invalid.")
        for field in (
            "video_id",
            "video_url",
            "upload_status",
            "processing_status",
            "privacy_status",
            "title",
            "description",
            "thumbnail_prompt",
            "category_id",
        ):
            if not isinstance(youtube.get(field), str):
                raise ProjectMetadataError(
                    f"Project YouTube field '{field}' is invalid."
                )
        if youtube.get("privacy_status") != "private":
            raise ProjectMetadataError("Project YouTube privacy status is invalid.")
        tags = youtube.get("tags")
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise ProjectMetadataError("Project YouTube tags are invalid.")


def _fallback_timestamp(project_path: Path) -> datetime:
    try:
        return datetime.fromtimestamp(project_path.stat().st_mtime, timezone.utc)
    except OSError:
        return datetime.fromtimestamp(0, timezone.utc)


def _metadata_timestamp(value: object, fallback: datetime) -> tuple[str, datetime]:
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return value, parsed
        except ValueError:
            pass

    fallback_value = fallback.isoformat().replace("+00:00", "Z")
    return fallback_value, fallback


def _metadata_text(value: object, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback
