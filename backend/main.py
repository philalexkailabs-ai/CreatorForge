import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from backend.ollama import UnsupportedModelError
from backend.services.generator import (
    generate_description as generate_description_content,
    generate_outline as generate_outline_content,
    generate_research as generate_research_content,
    generate_research_summary as generate_research_summary_content,
    generate_script as generate_script_content,
    generate_tags as generate_tags_content,
    generate_thumbnail as generate_thumbnail_content,
    generate_titles as generate_titles_content,
)
from backend.services.project_saver import save_project
from backend.services.export_service import create_project_export
from backend.services.project_service import (
    ProjectMetadataError,
    ProjectNotFoundError,
    ProjectVoiceNotFoundError,
    ProjectVideoNotFoundError,
    get_video_path,
    get_voice_path,
    get_project as get_saved_project,
    list_projects as list_saved_projects,
    rename_project,
    duplicate_project,
    delete_project,
    set_project_favorite,
    dashboard_metrics,
)
from backend.services.settings_service import get_settings, save_settings
from backend.services.diagnostics_service import get_diagnostics
from backend.services.tts_service import TTSServiceError, generate_voice
from backend.services.video_service import VideoServiceError, render_project_video
from backend.services.image_service import (
    ImageServiceError,
    generate_project_images,
    regenerate_project_image,
)
from backend.services.youtube_service import (
    YouTubeServiceError,
    retry_upload_project_video,
    upload_project_video,
)
from backend.services.validator import (
    validate_description,
    validate_outline,
    validate_research,
    validate_research_summary,
    validate_script,
    validate_tags,
    validate_thumbnail,
    validate_titles,
)

logger = logging.getLogger(__name__)
app = FastAPI(title="CreatorForge")
generation_status = {
    "running": False,
    "stage": "Idle",
}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    topic: str
    model: str | None = None
    full_pipeline: bool = False


class ImageGenerationRequest(BaseModel):
    workflow: str = "sdxl_turbo.json"
    visual_mode: str = "ai"
    scene_duration_seconds: float = 5.0


class VideoRenderRequest(BaseModel):
    visual_mode: str = "manual"
    image_duration_seconds: float | None = None
    fade_transitions: bool = False
    ken_burns: bool = False
    subtitles: bool = False
    background_music: bool = False


class ProjectNameRequest(BaseModel):
    name: str


class FavoriteRequest(BaseModel):
    favorite: bool


class SettingsRequest(BaseModel):
    ollama_url: str | None = None
    comfyui_url: str | None = None
    ffmpeg_path: str | None = None
    tts_provider: str | None = None
    default_model: str | None = None
    workflow_template: str | None = None
    theme: str | None = None
    youtube_client_secrets: str | None = None


@app.exception_handler(UnsupportedModelError)
def unsupported_model_handler(
    request: Request,
    exc: UnsupportedModelError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": f"Unsupported model: {exc.model}"},
    )


