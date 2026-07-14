"""Project-level AI image orchestration and artifact persistence."""

from __future__ import annotations

import copy
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.services.comfyui_client import ComfyUIClient, ComfyUIClientError
from backend.services.project_service import get_project, get_project_directory


WORKFLOW_PATH = Path(__file__).resolve().parents[1] / "workflows" / "sdxl_turbo.json"
MANIFEST_FILENAME = "scene_manifest.json"
IMAGE_DIRECTORY_NAME = "images"


class ImageServiceError(RuntimeError):
    pass


def generate_project_images(project_id: str) -> dict[str, object]:
    """Generate one local ComfyUI image per non-empty script paragraph."""
    project = get_project(project_id)
    scenes = _build_scenes(project)
    project_directory = get_project_directory(project_id)
    image_directory = project_directory / IMAGE_DIRECTORY_NAME
    image_directory.mkdir(parents=True, exist_ok=True)
    workflow_template = _load_workflow()
    client = ComfyUIClient()

    manifest_scenes: list[dict[str, object]] = []
    manifest: dict[str, object] = {
        "version": 1,
        "created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provider": "comfyui",
        "workflow": "sdxl_turbo.json",
        "scenes": manifest_scenes,
    }
    _write_manifest(project_directory, manifest)
    for scene in scenes:
        number = scene["number"]
        prompt = scene["prompt"]
        prompt_path = project_directory / f"scene_{number:03d}.prompt.txt"
        image_path = image_directory / f"scene_{number:03d}.png"
        prompt_path.write_text(prompt, encoding="utf-8")
        workflow = _workflow_for_scene(workflow_template, prompt, number)
        try:
            image_path.write_bytes(client.generate_image(workflow))
        except ComfyUIClientError as error:
            raise ImageServiceError(str(error)) from error
        manifest_scenes.append(
            {
                "number": number,
                "prompt_file": prompt_path.name,
                "image_file": f"{IMAGE_DIRECTORY_NAME}/{image_path.name}",
            }
        )
        _write_manifest(project_directory, manifest)
    return manifest


def _build_scenes(project: dict[str, object]) -> list[dict[str, object]]:
    script = project.get("script")
    if not isinstance(script, str) or not script.strip():
        raise ImageServiceError("A project script is required to generate AI images.")
    topic = project.get("topic") if isinstance(project.get("topic"), str) else ""
    passages = [part.strip() for part in re.split(r"\n\s*\n", script) if part.strip()]
    if not passages:
        raise ImageServiceError("A project script is required to generate AI images.")
    return [
        {
            "number": index,
            "prompt": _scene_prompt(topic, passage),
        }
        for index, passage in enumerate(passages, start=1)
    ]


def _scene_prompt(topic: str, passage: str) -> str:
    compact_passage = " ".join(passage.split())
    return (
        f"Cinematic documentary scene about {topic}. {compact_passage}. "
        "Visually coherent, detailed, natural lighting, 16:9 composition, no text, no watermark."
    )


def _load_workflow() -> dict[str, Any]:
    try:
        workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ImageServiceError("The bundled ComfyUI workflow is unavailable or invalid.") from error
    if not isinstance(workflow, dict):
        raise ImageServiceError("The bundled ComfyUI workflow is invalid.")
    return workflow


def _workflow_for_scene(template: dict[str, Any], prompt: str, scene_number: int) -> dict[str, Any]:
    workflow = copy.deepcopy(template)
    try:
        workflow["6"]["inputs"]["text"] = prompt
        workflow["3"]["inputs"]["seed"] = scene_number
    except (KeyError, TypeError) as error:
        raise ImageServiceError("The bundled ComfyUI workflow has unsupported inputs.") from error
    return workflow


def _write_manifest(project_directory: Path, manifest: dict[str, object]) -> None:
    (project_directory / MANIFEST_FILENAME).write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
