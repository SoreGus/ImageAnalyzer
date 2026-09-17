from __future__ import annotations

import argparse
import json
from pathlib import Path

from image_analyzer import ImageAnalyzer

from examples.annotation_app.exporter import (
    export_comparison_bundle,
)


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_REFERENCE = (
    ROOT
    / "annotation_app"
    / "images"
    / "reference_scene.png"
)

DEFAULT_CANDIDATE = (
    ROOT
    / "annotation_app"
    / "images"
    / "candidate_scene.png"
)

DEFAULT_OUTPUT = (
    ROOT
    / "annotation_app"
    / "outputs"
    / "compare"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compare two images and export the "
            "comparison with annotated copies."
        )
    )

    parser.add_argument(
        "reference",
        nargs="?",
        type=Path,
        default=DEFAULT_REFERENCE,
    )

    parser.add_argument(
        "candidate",
        nargs="?",
        type=Path,
        default=DEFAULT_CANDIDATE,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    args = parser.parse_args()

    reference_path = (
        args.reference.resolve()
    )

    candidate_path = (
        args.candidate.resolve()
    )

    output_dir = (
        args.output.resolve()
    )

    analyzer = ImageAnalyzer()

    print("[1/3] Describing reference image...")

    reference_result = analyzer.describe(
        reference_path
    )

    print("[2/3] Describing candidate image...")

    candidate_result = analyzer.describe(
        candidate_path
    )

    print("[3/3] Comparing images...")

    comparison_result = analyzer.compare(
        reference_path,
        candidate_path,
    )

    reference_annotation = json.loads(
        reference_result.to_json()
    )

    candidate_annotation = json.loads(
        candidate_result.to_json()
    )

    comparison = json.loads(
        comparison_result.to_json()
    )

    (
        json_path,
        reference_output,
        candidate_output,
    ) = export_comparison_bundle(
        comparison=comparison,
        reference_annotation=reference_annotation,
        candidate_annotation=candidate_annotation,
        reference_image=reference_path,
        candidate_image=candidate_path,
        destination=output_dir,
    )

    print(f"[OK] Comparison: {json_path}")

    print(
        "[OK] Reference annotated: "
        f"{reference_output}"
    )

    print(
        "[OK] Candidate annotated: "
        f"{candidate_output}"
    )


if __name__ == "__main__":
    main()
    