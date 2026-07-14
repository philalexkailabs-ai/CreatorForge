"""Project-level AI image orchestration and artifact persistence."""

from __future__ import annotations

import copy
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.services.comfyui_client import ComfyUIClient, ComfyUIClientError
from backend.services.project_service import get_project, get_project_directory


WORKFLOW_DIRECTORY = Path(__file__).resolve().parents[1] / "workflows"
DEFAULT_WORKFLOW = "sdxl_turbo.json"
WORKFLOW_NAMES = {"sdxl_turbo.json", "biblical.json", "business.json", "technology.json"}
MANIFEST_FILENAME = "scene_manifest.json"
IMAGE_DIRECTORY_NAME = "images"
VISUAL_MODES = {"manual", "ai", "mixed"}
DEFAULT_SCENE_DURATION_SECONDS = 5.0
logger = logging.getLogger(__name__)


class ImageServiceError(RuntimeError):
    pass


def generate_project_images(
    project_id: str,
    workflow_name: str = DEFAULT_WORKFLOW,
    visual_mode: str = "ai",
    scene_duration_seconds: float = DEFAULT_SCENE_DURATION_SECONDS,
) -> dict[str, object]:
    """Plan and persist project visuals, generating scenes when requested."""
    _validate_options(workflow_name, visual_mode, scene_duration_seconds)
    logger.info(
        "Planning project images project_id=%s workflow=%s visual_mode=%s",
        project_id,
        workflow_name,
        visual_mode,
    )
    project = get_project(project_id)
    scenes = _build_scenes(project)
    project_directory = get_project_directory(project_id)
    image_directory = project_directory / IMAGE_DIRECTORY_NAME
    image_directory.mkdir(parents=True, exist_ok=True)
    workflow_template = _load_workflow(workflow_name) if visual_mode != "manual" else None
    manifest = _new_manifest(workflow_name, visual_mode, workflow_template)
    _write_manifest(project_directory, manifest)

    for scene in scenes:
        _persist_scene(
            project_directory,
            manifest,
            scene,
            workflow_template,
            visual_mode,
            scene_duration_seconds,
        )
    return manifest


def regenerate_project_image(project_id: str, scene_number: int) -> dict[str, object]:
    """Regenerate one planned AI scene without changing the project script."""
    if scene_number < 1:
        raise ImageServiceError("Scene number must be a positive integer.")
    logger.info("Regenerating project image project_id=%s scene=%s", project_id, scene_number)
    project_directory = get_project_directory(project_id)
    manifest = _read_manifest(project_directory)
    if manifest is None:
        raise ImageServiceError("Generate or plan project images before regenerating a scene.")
    scenes = manifest.get("scenes")
    if not isinstance(scenes, list):
        raise ImageServiceError("The scene manifest is invalid.")
    scene = next((item for item in scenes if isinstance(item, dict) and item.get("number") == scene_number), None)
    if scene is None:
        raise ImageServiceError("Scene number was not found in this project.")
    prompt_name = scene.get("prompt_filename") or scene.get("prompt_file")
    if not isinstance(prompt_name, str):
        raise ImageServiceError("The scene prompt is unavailable.")
    try:
        prompt = (project_directory / prompt_name).read_text(encoding="utf-8").strip()
    except OSError as error:
        raise ImageServiceError("The scene prompt is unavailable.") from error
    workflow_name = manifest.get("workflow")
    if not isinstance(workflow_name, str):
        raise ImageServiceError("The scene workflow is invalid.")
    template = _load_workflow(workflow_name)
    seed = _next_seed(scene.get("seed"), scene_number)
    image_path = project_directory / IMAGE_DIRECTORY_NAME / f"scene_{scene_number:03d}.png"
    try:
        image_path.write_bytes(ComfyUIClient().generate_image(_workflow_for_scene(template, prompt, seed)))
    except ComfyUIClientError as error:
        raise ImageServiceError(str(error)) from error
    scene.update(_scene_metadata(template, scene_number, prompt_name, image_path.name, seed, scene.get("duration_seconds")))
    manifest["generated_at"] = _timestamp()
    _write_manifest(project_directory, manifest)
    return scene


def _persist_scene(
    project_directory: Path,
    manifest: dict[str, object],
    scene: dict[str, object],
    workflow_template: dict[str, Any] | None,
    visual_mode: str,
    duration_seconds: float,
) -> None:
    number = int(scene["number"])
    prompt = str(scene["prompt"])
    prompt_name = f"scene_{number:03d}.prompt.txt"
    image_path = project_directory / IMAGE_DIRECTORY_NAME / f"scene_{number:03d}.png"
    (project_directory / prompt_name).write_text(prompt, encoding="utf-8")
    seed = number
    if visual_mode == "ai" or (visual_mode == "mixed" and not image_path.is_file()):
        if workflow_template is None:
            raise ImageServiceError("An AI workflow is required for generated scenes.")
        try:
            image_path.write_bytes(ComfyUIClient().generate_image(_workflow_for_scene(workflow_template, prompt, seed)))
        except ComfyUIClientError as error:
            raise ImageServiceError(str(error)) from error
    if visual_mode == "manual" and not image_path.is_file():
        image_filename: str | None = None
    else:
        image_filename = image_path.name if image_path.is_file() else None
    template = workflow_template or _load_workflow(DEFAULT_WORKFLOW)
    scene_data = _scene_metadata(template, number, prompt_name, image_filename, seed, duration_seconds)
    manifest_scenes = manifest["scenes"]
    if isinstance(manifest_scenes, list):
        manifest_scenes.append(scene_data)
    _write_manifest(project_directory, manifest)


