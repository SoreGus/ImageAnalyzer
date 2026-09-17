from pathlib import Path
from image_analyzer.config import Settings, load_settings

class ImageAnalyzer:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()
        self.provider = self._make_provider()

    def _make_provider(self):
        provider = self.settings.model.provider.lower()
        if provider == "local":
            from image_analyzer.providers.local.qwen import QwenProvider
            return QwenProvider(self.settings)
        if provider == "openai":
            from image_analyzer.providers.openai.provider import OpenAIProvider
            return OpenAIProvider(self.settings)
        raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def _path(value) -> Path:
        path = Path(value).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return path

    def describe(self, image):
        return self.provider.describe(self._path(image))

    def compare(self, reference, candidate):
        return self.provider.compare(self._path(reference), self._path(candidate))
