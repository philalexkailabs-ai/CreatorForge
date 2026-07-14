import os
import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


OUTPUT_DIR = "outputs"


def save_project(topic: str, project: dict[str, Any]) -> dict[str, Any]:

    folder_name = topic.replace(" ", "_")

    project_path = os.path.join(OUTPUT_DIR, folder_name)

    os.makedirs(project_path, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    project_id = project.get("id")
    created = project.get("created")
    saved_project = {
        **project,
        "id": project_id if isinstance(project_id, str) and project_id else str(uuid4()),
        "topic": topic,
        "created": created if isinstance(created, str) and created else now,
        "last_modified": now,
        "generator_version": "0.5.3",
    }

    with open(os.path.join(project_path, "project.json"), "w", encoding="utf-8") as f:
        json.dump(saved_project, f, indent=4, ensure_ascii=False)

    with open(os.path.join(project_path, "titles.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(project["titles"]))

    with open(os.path.join(project_path, "script.md"), "w", encoding="utf-8") as f:
        f.write(project["script"])

    with open(os.path.join(project_path, "description.md"), "w", encoding="utf-8") as f:
        f.write(project["description"])

    with open(os.path.join(project_path, "tags.txt"), "w", encoding="utf-8") as f:
        f.write(", ".join(project["tags"]))

    with open(os.path.join(project_path, "research.md"), "w", encoding="utf-8") as f:
        f.write(project.get("research", ""))

    with open(os.path.join(project_path, "research_summary.md"), "w", encoding="utf-8") as f:
        f.write(project.get("research_summary", ""))

    with open(os.path.join(project_path, "outline.md"), "w", encoding="utf-8") as f:
        f.write(project.get("outline", ""))

    with open(os.path.join(project_path, "thumbnail.md"), "w", encoding="utf-8") as f:
        f.write(project.get("thumbnail_prompt", ""))

    return saved_project
