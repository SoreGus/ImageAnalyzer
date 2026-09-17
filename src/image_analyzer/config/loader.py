from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import os
import yaml

@dataclass(frozen=True, slots=True)
class ModelSettings:
    provider: str
    name: str

@dataclass(frozen=True, slots=True)
class LocalSettings:
    backend: str = "transformers"
    device: str = "mps"
    model_dir: str = ".models"

@dataclass(frozen=True, slots=True)
class GenerationSettings:
    max_new_tokens: int = 2048
    temperature: float = 0.1

@dataclass(frozen=True, slots=True)
class Settings:
    model: ModelSettings
    local: LocalSettings
    generation: GenerationSettings

def project_root() -> Path:
    current = Path.cwd()
    for path in (current, *current.parents):
        if (path / "pyproject.toml").exists():
            return path
    return current

def load_settings(path: str | Path | None = None) -> Settings:
    root = project_root()
    load_dotenv(root / ".env")
    source = Path(path) if path else root / "config" / "settings.yaml"
    data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    model = data.get("model", {})
    local = data.get("local", {})
    generation = data.get("generation", {})
    name = os.getenv("IMAGE_ANALYZER_MODEL", model.get("name", ""))
    if not name:
        raise ValueError("model.name is required")
    return Settings(
        model=ModelSettings(
            provider=os.getenv("IMAGE_ANALYZER_PROVIDER", model.get("provider", "local")),
            name=name,
        ),
        local=LocalSettings(
            backend=local.get("backend", "transformers"),
            device=local.get("device", "mps"),
            model_dir=local.get("model_dir", ".models"),
        ),
        generation=GenerationSettings(
            max_new_tokens=int(generation.get("max_new_tokens", 2048)),
            temperature=float(generation.get("temperature", 0.1)),
        ),
    )
