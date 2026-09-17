import base64
import mimetypes
import os
from pathlib import Path

from image_analyzer.config import Settings
from image_analyzer.providers.base import ImageProvider
from image_analyzer.providers.common import (
    comparison_from_dict,
    description_from_dict,
    extract_json,
)
from image_analyzer.providers.prompts import (
    COMPARE_PROMPT,
    DESCRIBE_PROMPT,
)


GPT_5_NANO_INPUT_COST_PER_MILLION = 0.05
GPT_5_NANO_OUTPUT_COST_PER_MILLION = 0.40


class OpenAIProvider(ImageProvider):
    def __init__(
        self,
        settings: Settings,
    ):
        self.settings = settings

        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError(
                "Run: pip install -e '.[openai]'"
            ) from error

        key = os.getenv(
            "OPENAI_API_KEY"
        )

        if not key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured"
            )

        self.client = OpenAI(
            api_key=key
        )

    @staticmethod
    def _data_url(
        path: Path,
    ) -> str:
        mime = (
            mimetypes.guess_type(
                path.name
            )[0]
            or "image/jpeg"
        )

        encoded = base64.b64encode(
            path.read_bytes()
        ).decode(
            "ascii"
        )

        return (
            f"data:{mime};base64,"
            f"{encoded}"
        )

    def _request(
        self,
        paths: list[Path],
        prompt: str,
    ) -> str:
        content = [
            {
                "type": "input_image",
                "image_url": self._data_url(
                    path
                ),
            }
            for path in paths
        ]

        content.append(
            {
                "type": "input_text",
                "text": prompt,
            }
        )

        response = (
            self.client.responses.create(
                model=self.settings.model.name,
                input=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
            )
        )

        self._print_usage(
            response
        )

        return response.output_text

    def _print_usage(
        self,
        response,
    ) -> None:
        usage = getattr(
            response,
            "usage",
            None,
        )

        if usage is None:
            print(
                "OpenAI usage unavailable"
            )
            return

        input_tokens = int(
            getattr(
                usage,
                "input_tokens",
                0,
            )
            or 0
        )

        output_tokens = int(
            getattr(
                usage,
                "output_tokens",
                0,
            )
            or 0
        )

        total_tokens = int(
            getattr(
                usage,
                "total_tokens",
                (
                    input_tokens
                    + output_tokens
                ),
            )
            or 0
        )

        print()
        print("=== OpenAI usage ===")
        print(
            "Model:",
            self.settings.model.name,
        )
        print(
            "Input tokens:",
            input_tokens,
        )
        print(
            "Output tokens:",
            output_tokens,
        )
        print(
            "Total tokens:",
            total_tokens,
        )

        if (
            self.settings.model.name
            == "gpt-5-nano"
        ):
            input_cost = (
                input_tokens
                / 1_000_000
                * GPT_5_NANO_INPUT_COST_PER_MILLION
            )

            output_cost = (
                output_tokens
                / 1_000_000
                * GPT_5_NANO_OUTPUT_COST_PER_MILLION
            )

            total_cost = (
                input_cost
                + output_cost
            )

            print(
                "Estimated input cost:",
                f"${input_cost:.8f}",
            )
            print(
                "Estimated output cost:",
                f"${output_cost:.8f}",
            )
            print(
                "Estimated total cost:",
                f"${total_cost:.8f}",
            )

        print("====================")
        print()

    def describe(
        self,
        image: Path,
    ):
        return description_from_dict(
            extract_json(
                self._request(
                    [image],
                    DESCRIBE_PROMPT,
                )
            )
        )

    def compare(
        self,
        reference: Path,
        candidate: Path,
    ):
        return comparison_from_dict(
            extract_json(
                self._request(
                    [
                        reference,
                        candidate,
                    ],
                    COMPARE_PROMPT,
                )
            )
        )