def _new_manifest(
    workflow_name: str,
    visual_mode: str,
    template: dict[str, Any] | None,
) -> dict[str, object]:
    metadata_template = template or _load_workflow(DEFAULT_WORKFLOW)
    return {
        "version": 2,
        "workflow": workflow_name,
        "checkpoint": _workflow_checkpoint(metadata_template),
        "generated_at": _timestamp(),
        "visual_mode": visual_mode,
        "scenes": [],
    }


def _scene_metadata(
    template: dict[str, Any], number: int, prompt_name: str, image_name: str | None, seed: int, duration: object) -> dict[str, object]:
    width, height = _workflow_resolution(template)
    return {
        "number": number,
        "workflow": _workflow_name(template),
        "checkpoint": _workflow_checkpoint(template),
        "generated_at": _timestamp(),
        "seed": seed,
        "resolution": {"width": width, "height": height},
        "duration_seconds": duration if isinstance(duration, (int, float)) else DEFAULT_SCENE_DURATION_SECONDS,
        "prompt_filename": prompt_name,
        "image_filename": f"{IMAGE_DIRECTORY_NAME}/{image_name}" if image_name else None,
    }


def _build_scenes(project: dict[str, object]) -> list[dict[str, object]]:
    script = project.get("script")
    if not isinstance(script, str) or not script.strip():
        raise ImageServiceError("A project script is required to generate AI images.")
    topic = project.get("topic") if isinstance(project.get("topic"), str) else ""
    passages = [part.strip() for part in re.split(r"\n\s*\n", script) if part.strip()]
    if not passages:
        raise ImageServiceError("A project script is required to generate AI images.")
    return [{"number": index, "prompt": _scene_prompt(topic, passage)} for index, passage in enumerate(passages, 1)]


def _scene_prompt(topic: str, passage: str) -> str:
    return (f"Cinematic documentary scene about {topic}. {' '.join(passage.split())}. " "Visually coherent, detailed, natural lighting, 16:9 composition, no text, no watermark.")


def _load_workflow(workflow_name: str = DEFAULT_WORKFLOW) -> dict[str, Any]:
    if workflow_name not in WORKFLOW_NAMES:
        raise ImageServiceError("Unsupported ComfyUI workflow.")
    try:
        workflow = json.loads((WORKFLOW_DIRECTORY / workflow_name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ImageServiceError("The bundled ComfyUI workflow is unavailable or invalid.") from error
    if not isinstance(workflow, dict):
        raise ImageServiceError("The bundled ComfyUI workflow is invalid.")
    _validate_workflow(workflow)
    return workflow


def _validate_workflow(workflow: dict[str, Any]) -> None:
    try:
        if not all(isinstance(workflow[key]["inputs"], dict) for key in ("3", "4", "5", "6")):
            raise KeyError
        if not isinstance(workflow["4"]["inputs"].get("ckpt_name"), str):
            raise KeyError
    except (KeyError, TypeError) as error:
        raise ImageServiceError("The bundled ComfyUI workflow has unsupported inputs.") from error


def _workflow_for_scene(template: dict[str, Any], prompt: str, seed: int) -> dict[str, Any]:
    workflow = copy.deepcopy(template)
    try:
        workflow["6"]["inputs"]["text"] = prompt
        workflow["3"]["inputs"]["seed"] = seed
    except (KeyError, TypeError) as error:
        raise ImageServiceError("The bundled ComfyUI workflow has unsupported inputs.") from error
    return workflow


def _workflow_checkpoint(template: dict[str, Any]) -> str:
    return str(template["4"]["inputs"]["ckpt_name"])


def _workflow_resolution(template: dict[str, Any]) -> tuple[int, int]:
    inputs = template["5"]["inputs"]
    return int(inputs.get("width", 1024)), int(inputs.get("height", 576))


def _workflow_name(template: dict[str, Any]) -> str:
    return DEFAULT_WORKFLOW


def _validate_options(workflow_name: str, visual_mode: str, duration: float) -> None:
    if workflow_name not in WORKFLOW_NAMES:
        raise ImageServiceError("Unsupported ComfyUI workflow.")
    if visual_mode not in VISUAL_MODES:
        raise ImageServiceError("Visual mode must be manual, ai, or mixed.")
    if duration <= 0:
        raise ImageServiceError("Scene duration must be greater than zero.")


def _read_manifest(project_directory: Path) -> dict[str, object] | None:
    try:
        value = json.loads((project_directory / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _next_seed(seed: object, fallback: int) -> int:
    return seed + 1 if isinstance(seed, int) else fallback + 1


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_manifest(project_directory: Path, manifest: dict[str, object]) -> None:
    (project_directory / MANIFEST_FILENAME).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
