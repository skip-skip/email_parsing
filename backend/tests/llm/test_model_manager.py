from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from backend.app.services.llm.model_config import FALLBACK_CHAIN
from backend.app.services.llm.model_manager import ModelManager


class TestModelManagerGenerateWithFallback:
    def test_success_on_first_model(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = "response from qwen"
        manager = ModelManager(client=mock_client)

        response, model_used = manager.generate_with_fallback("test prompt")

        assert response == "response from qwen"
        assert model_used == FALLBACK_CHAIN[0]
        assert mock_client.generate.call_count == 1

    def test_fallback_to_second_model(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.side_effect = [
            ConnectionError("qwen failed"),
            "response from llama",
        ]
        manager = ModelManager(client=mock_client)

        response, model_used = manager.generate_with_fallback("test prompt")

        assert response == "response from llama"
        assert model_used == FALLBACK_CHAIN[1]
        assert mock_client.generate.call_count == 2

    def test_fallback_to_third_model(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.side_effect = [
            ConnectionError("qwen failed"),
            ConnectionError("llama failed"),
            "response from gemma",
        ]
        manager = ModelManager(client=mock_client)

        response, model_used = manager.generate_with_fallback("test prompt")

        assert response == "response from gemma"
        assert model_used == FALLBACK_CHAIN[2]
        assert mock_client.generate.call_count == 3

    def test_all_models_fail_raises_error(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.side_effect = [
            ConnectionError("qwen failed"),
            ConnectionError("llama failed"),
            ConnectionError("gemma failed"),
        ]
        manager = ModelManager(client=mock_client)

        with pytest.raises(ConnectionError, match="All models in fallback chain failed"):
            manager.generate_with_fallback("test prompt")

        assert mock_client.generate.call_count == 3

    def test_passes_system_prompt(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = "response"
        manager = ModelManager(client=mock_client)

        manager.generate_with_fallback("prompt", system_prompt="system instructions")

        mock_client.generate.assert_called_once_with(
            prompt="prompt",
            system_prompt="system instructions",
            model=FALLBACK_CHAIN[0],
        )

    def test_empty_system_prompt(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = "response"
        manager = ModelManager(client=mock_client)

        manager.generate_with_fallback("prompt")

        mock_client.generate.assert_called_once_with(
            prompt="prompt",
            system_prompt="",
            model=FALLBACK_CHAIN[0],
        )


class TestModelManagerTracking:
    def test_tracks_successful_requests(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = "response"
        manager = ModelManager(client=mock_client)

        manager.generate_with_fallback("prompt 1")
        manager.generate_with_fallback("prompt 2")

        stats = manager.usage_stats
        assert stats.total_requests == 2
        assert stats.successful_requests == 2
        assert stats.failed_requests == 0

    def test_tracks_failed_requests(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.side_effect = ConnectionError("fail")
        manager = ModelManager(client=mock_client)

        with pytest.raises(ConnectionError):
            manager.generate_with_fallback("prompt")

        stats = manager.usage_stats
        assert stats.total_requests == 3
        assert stats.successful_requests == 0
        assert stats.failed_requests == 3

    def test_tracks_model_counts(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = "response"
        manager = ModelManager(client=mock_client)

        manager.generate_with_fallback("prompt 1")
        manager.generate_with_fallback("prompt 2")
        manager.generate_with_fallback("prompt 3")

        stats = manager.usage_stats
        assert stats.model_counts[FALLBACK_CHAIN[0]] == 3

    def test_tracks_model_switches(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.side_effect = [
            ConnectionError("qwen failed"),
            "response from llama",
        ]
        manager = ModelManager(client=mock_client)

        manager.generate_with_fallback("prompt")

        switches = manager.usage_stats.model_switches
        assert len(switches) == 1
        assert switches[0]["from_model"] == FALLBACK_CHAIN[0]
        assert switches[0]["to_model"] == FALLBACK_CHAIN[1]
        assert "timestamp" in switches[0]

    def test_multiple_switches_recorded(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.side_effect = [
            ConnectionError("qwen failed"),
            ConnectionError("llama failed"),
            "response from gemma",
        ]
        manager = ModelManager(client=mock_client)

        manager.generate_with_fallback("prompt")

        switches = manager.usage_stats.model_switches
        assert len(switches) == 2
        assert switches[0]["from_model"] == FALLBACK_CHAIN[0]
        assert switches[0]["to_model"] == FALLBACK_CHAIN[1]
        assert switches[1]["from_model"] == FALLBACK_CHAIN[1]
        assert switches[1]["to_model"] == FALLBACK_CHAIN[2]


class TestModelManagerHealth:
    def test_check_health_returns_status(self) -> None:
        mock_client = MagicMock()
        mock_client.list_models.return_value = ["qwen3:8b", "llama3.3:8b"]
        manager = ModelManager(client=mock_client)

        health = manager.check_health()

        assert len(health) == len(FALLBACK_CHAIN)
        assert health["qwen3:8b"].available is True
        assert health["llama3.3:8b"].available is True
        assert health["gemma3:12b"].available is False

    def test_check_health_with_all_models_available(self) -> None:
        mock_client = MagicMock()
        mock_client.list_models.return_value = [
            "qwen3:8b",
            "llama3.3:8b",
            "gemma3:12b",
        ]
        manager = ModelManager(client=mock_client)

        health = manager.check_health()

        for model in FALLBACK_CHAIN:
            assert health[model].available is True

    def test_check_health_with_no_models(self) -> None:
        mock_client = MagicMock()
        mock_client.list_models.side_effect = ConnectionError("Ollama down")
        manager = ModelManager(client=mock_client)

        health = manager.check_health()

        for model in FALLBACK_CHAIN:
            assert health[model].available is False
            assert health[model].last_error is not None

    def test_check_health_sets_last_checked(self) -> None:
        mock_client = MagicMock()
        mock_client.list_models.return_value = []
        manager = ModelManager(client=mock_client)

        assert manager.last_health_check is None
        manager.check_health()
        assert manager.last_health_check is not None

    def test_needs_health_check_initial(self) -> None:
        mock_client = MagicMock()
        manager = ModelManager(client=mock_client)
        assert manager.needs_health_check() is True

    def test_needs_health_check_after_check(self) -> None:
        mock_client = MagicMock()
        mock_client.list_models.return_value = []
        manager = ModelManager(client=mock_client)

        manager.check_health()
        assert manager.needs_health_check() is False


class TestModelManagerFallbackChain:
    def test_default_fallback_chain(self) -> None:
        mock_client = MagicMock()
        manager = ModelManager(client=mock_client)
        assert manager.fallback_chain == [
            "qwen3:8b",
            "llama3.3:8b",
            "gemma3:12b",
        ]

    def test_fallback_chain_is_copy(self) -> None:
        mock_client = MagicMock()
        manager = ModelManager(client=mock_client)
        chain = manager.fallback_chain
        chain.append("extra:model")
        assert manager.fallback_chain == [
            "qwen3:8b",
            "llama3.3:8b",
            "gemma3:12b",
        ]
