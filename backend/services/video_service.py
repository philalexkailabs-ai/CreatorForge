from __future__ import annotations

import os
import subprocess
import tempfile
import wave
from pathlib import Path

from backend.services.project_service import (
    get_project as get_saved_project,
    get_project_directory,
    get_voice_path,
    save_video_metadata,
)


VIDEO_FILENAME = "video.mp4"
IMAGE_DIRECTORY_NAME = "images"
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
IMAGE_EXTENSIONS = {".jpeg", ".jpg", ".png", ".webp"}


class VideoServiceError(RuntimeError):
    pass


class FFmpegUnavailableError(VideoServiceError):
    pass


def render_project_video(project_id: str) -> dict[str, object]:
    """Render user-supplied project images and narration into an MP4."""
    get_saved_project(project_id)
    project_directory = get_project_directory(project_id)
    voice_path = get_voice_path(project_id)
    image_paths = _get_user_images(project_directory / IMAGE_DIRECTORY_NAME)
    duration_seconds = _wav_duration(voice_path)
    output_path = project_directory / VIDEO_FILENAME
    manifest_path = _write_concat_manifest(project_directory, image_paths, duration_seconds)

    try:
        command = build_ffmpeg_command(manifest_path, voice_path, output_path)
        _run_ffmpeg(command)
    finally:
        manifest_path.unlink(missing_ok=True)

    if not output_path.is_file():
        raise VideoServiceError("FFmpeg did not create video.mp4.")

    metadata = {
        "path": VIDEO_FILENAME,
        "visual_mode": "user_images",
        "width": VIDEO_WIDTH,
        "height": VIDEO_HEIGHT,
        "fps": VIDEO_FPS,
        "video_codec": "h264",
        "audio_codec": "aac",
        "duration_seconds": duration_seconds,
        "image_count": len(image_paths),
    }
    save_video_metadata(project_id, metadata)
    return metadata


def build_ffmpeg_command(
    manifest_path: Path,
    voice_path: Path,
    output_path: Path,
) -> list[str]:
    return [
        os.getenv("CREATORFORGE_FFMPEG_BIN", "ffmpeg"),
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(manifest_path),
        "-i",
        str(voice_path),
        "-filter_complex",
        (
            "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v]"
        ),
        "-map",
        "[v]",
        "-map",
        "1:a",
        "-r",
        str(VIDEO_FPS),
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-shortest",
        "-movflags",
        "+faststart",
        str(output_path),
    ]


def _get_user_images(images_directory: Path) -> list[Path]:
    if not images_directory.is_dir():
        raise VideoServiceError(
            "Project images are required. Copy JPG, PNG, or WebP files into "
            f"{IMAGE_DIRECTORY_NAME}/ before generating video."
        )

    image_paths = sorted(
        path for path in images_directory.iterdir()
        if path.is_file() and path.suffix.casefold() in IMAGE_EXTENSIONS
    )
    if not image_paths:
        raise VideoServiceError(
            "Project images are required. Copy JPG, PNG, or WebP files into "
            f"{IMAGE_DIRECTORY_NAME}/ before generating video."
        )

    return image_paths


def _wav_duration(voice_path: Path) -> float:
    try:
        with wave.open(str(voice_path), "rb") as audio_file:
            sample_rate = audio_file.getframerate()
            if sample_rate <= 0:
                raise VideoServiceError("Project narration has an invalid sample rate.")
            return round(audio_file.getnframes() / sample_rate, 3)
    except wave.Error as error:
        raise VideoServiceError("Project narration must be a valid WAV file.") from error


def _write_concat_manifest(
    project_directory: Path,
    image_paths: list[Path],
    duration_seconds: float,
) -> Path:
    image_duration = max(duration_seconds / len(image_paths), 0.1)
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".ffconcat",
        prefix="creatorforge-video-",
        dir=project_directory,
        encoding="utf-8",
        delete=False,
    ) as manifest:
        for image_path in image_paths:
            manifest.write(f"file '{_ffconcat_path(image_path)}'\n")
            manifest.write(f"duration {image_duration:.3f}\n")
        manifest.write(f"file '{_ffconcat_path(image_paths[-1])}'\n")
        return Path(manifest.name)


def _ffconcat_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", r"'\\''")


def _run_ffmpeg(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as error:
        raise FFmpegUnavailableError(
            "FFmpeg is unavailable. Install FFmpeg and add it to PATH."
        ) from error
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() or "Unknown FFmpeg failure."
        raise VideoServiceError(f"FFmpeg could not render the video: {details}") from error
