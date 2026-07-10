from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from backend.services.project_service import (
    ProjectMetadataError,
    ProjectNotFoundError,
    get_project as get_saved_project,
    list_projects as list_saved_projects,
)
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

        generation_status["stage"] = "Saving"
        save_project(request.topic, project)

        generation_status.update(running=False, stage="Completed")
        return project
    finally:
        generation_status.update(running=False, stage="Idle")
