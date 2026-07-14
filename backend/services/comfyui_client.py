"""Narrow REST client for a local ComfyUI server."""

from __future__ import annotations

import os
import time
import logging
from typing import Any
from uuid import uuid4

import requests

from backend.config import COMFYUI_URL


logger = logging.getLogger(__name__)


class ComfyUIClientError(RuntimeError):
    """Raised when ComfyUI cannot accept or complete a workflow."""


class ComfyUIClient:
    """Owns all HTTP communication with ComfyUI's REST API."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float = 120.0,
        poll_interval_seconds: float = 0.5,
        max_attempts: int | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("CREATORFORGE_COMFYUI_URL", COMFYUI_URL)).rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self.max_attempts = max_attempts or _configured_attempts()

    def generate_image(self, workflow: dict[str, Any]) -> bytes:
        """Submit a workflow, wait for it, and return its first output image."""
        for attempt in range(1, self.max_attempts + 1):
            try:
                prompt_id = self.queue_prompt(workflow)
                output = self.wait_for_output(prompt_id)
                return self.download_image(output)
            except ComfyUIClientError:
                if attempt == self.max_attempts:
                    raise
                logger.warning(
                    "ComfyUI image attempt %s of %s failed; retrying.",
                    attempt,
                    self.max_attempts,
                )
                time.sleep(min(self.poll_interval_seconds * attempt, 2.0))
        raise ComfyUIClientError("ComfyUI image generation failed.")

    def queue_prompt(self, workflow: dict[str, Any]) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow, "client_id": str(uuid4())},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as error:
            raise ComfyUIClientError("ComfyUI is unavailable. Start ComfyUI and try again.") from error
        except ValueError as error:
            raise ComfyUIClientError("ComfyUI returned an invalid queue response.") from error

        prompt_id = payload.get("prompt_id") if isinstance(payload, dict) else None
        if not isinstance(prompt_id, str) or not prompt_id:
            message = payload.get("error") if isinstance(payload, dict) else None
            raise ComfyUIClientError(f"ComfyUI rejected the workflow: {message or 'unknown error'}")
        return prompt_id

    def wait_for_output(self, prompt_id: str) -> dict[str, str]:
        deadline = time.monotonic() + self.timeout_seconds
        while time.monotonic() < deadline:
            history = self._get_history(prompt_id)
            entry = history.get(prompt_id) if isinstance(history, dict) else None
            if isinstance(entry, dict):
                status = entry.get("status")
                if isinstance(status, dict) and status.get("status_str") == "error":
                    raise ComfyUIClientError("ComfyUI could not generate this image.")
                output = self._first_output(entry)
                if output is not None:
                    return output
            time.sleep(self.poll_interval_seconds)
        raise ComfyUIClientError("ComfyUI image generation timed out.")

    def download_image(self, image: dict[str, str]) -> bytes:
        try:
            response = requests.get(
                f"{self.base_url}/view",
                params=image,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as error:
            raise ComfyUIClientError("ComfyUI could not provide the generated image.") from error

    def _get_history(self, prompt_id: str) -> dict[str, Any]:
        try:
            response = requests.get(
                f"{self.base_url}/history/{prompt_id}",
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as error:
            raise ComfyUIClientError("ComfyUI became unavailable while generating an image.") from error
        except ValueError as error:
            raise ComfyUIClientError("ComfyUI returned invalid generation status.") from error
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _first_output(history_entry: dict[str, Any]) -> dict[str, str] | None:
        outputs = history_entry.get("outputs")
        if not isinstance(outputs, dict):
            return None
        for node_output in outputs.values():
            if not isinstance(node_output, dict):
                continue
            images = node_output.get("images")
            if not isinstance(images, list) or not images:
                continue
            image = images[0]
            if not isinstance(image, dict):
                continue
            filename = image.get("filename")
            if isinstance(filename, str) and filename:
                result = {"filename": filename}
                for field in ("subfolder", "type"):
                    value = image.get(field)
                    if isinstance(value, str):
                        result[field] = value
                return result
        return None


def _configured_attempts() -> int:
    try:
        return max(1, int(os.getenv("CREATORFORGE_COMFYUI_MAX_ATTEMPTS", "2")))
    except ValueError:
        logger.warning("Invalid CREATORFORGE_COMFYUI_MAX_ATTEMPTS; using 2.")
        return 2
