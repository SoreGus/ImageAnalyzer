import os
import sys
from image_analyzer.config import load_settings

def run_bootstrap() -> int:
    if sys.version_info[:2] != (3, 14):
        print(f"[ERROR] Python 3.14 required; running {sys.version.split()[0]}")
        return 1
    try:
        settings = load_settings()
    except Exception as error:
        print(f"[ERROR] Configuration: {error}")
        return 1
    provider = settings.model.provider.lower()
    print(f"[OK] Provider: {provider}")
    print(f"[OK] Model: {settings.model.name}")

    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            print("[ERROR] OPENAI_API_KEY is missing")
            return 1
        try:
            import openai
        except ImportError:
            print("[ERROR] Run: pip install -e '.[openai]'")
            return 1
        print("[OK] OpenAI environment ready")
        return 0

    if provider == "local":
        try:
            from transformers import AutoModelForImageTextToText, AutoProcessor
        except ImportError:
            print("[ERROR] Run: pip install -e '.[local]'")
            return 1
        print("[INFO] Preparing local model; missing files will be downloaded...")
        try:
            AutoProcessor.from_pretrained(settings.model.name, cache_dir=settings.local.model_dir)
            AutoModelForImageTextToText.from_pretrained(
                settings.model.name,
                cache_dir=settings.local.model_dir,
                torch_dtype="auto",
            )
        except Exception as error:
            print(f"[ERROR] Model preparation failed: {error}")
            return 1
        print("[OK] Local model available")
        return 0

    print(f"[ERROR] Unsupported provider: {provider}")
    return 1
