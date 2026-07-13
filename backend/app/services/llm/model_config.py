from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    model: str
    temperature: float = 0.7
    top_p: float = 0.9
    num_predict: int = 2048


DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")

FALLBACK_CHAIN: list[str] = [
    "gemma3:4b",
    "qwen3:1.7b",
    "llama3.2:3b",
]

MODEL_CONFIGS: dict[str, ModelConfig] = {
    "gemma3:4b": ModelConfig(model="gemma3:4b", temperature=0.6),
    "qwen3:1.7b": ModelConfig(model="qwen3:1.7b", temperature=0.7),
    "llama3.2:3b": ModelConfig(model="llama3.2:3b", temperature=0.7),
    "qwen3:8b": ModelConfig(model="qwen3:8b", temperature=0.7),
}


def get_model_config(model: str | None = None) -> ModelConfig:
    model_name = model or DEFAULT_MODEL
    if model_name in MODEL_CONFIGS:
        return MODEL_CONFIGS[model_name]
    return ModelConfig(model=model_name)


def get_fallback_model() -> str:
    return FALLBACK_CHAIN[0]
