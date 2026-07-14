import logging

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
)
from backend.services.tts_service import TTSServiceError, generate_voice
from backend.services.video_service import VideoServiceError, render_project_video
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


@app.get("/")
def home():
    return {"message": "CreatorForge Running 🚀"}


@app.get("/projects")
def get_projects() -> list[dict[str, str]]:
    return list_saved_projects()


@app.get("/generation/status")
def get_generation_status() -> dict[str, object]:
    return generation_status.copy()


@app.get("/projects/{project_id}")
def get_project(project_id: str) -> dict[str, object]:
    return get_saved_project(project_id)


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
def generate_project_video(project_id: str) -> dict[str, object]:
    return render_project_video(project_id)


@app.get("/projects/{project_id}/video")
def get_project_video(project_id: str) -> FileResponse:
    return FileResponse(get_video_path(project_id), media_type="video/mp4")


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
                "voice": voice,
            },
        )

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
        return project
    finally:
        generation_status.update(running=False, stage="Idle")
