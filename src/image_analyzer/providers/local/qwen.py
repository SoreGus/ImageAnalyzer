from pathlib import Path
from image_analyzer.config import Settings
from image_analyzer.providers.base import ImageProvider
from image_analyzer.providers.common import comparison_from_dict, description_from_dict, extract_json
from image_analyzer.providers.prompts import COMPARE_PROMPT, DESCRIBE_PROMPT

class QwenProvider(ImageProvider):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = None
        self.processor = None

    def _load(self):
        if self.model is not None:
            return
        try:
            from transformers import AutoModelForImageTextToText, AutoProcessor
        except ImportError as error:
            raise RuntimeError("Run: pip install -e '.[local]'") from error
        self.processor = AutoProcessor.from_pretrained(
            self.settings.model.name, cache_dir=self.settings.local.model_dir
        )
        self.model = AutoModelForImageTextToText.from_pretrained(
            self.settings.model.name,
            cache_dir=self.settings.local.model_dir,
            torch_dtype="auto",
            device_map="auto",
        )

    def _generate(self, paths: list[Path], prompt: str) -> str:
        self._load()
        from PIL import Image
        images = [Image.open(path).convert("RGB") for path in paths]
        content = [{"type": "image", "image": image} for image in images]
        content.append({"type": "text", "text": prompt})
        messages = [{"role": "user", "content": content}]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=[text], images=images, padding=True, return_tensors="pt")
        inputs = inputs.to(self.model.device)
        output = self.model.generate(**inputs, max_new_tokens=self.settings.generation.max_new_tokens)
        output = output[:, inputs.input_ids.shape[1]:]
        return self.processor.batch_decode(output, skip_special_tokens=True)[0]

    def describe(self, image: Path):
        return description_from_dict(extract_json(self._generate([image], DESCRIBE_PROMPT)))

    def compare(self, reference: Path, candidate: Path):
        return comparison_from_dict(extract_json(self._generate([reference, candidate], COMPARE_PROMPT)))
