from __future__ import annotations

import json
import logging
import os
import re
import time

import httpx

from backend.app.services.llm.model_config import get_model_config

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "60"))
MAX_RETRIES = 3
BASE_DELAY = 1.0


class OllamaClient:
    """HTTP client for the Ollama local LLM API.

    Provides synchronous methods for text generation, JSON generation,
    and model listing. Includes automatic retry with exponential backoff
    for transient connection failures.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Initialize the Ollama client.

        Args:
            base_url: Ollama server URL. Defaults to OLLAMA_BASE_URL env var.
            timeout: Request timeout in seconds. Defaults to OLLAMA_TIMEOUT env var.
        """
        self._base_url = (base_url or OLLAMA_BASE_URL).rstrip("/")
        self._timeout = timeout or OLLAMA_TIMEOUT

    def _get_client(self) -> httpx.Client:
        return httpx.Client(base_url=self._base_url, timeout=self._timeout)

    def _request_with_retry(
        self, method: str, path: str, **kwargs: object
    ) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                with self._get_client() as client:
                    response = client.request(method, path, **kwargs)
                    response.raise_for_status()
                    return response
            except (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout) as e:
                last_error = e
                logger.warning(
                    "Ollama request attempt %d/%d failed: %s",
                    attempt + 1,
                    MAX_RETRIES,
                    e,
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BASE_DELAY * (2 ** attempt))
        raise ConnectionError(
            f"Failed to connect to Ollama after {MAX_RETRIES} attempts"
        ) from last_error

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str | None = None,
    ) -> str:
        """Generate a text response from the LLM.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system-level instructions.
            model: Model name override. Uses default if None.

        Returns:
            The generated text response.
        """
        config = get_model_config(model)
        payload: dict[str, object] = {
            "model": config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "num_predict": config.num_predict,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        response = self._request_with_retry("POST", "/api/generate", json=payload)
        data = response.json()
        return data.get("response", "")

    def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str | None = None,
    ) -> dict:
        """Generate a JSON response from the LLM with automatic parsing.

        Retries once if the initial response cannot be parsed as JSON.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system-level instructions.
            model: Model name override. Uses default if None.

        Returns:
            Parsed JSON as a dictionary.

        Raises:
            ValueError: If the response cannot be parsed as JSON after retry.
        """
        for attempt in range(2):
            response_text = self.generate(prompt, system_prompt, model)
            parsed = self._parse_json(response_text)
            if parsed is not None:
                return parsed
            logger.warning(
                "JSON parse failed on attempt %d, retrying", attempt + 1
            )
        raise ValueError(f"Failed to parse JSON from LLM response: {response_text[:200]}")

    def _parse_json(self, text: str) -> dict | None:
        cleaned = text.strip()
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
        try:
            result = json.loads(cleaned)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end > start:
            try:
                result = json.loads(cleaned[start : end + 1])
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass
        return None

    def list_models(self) -> list[str]:
        """List available models from the Ollama server."""
        response = self._request_with_retry("GET", "/api/tags")
        data = response.json()
        models = data.get("models", [])
        return [m.get("name", "") for m in models if m.get("name")]
