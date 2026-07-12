from __future__ import annotations

from collections.abc import Generator

import pytest

from backend.app.services.llm.ollama_client import OllamaClient
from backend.tests.llm.mock_ollama import MockOllamaServer


@pytest.fixture
def mock_server() -> Generator[MockOllamaServer, None, None]:
    server = MockOllamaServer()
    yield server
    server.stop()


class TestOllamaClientGenerate:
    def test_successful_generation(self, mock_server: MockOllamaServer) -> None:
        base_url = mock_server.start({"generate": "Hello from the model"})
        client = OllamaClient(base_url=base_url, timeout=5)

        result = client.generate("Say hello", model="qwen3:8b")

        assert result == "Hello from the model"

    def test_generation_with_system_prompt(
        self, mock_server: MockOllamaServer
    ) -> None:
        base_url = mock_server.start({"generate": "response"})
        client = OllamaClient(base_url=base_url, timeout=5)

        client.generate("test prompt", system_prompt="Be helpful", model="qwen3:8b")

        requests = mock_server.get_request_log()
        assert len(requests) == 1
        assert requests[0]["system"] == "Be helpful"
        assert requests[0]["prompt"] == "test prompt"
        assert requests[0]["model"] == "qwen3:8b"

    def test_generation_empty_response(self, mock_server: MockOllamaServer) -> None:
        base_url = mock_server.start({"generate": ""})
        client = OllamaClient(base_url=base_url, timeout=5)

        result = client.generate("test", model="qwen3:8b")

        assert result == ""

    def test_generation_payload_includes_model_config(
        self, mock_server: MockOllamaServer
    ) -> None:
        base_url = mock_server.start({"generate": "ok"})
        client = OllamaClient(base_url=base_url, timeout=5)

        client.generate("test", model="qwen3:8b")

        requests = mock_server.get_request_log()
        assert requests[0]["model"] == "qwen3:8b"
        assert requests[0]["stream"] is False
        assert "options" in requests[0]

    def test_generation_uses_default_model(
        self, mock_server: MockOllamaServer
    ) -> None:
        base_url = mock_server.start({"generate": "ok"})
        client = OllamaClient(base_url=base_url, timeout=5)

        client.generate("test")

        requests = mock_server.get_request_log()
        assert requests[0]["model"] == "qwen3:8b"


class TestOllamaClientRetryLogic:
    def test_retries_on_server_error(self, mock_server: MockOllamaServer) -> None:
        call_count = 0

        def flaky_error(request_data: dict) -> tuple[int, str] | None:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return (503, "Service unavailable")
            return None

        base_url = mock_server.start({"error": flaky_error, "generate": "ok"})
        client = OllamaClient(base_url=base_url, timeout=5)

        result = client.generate("test", model="qwen3:8b")

        assert result == "ok"
        assert mock_server.get_request_count() == 3

    def test_retries_on_connection_error(self, mock_server: MockOllamaServer) -> None:
        base_url = mock_server.start(
            {"error": {"code": 503, "message": "Service unavailable"}}
        )
        client = OllamaClient(base_url=base_url, timeout=5)

        with pytest.raises(ConnectionError, match="Failed to connect to Ollama"):
            client.generate("test", model="qwen3:8b")

        assert mock_server.get_request_count() == 3

    def test_retries_on_http_status_error(
        self, mock_server: MockOllamaServer
    ) -> None:
        base_url = mock_server.start(
            {"error": {"code": 500, "message": "Internal error"}}
        )
        client = OllamaClient(base_url=base_url, timeout=5)

        with pytest.raises(ConnectionError, match="Failed to connect to Ollama"):
            client.generate("test", model="qwen3:8b")

        assert mock_server.get_request_count() == 3

    def test_succeeds_on_second_attempt(self) -> None:
        attempt = 0

        def handler(request_data: dict) -> tuple[int, str] | None:
            nonlocal attempt
            attempt += 1
            if attempt == 1:
                return (500, "Internal error")
            return None

        server = MockOllamaServer()
        base_url = server.start({"error": handler, "generate": "ok"})
        client = OllamaClient(base_url=base_url, timeout=5)

        try:
            result = client.generate("test", model="qwen3:8b")
            assert result == "ok"
            assert attempt == 2
        finally:
            server.stop()

    def test_no_retry_on_success(self, mock_server: MockOllamaServer) -> None:
        base_url = mock_server.start({"generate": "ok"})
        client = OllamaClient(base_url=base_url, timeout=5)

        client.generate("test", model="qwen3:8b")

        assert mock_server.get_request_count() == 1