@app.exception_handler(ProjectNotFoundError)
def project_not_found_handler(
    request: Request,
    exc: ProjectNotFoundError,
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ProjectMetadataError)
def project_metadata_handler(
    request: Request,
    exc: ProjectMetadataError,
) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(ProjectVoiceNotFoundError)
def project_voice_not_found_handler(
    request: Request,
    exc: ProjectVoiceNotFoundError,
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(TTSServiceError)
def tts_service_error_handler(
    request: Request,
    exc: TTSServiceError,
) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(ProjectVideoNotFoundError)
def project_video_not_found_handler(
    request: Request,
    exc: ProjectVideoNotFoundError,
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(VideoServiceError)
def video_service_error_handler(
    request: Request,
    exc: VideoServiceError,
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(ImageServiceError)
def image_service_error_handler(
    request: Request,
    exc: ImageServiceError,
) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(YouTubeServiceError)
def youtube_service_error_handler(
    request: Request,
    exc: YouTubeServiceError,
) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.get("/")
def home():
    return {"message": "CreatorForge Running 🚀"}


@app.get("/projects")
def get_projects(search: str = "", sort: str = "updated") -> list[dict[str, str]]:
    return list_saved_projects(search, sort)


@app.get("/dashboard")
def get_dashboard() -> dict[str, object]:
    return dashboard_metrics()


@app.get("/settings")
def get_application_settings() -> dict[str, object]:
    return get_settings()


@app.put("/settings")
def update_application_settings(request: SettingsRequest) -> dict[str, object]:
    saved = save_settings(request.model_dump(exclude_none=True))
    environment = {
        "CREATORFORGE_OLLAMA_URL": "ollama_url",
        "CREATORFORGE_COMFYUI_URL": "comfyui_url",
        "CREATORFORGE_FFMPEG_BIN": "ffmpeg_path",
        "CREATORFORGE_TTS_PROVIDER": "tts_provider",
        "CREATORFORGE_YOUTUBE_CLIENT_SECRETS": "youtube_client_secrets",
    }
    for variable, field in environment.items():
        value = saved.get(field)
        if isinstance(value, str) and value:
            os.environ[variable] = value
    return saved


@app.get("/diagnostics")
def get_startup_diagnostics() -> dict[str, object]:
    return get_diagnostics()


@app.get("/generation/status")
def get_generation_status() -> dict[str, object]:
    return generation_status.copy()


@app.get("/projects/{project_id}")
def get_project(project_id: str) -> dict[str, object]:
    return get_saved_project(project_id)


@app.put("/projects/{project_id}/name")
def update_project_name(project_id: str, request: ProjectNameRequest) -> dict[str, object]:
    return rename_project(project_id, request.name)


@app.post("/projects/{project_id}/duplicate")
def duplicate_saved_project(project_id: str, request: ProjectNameRequest | None = None) -> dict[str, str]:
    return duplicate_project(project_id, request.name if request else None)


@app.delete("/projects/{project_id}", status_code=204)
def remove_project(project_id: str) -> None:
    delete_project(project_id)


@app.put("/projects/{project_id}/favorite")
def update_project_favorite(project_id: str, request: FavoriteRequest) -> dict[str, object]:
    return set_project_favorite(project_id, request.favorite)


@app.get("/projects/{project_id}/export")
def export_project(project_id: str) -> FileResponse:
    archive_path = create_project_export(project_id)
    return FileResponse(
        archive_path,
        media_type="application/zip",
        filename=f"creatorforge-project-{project_id}.zip",
    )


@app.get("/projects/{project_id}/voice")
def get_project_voice(project_id: str) -> FileResponse:
    return FileResponse(get_voice_path(project_id), media_type="audio/wav")


@app.post("/projects/{project_id}/video")
def generate_project_video(
    project_id: str,
    request: VideoRenderRequest | None = None,
) -> dict[str, object]:
    options = request or VideoRenderRequest()
    return render_project_video(
        project_id,
        visual_mode=options.visual_mode,
        image_duration_seconds=options.image_duration_seconds,
        fade_transitions=options.fade_transitions,
        ken_burns=options.ken_burns,
        subtitles=options.subtitles,
        background_music=options.background_music,
    )


@app.post("/projects/{project_id}/images")
def generate_project_images_route(
    project_id: str,
    request: ImageGenerationRequest | None = None,
) -> dict[str, object]:
    options = request or ImageGenerationRequest()
    return generate_project_images(
        project_id,
        workflow_name=options.workflow,
        visual_mode=options.visual_mode,
        scene_duration_seconds=options.scene_duration_seconds,
    )


@app.post("/projects/{project_id}/images/{scene_number}/regenerate")
def regenerate_project_image_route(project_id: str, scene_number: int) -> dict[str, object]:
    return regenerate_project_image(project_id, scene_number)


@app.post("/projects/{project_id}/voice")
def regenerate_project_voice(project_id: str) -> dict[str, object]:
    return generate_voice(project_id)


@app.get("/projects/{project_id}/video")
def get_project_video(project_id: str) -> FileResponse:
    return FileResponse(get_video_path(project_id), media_type="video/mp4")


@app.post("/projects/{project_id}/youtube-upload")
def upload_project_to_youtube(project_id: str) -> dict[str, object]:
    return upload_project_video(project_id)


@app.post("/projects/{project_id}/youtube-upload/retry")
def retry_project_youtube_upload(project_id: str) -> dict[str, object]:
    return retry_upload_project_video(project_id)


@app.post("/generate/titles")
def generate_titles(request: TopicRequest):
    return {
        "titles": generate_titles_content(request.topic, request.model)
    }
@app.post("/generate/script")
def generate_script(request: TopicRequest):
    return {
        "script": generate_script_content(request.topic, request.model)
    }


@app.post("/generate/thumbnail")
def generate_thumbnail(request: TopicRequest):
    return {
        "thumbnail_prompt": generate_thumbnail_content(request.topic, request.model)
    }


@app.post("/generate/project")
def generate_project(request: TopicRequest):
    generation_status.update(running=True, stage="Research")

    try:
        research = generate_research_content(request.topic, request.model)

        generation_status["stage"] = "Research Summary"
        research_summary = generate_research_summary_content(
            research,
            request.model,
        )

        generation_status["stage"] = "Outline"
        outline = generate_outline_content(
            request.topic,
            model=request.model,
            research_summary=research_summary,
        )

        generation_status["stage"] = "Titles"
        titles = generate_titles_content(
            request.topic,
            request.model,
            research_summary=research_summary,
            outline=outline,
        )

        generation_status["stage"] = "Script"
        script = generate_script_content(
            request.topic,
            request.model,
            research_summary=research_summary,
            outline=outline,
            titles=titles,
        )

        project = {
            "titles": titles,
            "script": script,
            "description": "",
            "tags": [],
            "research": research,
            "research_summary": research_summary,
            "outline": outline,
            "thumbnail_prompt": "",
        }
        saved_project = save_project(request.topic, project)

        voice: dict[str, object] | None = None
        if not request.full_pipeline:
            generation_status["stage"] = "Voice"
            voice = generate_voice(saved_project["id"])

        generation_status["stage"] = "Description"
        description = generate_description_content(
            request.topic,
            request.model,
            research_summary=research_summary,
            outline=outline,
            script=script,
        )

        generation_status["stage"] = "Tags"
        tags = generate_tags_content(
            request.topic,
            request.model,
            research_summary=research_summary,
            outline=outline,
            script=script,
        )

        generation_status["stage"] = "Thumbnail"
        thumbnail_prompt = generate_thumbnail_content(
            request.topic,
            request.model,
            research_summary=research_summary,
            outline=outline,
            script=script,
        )

        project = {
            "titles": titles,
            "script": script,
            "description": description,
            "tags": tags,
            "research": research,
            "research_summary": research_summary,
            "outline": outline,
            "thumbnail_prompt": thumbnail_prompt,
        }
        saved_project = save_project(
            request.topic,
            {
                **project,
                "id": saved_project["id"],
                "created": saved_project["created"],
                **({"voice": voice} if voice else {}),
            },
        )

        pipeline: dict[str, str] = {}
        if request.full_pipeline:
            for stage, action in (
                ("Images", lambda: generate_project_images(saved_project["id"])),
                ("Voice", lambda: generate_voice(saved_project["id"])),
                ("Video", lambda: render_project_video(saved_project["id"], visual_mode="ai", subtitles=True)),
                ("Upload", lambda: upload_project_video(saved_project["id"])),
            ):
                generation_status["stage"] = stage
                try:
                    action()
                    pipeline[stage.casefold()] = "completed"
                except (ImageServiceError, VideoServiceError, YouTubeServiceError) as error:
                    logger.warning("Pipeline stage %s failed: %s", stage, error)
                    pipeline[stage.casefold()] = str(error)

        validation_results = {
            "research": validate_research(research),
            "research_summary": validate_research_summary(research_summary),
            "outline": validate_outline(outline),
            "titles": validate_titles(titles),
            "script": validate_script(script),
            "description": validate_description(description),
            "tags": validate_tags(tags),
            "thumbnail_prompt": validate_thumbnail(thumbnail_prompt),
        }

        for artifact, result in validation_results.items():
            if not result["valid"]:
                logger.warning("Validation failed for %s: %s", artifact, result)

        generation_status["stage"] = "Saving"

        generation_status.update(running=False, stage="Completed")
        return {**project, "pipeline": pipeline}
    finally:
        generation_status.update(running=False, stage="Idle")
