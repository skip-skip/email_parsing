from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

from backend.app.services.llm.model_config import FALLBACK_CHAIN
from backend.app.services.llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

HEALTH_CHECK_INTERVAL = 300  # 5 minutes


@dataclass
class ModelHealthStatus:
    model: str
    available: bool
    last_checked: datetime | None = None
    last_error: str | None = None


@dataclass
class ModelUsageStats:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    model_counts: dict[str, int] = field(default_factory=dict)
    model_switches: list[dict[str, str]] = field(default_factory=list)


class ModelManager:
    """Manages LLM model selection, fallback chains, and health monitoring.

    Tracks model availability through periodic health checks and
    automatically falls back to the next model in the chain when one
    fails. Records usage statistics and model switch events.
    """

    def __init__(self, client: OllamaClient | None = None) -> None:
        """Initialize the model manager.

        Args:
            client: Ollama client instance. Creates a default client if None.
        """
        self._client = client or OllamaClient()
        self._fallback_chain = list(FALLBACK_CHAIN)
        self._health_status: dict[str, ModelHealthStatus] = {}
        self._usage_stats = ModelUsageStats()
        self._last_health_check: datetime | None = None

    @property
    def fallback_chain(self) -> list[str]:
        return list(self._fallback_chain)

    @property
    def usage_stats(self) -> ModelUsageStats:
        return self._usage_stats

    @property
    def health_status(self) -> dict[str, ModelHealthStatus]:
        return dict(self._health_status)

    @property
    def last_health_check(self) -> datetime | None:
        return self._last_health_check

    def generate_with_fallback(
        self,
        prompt: str,
        system_prompt: str = "",
    ) -> tuple[str, str]:
        """Generate a response using the fallback model chain.

        Tries each model in order. If one fails, logs the failure and
        attempts the next. Returns the response text and the model name
        that produced it.

        Args:
            prompt: The user prompt to send to the model.
            system_prompt: Optional system-level instructions.

        Returns:
            A tuple of (response_text, model_name).

        Raises:
            ConnectionError: If all models in the fallback chain fail.
        """
        last_error: Exception | None = None

        for model in self._fallback_chain:
            try:
                self._usage_stats.total_requests += 1
                response = self._client.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=model,
                )
                self._usage_stats.successful_requests += 1
                self._usage_stats.model_counts[model] = (
                    self._usage_stats.model_counts.get(model, 0) + 1
                )
                return response, model
            except Exception as e:
                last_error = e
                self._usage_stats.failed_requests += 1
                logger.warning(
                    "Model %s failed: %s. Attempting fallback.",
                    model,
                    e,
                )
                if model != self._fallback_chain[-1]:
                    next_index = self._fallback_chain.index(model) + 1
                    next_model = self._fallback_chain[next_index]
                    self._log_model_switch(model, next_model, str(e))

        raise ConnectionError(
            f"All models in fallback chain failed. Last error: {last_error}"
        )

    def _log_model_switch(
        self, from_model: str, to_model: str, reason: str
    ) -> None:
        switch_record = {
            "from_model": from_model,
            "to_model": to_model,
            "reason": reason,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self._usage_stats.model_switches.append(switch_record)
        logger.info(
            "Model switch: %s → %s (reason: %s)",
            from_model,
            to_model,
            reason,
        )

    def check_health(self) -> dict[str, ModelHealthStatus]:
        """Check availability of all models in the fallback chain.

        Queries Ollama for available models and updates the health status
        cache. Returns the current health status of all configured models.
        """
        now = datetime.now(UTC)
        try:
            available_models = self._client.list_models()
        except Exception as e:
            logger.error("Health check failed to reach Ollama: %s", e)
            available_models = []

        for model in self._fallback_chain:
            is_available = any(
                model in m for m in available_models
            )
            self._health_status[model] = ModelHealthStatus(
                model=model,
                available=is_available,
                last_checked=now,
                last_error=None if is_available else "Model not found in Ollama",
            )

        self._last_health_check = now
        return dict(self._health_status)

    def needs_health_check(self) -> bool:
        """Determine if a health check is due based on the interval."""
        if self._last_health_check is None:
            return True
        elapsed = (datetime.now(UTC) - self._last_health_check).total_seconds()
        return elapsed >= HEALTH_CHECK_INTERVAL
