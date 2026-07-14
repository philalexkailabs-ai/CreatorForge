import unittest
from unittest.mock import patch

from backend.services.comfyui_client import ComfyUIClient, ComfyUIClientError


class ComfyUIClientTests(unittest.TestCase):
    def test_generate_image_retries_a_failed_attempt(self) -> None:
        client = ComfyUIClient(max_attempts=2, poll_interval_seconds=0)
        with (
            patch.object(client, "queue_prompt", side_effect=[ComfyUIClientError("offline"), "id-1"]),
            patch.object(client, "wait_for_output", return_value={"filename": "image.png"}),
            patch.object(client, "download_image", return_value=b"png"),
        ):
            self.assertEqual(client.generate_image({}), b"png")


if __name__ == "__main__":
    unittest.main()
