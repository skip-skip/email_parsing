from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


class MockOllamaHandler(BaseHTTPRequestHandler):
    """HTTP handler that simulates Ollama API endpoints."""

    mock_responses: dict[str, Any] = {}
    request_log: list[dict[str, Any]] = []
    request_count: int = 0

    def do_GET(self) -> None:
        if self.path == "/api/tags":
            self._handle_tags()
        else:
            self._send_error(404, "Not found")

    def do_POST(self) -> None:
        if self.path == "/api/generate":
            self._handle_generate()
        else:
            self._send_error(404, "Not found")

    def _handle_tags(self) -> None:
        error_config = self.mock_responses.get("tags_error")
        if error_config is not None:
            if isinstance(error_config, dict):
                self._send_error(
                    error_config.get("code", 500),
                    error_config.get("message", "Internal error"),
                )
            else:
                self._send_error(500, str(error_config))
            return

        models = self.mock_responses.get(
            "tags",
            {"models": [{"name": "gemma3:4b"}, {"name": "qwen3:1.7b"}, {"name": "llama3.2:3b"}]},
        )
        self._send_json(models)

    def _handle_generate(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        request_data = json.loads(body) if body else {}

        self.__class__.request_count += 1
        self.__class__.request_log.append(request_data)

        delay = self.mock_responses.get("delay", 0)
        if delay > 0:
            time.sleep(delay)

        error_config = self.mock_responses.get("error")
        if error_config is not None:
            if callable(error_config):
                result = error_config(request_data)
                if result is not None:
                    code, message = result
                    self._send_error(code, message)
                    return
            elif isinstance(error_config, dict):
                self._send_error(
                    error_config.get("code", 500),
                    error_config.get("message", "Internal error"),
                )
                return
            else:
                self._send_error(500, str(error_config))
                return

        response_generator = self.mock_responses.get("generate")
        if callable(response_generator):
            response_text = response_generator(request_data)
        else:
            response_text = self.mock_responses.get(
                "generate", "Mock response from Ollama"
            )

        self._send_json({"response": response_text})

    def _send_json(self, data: dict[str, Any]) -> None:
        payload = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_error(self, code: int, message: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        payload = json.dumps({"error": message}).encode()
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        pass


class MockOllamaServer:
    """Lightweight mock Ollama server for testing."""

    def __init__(self) -> None:
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = 0

    def start(self, responses: dict[str, Any] | None = None) -> str:
        MockOllamaHandler.mock_responses = responses or {}
        MockOllamaHandler.request_log = []
        MockOllamaHandler.request_count = 0

        self._server = HTTPServer(("127.0.0.1", 0), MockOllamaHandler)
        self.port = self._server.server_address[1]

        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

        return f"http://127.0.0.1:{self.port}"

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5)
        self._server = None
        self._thread = None

    def get_request_count(self) -> int:
        return MockOllamaHandler.request_count

    def get_request_log(self) -> list[dict[str, Any]]:
        return list(MockOllamaHandler.request_log)

    def clear_log(self) -> None:
        MockOllamaHandler.request_log = []
        MockOllamaHandler.request_count = 0
