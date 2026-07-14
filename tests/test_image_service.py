import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.services import image_service


class ImageServiceTests(unittest.TestCase):
    def test_generate_project_images_persists_prompts_images_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            project = {"topic": "Solar eclipses", "script": "First scene.\n\nSecond scene."}
            with (
                patch.object(image_service, "get_project", return_value=project),
                patch.object(image_service, "get_project_directory", return_value=project_directory),
                patch.object(image_service, "ComfyUIClient") as client_type,
            ):
                client_type.return_value.generate_image.return_value = b"png"
                manifest = image_service.generate_project_images("project-1")

            self.assertEqual(len(manifest["scenes"]), 2)
            self.assertTrue((project_directory / "scene_001.prompt.txt").is_file())
            self.assertTrue((project_directory / "scene_002.prompt.txt").is_file())
            self.assertEqual((project_directory / "images" / "scene_001.png").read_bytes(), b"png")
            saved_manifest = json.loads((project_directory / "scene_manifest.json").read_text())
            self.assertEqual(saved_manifest["provider"], "comfyui")
            self.assertEqual(saved_manifest["scenes"][0]["image_file"], "images/scene_001.png")

    def test_workflow_for_scene_does_not_mutate_template(self) -> None:
        template = image_service._load_workflow()
        workflow = image_service._workflow_for_scene(template, "A prompt", 2)
        self.assertEqual(workflow["6"]["inputs"]["text"], "A prompt")
        self.assertEqual(workflow["3"]["inputs"]["seed"], 2)
        self.assertEqual(template["6"]["inputs"]["text"], "")

    def test_provider_failure_still_saves_an_empty_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            with (
                patch.object(
                    image_service,
                    "get_project",
                    return_value={"topic": "Topic", "script": "One scene."},
                ),
                patch.object(image_service, "get_project_directory", return_value=project_directory),
                patch.object(image_service, "ComfyUIClient") as client_type,
            ):
                client_type.return_value.generate_image.side_effect = (
                    image_service.ComfyUIClientError("unavailable")
                )
                with self.assertRaises(image_service.ImageServiceError):
                    image_service.generate_project_images("project-1")

            manifest = json.loads((project_directory / "scene_manifest.json").read_text())
            self.assertEqual(manifest["scenes"], [])


if __name__ == "__main__":
    unittest.main()