class TestOllamaClientTimeoutHandling:
    def test_timeout_raises_connection_error(
        self, mock_server: MockOllamaServer
    ) -> None:
        base_url = mock_server.start({"delay": 10, "generate": "slow"})
        client = OllamaClient(base_url=base_url, timeout=1)

        with pytest.raises(ConnectionError, match="Failed to connect to Ollama"):
            client.generate("test", model="qwen3:8b")

    def test_fast_response_within_timeout(
        self, mock_server: MockOllamaServer
    ) -> None:
        base_url = mock_server.start({"generate": "fast response"})
        client = OllamaClient(base_url=base_url, timeout=5)

        result = client.generate("test", model="qwen3:8b")
        assert result == "fast response"


class TestOllamaClientJsonParsing:
    def test_parse_plain_json(self) -> None:
        client = OllamaClient(base_url="http://localhost:1", timeout=1)
        result = client._parse_json('{"key": "value", "num": 42}')
        assert result == {"key": "value", "num": 42}

    def test_parse_json_with_markdown_fence(self) -> None:
        client = OllamaClient(base_url="http://localhost:1", timeout=1)
        text = 'Here is the result:\n```json\n{"task": "test"}\n```\nDone.'
        result = client._parse_json(text)
        assert result == {"task": "test"}

    def test_parse_json_with_generic_fence(self) -> None:
        client = OllamaClient(base_url="http://localhost:1", timeout=1)
        text = '```\n{"task": "test"}\n```'
        result = client._parse_json(text)
        assert result == {"task": "test"}

    def test_parse_json_with_surrounding_text(self) -> None:
        client = OllamaClient(base_url="http://localhost:1", timeout=1)
        text = 'Sure, here is the JSON:\n{"client": "Acme", "hours": 5}\nHope that helps!'
        result = client._parse_json(text)
        assert result == {"client": "Acme", "hours": 5}

    def test_parse_invalid_json_returns_none(self) -> None:
        client = OllamaClient(base_url="http://localhost:1", timeout=1)
        result = client._parse_json("This is not JSON at all")
        assert result is None

    def test_parse_non_dict_json_returns_none(self) -> None:
        client = OllamaClient(base_url="http://localhost:1", timeout=1)
        result = client._parse_json('[1, 2, 3]')
        assert result is None

    def test_parse_empty_string_returns_none(self) -> None:
        client = OllamaClient(base_url="http://localhost:1", timeout=1)
        result = client._parse_json("")
        assert result is None

    def test_parse_json_incomplete_fence(self) -> None:
        client = OllamaClient(base_url="http://localhost:1", timeout=1)
        text = '```json\n{"task": "test"}\n'
        result = client._parse_json(text)
        assert result == {"task": "test"}


