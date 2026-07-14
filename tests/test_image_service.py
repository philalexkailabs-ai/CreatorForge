import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.services import image_service


class ImageServiceTests(unittest.TestCase):
    def test_workflow_loading_validates_sdxl_and_rejects_placeholder(self) -> None:
        workflow = image_service._load_workflow()
        self.assertEqual(workflow["4"]["inputs"]["ckpt_name"], "sd_xl_turbo_1.0_fp16.safetensors")
        with self.assertRaises(image_service.ImageServiceError):
            image_service._load_workflow("biblical.json")

    def test_generate_project_images_persists_complete_scene_manifest(self) -> None:
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

            self.assertEqual(manifest["workflow"], "sdxl_turbo.json")
            self.assertEqual(manifest["checkpoint"], "sd_xl_turbo_1.0_fp16.safetensors")
            scene = manifest["scenes"][0]
            self.assertEqual(scene["seed"], 1)
            self.assertEqual(scene["resolution"], {"width": 1024, "height": 576})
            self.assertEqual(scene["prompt_filename"], "scene_001.prompt.txt")
            self.assertEqual(scene["image_filename"], "images/scene_001.png")
            self.assertTrue((project_directory / "scene_002.prompt.txt").is_file())
            saved_manifest = json.loads((project_directory / "scene_manifest.json").read_text())
            self.assertEqual(len(saved_manifest["scenes"]), 2)

    def test_regenerate_one_scene_preserves_other_scenes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            images = project_directory / "images"
            images.mkdir()
            (project_directory / "scene_001.prompt.txt").write_text("Prompt one")
            (project_directory / "scene_002.prompt.txt").write_text("Prompt two")
            manifest = {
                "workflow": "sdxl_turbo.json", "scenes": [
                    {"number": 1, "seed": 1, "prompt_filename": "scene_001.prompt.txt", "duration_seconds": 5},
                    {"number": 2, "seed": 2, "prompt_filename": "scene_002.prompt.txt", "duration_seconds": 5},
                ],
            }
            (project_directory / "scene_manifest.json").write_text(json.dumps(manifest))
            with (
                patch.object(image_service, "get_project_directory", return_value=project_directory),
                patch.object(image_service, "ComfyUIClient") as client_type,
            ):
                client_type.return_value.generate_image.return_value = b"replacement"
                result = image_service.regenerate_project_image("project-1", 2)

            self.assertEqual(result["number"], 2)
            self.assertEqual(result["seed"], 3)
            self.assertEqual((images / "scene_002.png").read_bytes(), b"replacement")
            saved = json.loads((project_directory / "scene_manifest.json").read_text())
            self.assertEqual(saved["scenes"][0]["number"], 1)

    def test_manual_mode_creates_scene_plan_without_comfyui(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            with (
                patch.object(image_service, "get_project", return_value={"topic": "Topic", "script": "One scene."}),
                patch.object(image_service, "get_project_directory", return_value=project_directory),
                patch.object(image_service, "ComfyUIClient") as client_type,
            ):
                manifest = image_service.generate_project_images("project-1", visual_mode="manual")
            client_type.assert_not_called()
            self.assertEqual(manifest["visual_mode"], "manual")
            self.assertIsNone(manifest["scenes"][0]["image_filename"])


if __name__ == "__main__":
    unittest.main()
