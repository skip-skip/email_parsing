from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModelConfig:
    model: str
    temperature: float = 0.7
    top_p: float = 0.9
    num_predict: int = 2048


DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")

FALLBACK_CHAIN: list[str] = [
    "qwen3:8b",
    "gemma3:12b",
    "llama3.3:8b",
]

MODEL_CONFIGS: dict[str, ModelConfig] = {
    "qwen3:8b": ModelConfig(model="qwen3:8b", temperature=0.7),
    "gemma3:12b": ModelConfig(model="gemma3:12b", temperature=0.6),
    "llama3.3:8b": ModelConfig(model="llama3.3:8b", temperature=0.7),
}


def get_model_config(model: str | None = None) -> ModelConfig:
    model_name = model or DEFAULT_MODEL
    if model_name in MODEL_CONFIGS:
        return MODEL_CONFIGS[model_name]
    return ModelConfig(model=model_name)


def get_fallback_model() -> str:
    return FALLBACK_CHAIN[0]