class TestOllamaClientGenerateJson:
    def test_generate_json_parses_valid_json(
        self, mock_server: MockOllamaServer
    ) -> None:
        base_url = mock_server.start({"generate": '{"task": "review PR"}'})
        client = OllamaClient(base_url=base_url, timeout=5)

        result = client.generate_json("Extract task", model="qwen3:8b")

        assert result == {"task": "review PR"}

    def test_generate_json_retries_on_invalid_json(
        self, mock_server: MockOllamaServer
    ) -> None:
        call_count = 0

        def handler(request_data: dict) -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "Sorry, I can't parse that"
            return '{"result": "parsed"}'

        base_url = mock_server.start({"generate": handler})
        client = OllamaClient(base_url=base_url, timeout=5)

        result = client.generate_json("Extract task", model="qwen3:8b")

        assert result == {"result": "parsed"}
        assert mock_server.get_request_count() == 2

    def test_generate_json_fails_after_retries(
        self, mock_server: MockOllamaServer
    ) -> None:
        base_url = mock_server.start({"generate": "not json at all"})
        client = OllamaClient(base_url=base_url, timeout=5)

        with pytest.raises(ValueError, match="Failed to parse JSON"):
            client.generate_json("Extract task", model="qwen3:8b")

    def test_generate_json_extracts_from_markdown(
        self, mock_server: MockOllamaServer
    ) -> None:
        response = 'Here is the JSON:\n```json\n{"client": "Acme"}\n```'
        base_url = mock_server.start({"generate": response})
        client = OllamaClient(base_url=base_url, timeout=5)

        result = client.generate_json("Extract", model="qwen3:8b")

        assert result == {"client": "Acme"}

    def test_generate_json_with_system_prompt(
        self, mock_server: MockOllamaServer
    ) -> None:
        base_url = mock_server.start({"generate": '{"ok": true}'})
        client = OllamaClient(base_url=base_url, timeout=5)

        client.generate_json(
            "Extract", system_prompt="You are a JSON extractor", model="qwen3:8b"
        )

        requests = mock_server.get_request_log()
        assert requests[0]["system"] == "You are a JSON extractor"


class TestOllamaClientListModels:
    def test_list_models(self, mock_server: MockOllamaServer) -> None:
        base_url = mock_server.start(
            {
                "tags": {
                    "models": [
                        {"name": "qwen3:8b"},
                        {"name": "llama3.3:8b"},
                        {"name": "gemma3:12b"},
                    ]
                }
            }
        )
        client = OllamaClient(base_url=base_url, timeout=5)

        models = client.list_models()

        assert models == ["qwen3:8b", "llama3.3:8b", "gemma3:12b"]

    def test_list_models_empty(self, mock_server: MockOllamaServer) -> None:
        base_url = mock_server.start({"tags": {"models": []}})
        client = OllamaClient(base_url=base_url, timeout=5)

        models = client.list_models()

        assert models == []

    def test_list_models_skips_entries_without_name(
        self, mock_server: MockOllamaServer
    ) -> None:
        base_url = mock_server.start(
            {"tags": {"models": [{"name": "qwen3:8b"}, {"name": ""}]}}
        )
        client = OllamaClient(base_url=base_url, timeout=5)

        models = client.list_models()

        assert models == ["qwen3:8b"]

    def test_list_models_server_error(self, mock_server: MockOllamaServer) -> None:
        base_url = mock_server.start(
            {"tags_error": {"code": 500, "message": "Internal error"}}
        )
        client = OllamaClient(base_url=base_url, timeout=5)

        with pytest.raises(ConnectionError, match="Failed to connect to Ollama"):
            client.list_models()


class TestOllamaClientConstructor:
    def test_custom_base_url(self) -> None:
        client = OllamaClient(base_url="http://custom:9999", timeout=10)
        assert client._base_url == "http://custom:9999"
        assert client._timeout == 10

    def test_strips_trailing_slash(self) -> None:
        client = OllamaClient(base_url="http://localhost:11434/")
        assert client._base_url == "http://localhost:11434"

    def test_default_timeout(self) -> None:
        client = OllamaClient(base_url="http://localhost:1")
        assert client._timeout == 60


class TestOllamaClientWithCallableMock:
    def test_callable_generate_response(self) -> None:
        def responder(request_data: dict) -> str:
            prompt = request_data.get("prompt", "")
            return f"Echo: {prompt}"

        server = MockOllamaServer()
        base_url = server.start({"generate": responder})
        client = OllamaClient(base_url=base_url, timeout=5)

        try:
            result = client.generate("hello world", model="qwen3:8b")
            assert result == "Echo: hello world"
        finally:
            server.stop()
