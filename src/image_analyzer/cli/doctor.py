import importlib.util
import os
import sys
from image_analyzer.config import load_settings

def run_doctor() -> int:
    healthy = sys.version_info[:2] == (3, 14)
    print(f"[{'OK' if healthy else 'ERROR'}] Python: {sys.version.split()[0]}")
    in_venv = sys.prefix != sys.base_prefix
    print(f"[{'OK' if in_venv else 'ERROR'}] Virtual environment: {sys.prefix}")
    healthy &= in_venv
    try:
        settings = load_settings()
    except Exception as error:
        print(f"[ERROR] Configuration: {error}")
        return 1
    provider = settings.model.provider.lower()
    print(f"[OK] Provider: {provider}")
    print(f"[OK] Model: {settings.model.name}")
    if provider == "openai":
        package = importlib.util.find_spec("openai") is not None
        key = bool(os.getenv("OPENAI_API_KEY"))
        print(f"[{'OK' if package else 'ERROR'}] OpenAI package")
        print(f"[{'OK' if key else 'ERROR'}] OPENAI_API_KEY")
        healthy &= package and key
    elif provider == "local":
        transformers = importlib.util.find_spec("transformers") is not None
        torch = importlib.util.find_spec("torch") is not None
        print(f"[{'OK' if transformers else 'ERROR'}] Transformers")
        print(f"[{'OK' if torch else 'ERROR'}] PyTorch")
        healthy &= transformers and torch
    else:
        print(f"[ERROR] Unsupported provider: {provider}")
        healthy = False
    return 0 if healthy else 1
