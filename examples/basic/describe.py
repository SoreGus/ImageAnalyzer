from __future__ import annotations

import argparse
import json
from pathlib import Path

from image_analyzer import ImageAnalyzer

from examples.annotation_app.exporter import export_bundle


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_IMAGE = (
    ROOT
    / "annotation_app"
    / "images"
    / "reference_scene.png"
)

DEFAULT_OUTPUT = (
    ROOT
    / "annotation_app"
    / "outputs"
    / "describe"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Describe an image and export its JSON "
            "and annotated copy."
        )
    )

    parser.add_argument(
        "image",
        nargs="?",
        type=Path,
        default=DEFAULT_IMAGE,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    args = parser.parse_args()

    image_path = args.image.resolve()
    output_dir = args.output.resolve()

    analyzer = ImageAnalyzer()

    result = analyzer.describe(
        image_path
    )

    annotation = json.loads(
        result.to_json()
    )

    stem = image_path.stem

    json_path, annotated_path = (
        export_bundle(
            annotation,
            image_path,
            output_dir
            / "json"
            / f"{stem}.json",
            output_dir
            / "annotated"
            / f"{stem}_annotated.png",
        )
    )

    print(f"[OK] JSON: {json_path}")
    print(
        f"[OK] Annotated image: "
        f"{annotated_path}"
    )


if __name__ == "__main__":
    main()
    