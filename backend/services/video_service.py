from __future__ import annotations

import json
import logging
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
SUBTITLE_FILENAME = "subtitles.srt"
IMAGE_DIRECTORY_NAME = "images"
BACKGROUND_MUSIC_BASENAME = "background_music"
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
IMAGE_EXTENSIONS = {".jpeg", ".jpg", ".png", ".webp"}
AUDIO_EXTENSIONS = {".aac", ".m4a", ".mp3", ".wav"}
logger = logging.getLogger(__name__)


class VideoServiceError(RuntimeError):
    pass


class FFmpegUnavailableError(VideoServiceError):
    pass


def render_project_video(
    project_id: str,
    *,
    visual_mode: str = "manual",
    image_duration_seconds: float | None = None,
    fade_transitions: bool = False,
    ken_burns: bool = False,
    subtitles: bool = False,
    background_music: bool = False,
) -> dict[str, object]:
    """Render project images and narration, with optional local enhancements."""
    _validate_options(visual_mode, image_duration_seconds)
    logger.info(
        "Rendering project video project_id=%s visual_mode=%s subtitles=%s music=%s",
        project_id,
        visual_mode,
        subtitles,
        background_music,
    )
    project = get_saved_project(project_id)
    project_directory = get_project_directory(project_id)
    voice_path = get_voice_path(project_id)
    image_paths = _get_project_images(project_directory / IMAGE_DIRECTORY_NAME, visual_mode)
    narration_duration = _wav_duration(voice_path)
    image_duration = image_duration_seconds or max(narration_duration / len(image_paths), 0.1)
    output_path = project_directory / VIDEO_FILENAME
    concat_manifest = _write_concat_manifest(project_directory, image_paths, image_duration)
    subtitle_path = _write_subtitles(project_directory, project, image_duration) if subtitles else None
    music_path = _get_background_music(project_directory) if background_music else None

    try:
        command = build_ffmpeg_command(
            concat_manifest,
            voice_path,
            output_path,
            fade_transitions=fade_transitions,
            ken_burns=ken_burns,
            subtitle_path=subtitle_path,
            music_path=music_path,
        )
        _run_ffmpeg(command)
    finally:
        concat_manifest.unlink(missing_ok=True)

    if not output_path.is_file():
        raise VideoServiceError("FFmpeg did not create video.mp4.")

    metadata = {
        "path": VIDEO_FILENAME,
        "visual_mode": {"manual": "user_images", "ai": "ai_images", "mixed": "mixed"}[visual_mode],
        "width": VIDEO_WIDTH,
        "height": VIDEO_HEIGHT,
        "fps": VIDEO_FPS,
        "video_codec": "h264",
        "audio_codec": "aac",
        "duration_seconds": narration_duration,
        "image_count": len(image_paths),
        "image_duration_seconds": round(image_duration, 3),
        "fade_transitions": fade_transitions,
        "ken_burns": ken_burns,
        "subtitles_path": SUBTITLE_FILENAME if subtitle_path else None,
        "background_music": bool(music_path),
    }
    save_video_metadata(project_id, metadata)
    return metadata


def build_ffmpeg_command(
    manifest_path: Path,
    voice_path: Path,
    output_path: Path,
    *,
    fade_transitions: bool = False,
    ken_burns: bool = False,
    subtitle_path: Path | None = None,
    music_path: Path | None = None,
) -> list[str]:
    video_filter = (
        "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p"
    )
    if ken_burns:
        video_filter += ",zoompan=z='min(zoom+0.0005,1.08)':d=1:s=1920x1080:fps=30"
    if fade_transitions:
        video_filter += ",fade=t=in:st=0:d=0.4"
    if subtitle_path:
        video_filter += f",subtitles='{_ffmpeg_filter_path(subtitle_path)}'"
    filter_complex = f"{video_filter}[v]"
    command = [
        os.getenv("CREATORFORGE_FFMPEG_BIN", "ffmpeg"), "-y", "-f", "concat", "-safe", "0",
        "-i", str(manifest_path), "-i", str(voice_path),
    ]
    if music_path:
        command.extend(["-stream_loop", "-1", "-i", str(music_path)])
        filter_complex += ";[1:a][2:a]amix=inputs=2:duration=first:weights='1 0.18'[a]"
    command.extend(["-filter_complex", filter_complex, "-map", "[v]", "-map", "[a]" if music_path else "1:a"])
    command.extend([
        "-r", str(VIDEO_FPS), "-c:v", "libx264", "-c:a", "aac", "-shortest",
        "-movflags", "+faststart", str(output_path),
    ])
    return command


