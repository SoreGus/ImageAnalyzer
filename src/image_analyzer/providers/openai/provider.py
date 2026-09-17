import base64
import mimetypes
import os
from pathlib import Path
from image_analyzer.config import Settings
from image_analyzer.providers.base import ImageProvider
from image_analyzer.providers.common import comparison_from_dict, description_from_dict, extract_json
from image_analyzer.providers.prompts import COMPARE_PROMPT, DESCRIBE_PROMPT

class OpenAIProvider(ImageProvider):
    def __init__(self, settings: Settings):
        self.settings = settings
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("Run: pip install -e '.[openai]'") from error
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self.client = OpenAI(api_key=key)

    @staticmethod
    def _data_url(path: Path) -> str:
        mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
        return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"

    def _request(self, paths: list[Path], prompt: str) -> str:
        content = [{"type": "input_image", "image_url": self._data_url(path)} for path in paths]
        content.append({"type": "input_text", "text": prompt})
        response = self.client.responses.create(
            model=self.settings.model.name,
            input=[{"role": "user", "content": content}],
        )
        return response.output_text

    def describe(self, image: Path):
        return description_from_dict(extract_json(self._request([image], DESCRIBE_PROMPT)))

    def compare(self, reference: Path, candidate: Path):
        return comparison_from_dict(extract_json(self._request([reference, candidate], COMPARE_PROMPT)))
