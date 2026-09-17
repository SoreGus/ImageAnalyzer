from __future__ import annotations

from pathlib import Path
import json

try:
    from .exporter import export_bundle
except ImportError:
    from exporter import export_bundle


ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"
ANNOTATIONS = ROOT / "sample_annotations"
OUTPUTS = ROOT / "outputs" / "describe"


def main() -> None:
    for annotation_path in sorted(
        ANNOTATIONS.glob("*.json")
    ):
        payload = json.loads(
            annotation_path.read_text(
                encoding="utf-8"
            )
        )

        source_image = payload.pop(
            "source_image",
            None,
        )

        if not source_image:
            print(
                f"[SKIP] Missing source_image: "
                f"{annotation_path.name}"
            )
            continue

        image_path = (
            IMAGES / str(source_image)
        )

        if not image_path.exists():
            print(
                f"[SKIP] Image not found: "
                f"{image_path.name}"
            )
            continue

        stem = image_path.stem

        json_path, image_output = (
            export_bundle(
                payload,
                image_path,
                OUTPUTS
                / "json"
                / f"{stem}.json",
                OUTPUTS
                / "annotated"
                / f"{stem}_annotated.png",
            )
        )

        print(
            f"[OK] {json_path.relative_to(ROOT)}"
        )

        print(
            f"[OK] {image_output.relative_to(ROOT)}"
        )


if __name__ == "__main__":
    main()
    