def _validate_options(visual_mode: str, image_duration_seconds: float | None) -> None:
    if visual_mode not in {"manual", "ai", "mixed"}:
        raise VideoServiceError("Visual mode must be manual, ai, or mixed.")
    if image_duration_seconds is not None and image_duration_seconds <= 0:
        raise VideoServiceError("Image duration must be greater than zero.")


def _get_project_images(images_directory: Path, visual_mode: str) -> list[Path]:
    image_paths = _get_user_images(images_directory)
    if visual_mode == "ai":
        image_paths = [path for path in image_paths if path.name.startswith("scene_")]
        if not image_paths:
            raise VideoServiceError("AI scene images are required before rendering in AI mode.")
    return image_paths


def _get_user_images(images_directory: Path) -> list[Path]:
    if not images_directory.is_dir():
        raise VideoServiceError("Project images are required. Copy JPG, PNG, or WebP files into images/ before generating video.")
    image_paths = sorted(path for path in images_directory.iterdir() if path.is_file() and path.suffix.casefold() in IMAGE_EXTENSIONS)
    if not image_paths:
        raise VideoServiceError("Project images are required. Copy JPG, PNG, or WebP files into images/ before generating video.")
    return image_paths


def _get_background_music(project_directory: Path) -> Path:
    for extension in AUDIO_EXTENSIONS:
        candidate = project_directory / f"{BACKGROUND_MUSIC_BASENAME}{extension}"
        if candidate.is_file():
            return candidate
    raise VideoServiceError("Background music is enabled but no supported background_music file exists.")


def _wav_duration(voice_path: Path) -> float:
    try:
        with wave.open(str(voice_path), "rb") as audio_file:
            sample_rate = audio_file.getframerate()
            if sample_rate <= 0:
                raise VideoServiceError("Project narration has an invalid sample rate.")
            return round(audio_file.getnframes() / sample_rate, 3)
    except wave.Error as error:
        raise VideoServiceError("Project narration must be a valid WAV file.") from error


def _write_concat_manifest(project_directory: Path, image_paths: list[Path], image_duration: float) -> Path:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ffconcat", prefix="creatorforge-video-", dir=project_directory, encoding="utf-8", delete=False) as manifest:
        for image_path in image_paths:
            manifest.write(f"file '{_ffconcat_path(image_path)}'\n")
            manifest.write(f"duration {image_duration:.3f}\n")
        manifest.write(f"file '{_ffconcat_path(image_paths[-1])}'\n")
        return Path(manifest.name)


def _write_subtitles(project_directory: Path, project: dict[str, object], image_duration: float) -> Path:
    script = project.get("script")
    passages = [" ".join(part.split()) for part in str(script or "").split("\n\n") if part.strip()]
    if not passages:
        raise VideoServiceError("A project script is required to generate subtitles.")
    subtitle_path = project_directory / SUBTITLE_FILENAME
    lines: list[str] = []
    for index, passage in enumerate(passages, 1):
        start = (index - 1) * image_duration
        end = index * image_duration
        lines.extend([str(index), f"{_srt_timestamp(start)} --> {_srt_timestamp(end)}", passage, ""])
    subtitle_path.write_text("\n".join(lines), encoding="utf-8")
    return subtitle_path


def _srt_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{whole_seconds:02},{milliseconds:03}"


def _ffconcat_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", r"'\\''")


def _ffmpeg_filter_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", r"\\'").replace(":", r"\:")


def _run_ffmpeg(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as error:
        raise FFmpegUnavailableError("FFmpeg is unavailable. Install FFmpeg and add it to PATH.") from error
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() or "Unknown FFmpeg failure."
        raise VideoServiceError(f"FFmpeg could not render the video: {details}") from error
