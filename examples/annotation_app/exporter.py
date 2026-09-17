from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
import json

from PIL import Image, ImageDraw, ImageFont

try:
    from .colors import color_for
except ImportError:
    from colors import color_for


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def normalized_box(
    box: dict[str, Any],
) -> tuple[float, float, float, float]:
    x0 = clamp(box.get("x_min", 0.0))
    y0 = clamp(box.get("y_min", 0.0))
    x1 = clamp(box.get("x_max", 1.0))
    y1 = clamp(box.get("y_max", 1.0))

    return (
        min(x0, x1),
        min(y0, y1),
        max(x0, x1),
        max(y0, y1),
    )


def with_colors(
    annotation: dict[str, Any],
) -> dict[str, Any]:
    """Return a copy with a persisted color for every drawable element."""
    result = deepcopy(annotation)
    elements = result.setdefault("elements", [])

    for index, element in enumerate(elements):
        if not isinstance(element, dict):
            continue

        label = str(element.get("label", f"element-{index + 1}"))
        color = element.get("color")

        if not _is_valid_hex_color(color):
            element["color"] = color_for(label, index)

    return result


def build_annotation_payload(
    annotation: dict[str, Any],
    source_image: str | Path,
) -> dict[str, Any]:
    image_path = Path(source_image)

    with Image.open(image_path) as image:
        width, height = image.size

    payload = with_colors(annotation)
    payload["source_image"] = image_path.name
    payload["image_size"] = {
        "width": width,
        "height": height,
    }
    payload["bounding_box_format"] = {
        "coordinates": "normalized",
        "range": [0.0, 1.0],
        "origin": "top-left",
    }

    return payload


def export_json(
    annotation: dict[str, Any],
    source_image: str | Path,
    destination: str | Path,
) -> Path:
    output_path = Path(destination)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = build_annotation_payload(
        annotation,
        source_image,
    )

    _write_json(payload, output_path)

    return output_path


def render_annotated_image(
    source_image: str | Path,
    annotation: dict[str, Any],
    destination: str | Path,
) -> Path:
    """Draw annotations onto a copy without modifying the source image."""
    source_path = Path(source_image)
    output_path = Path(destination)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = with_colors(annotation)

    with Image.open(source_path) as source:
        image = source.convert("RGB").copy()

    draw = ImageDraw.Draw(image)

    width, height = image.size
    stroke = max(2, round(min(width, height) * 0.006))
    font = _font(max(13, round(min(width, height) * 0.025)))

    for index, element in enumerate(payload.get("elements", [])):
        if not isinstance(element, dict):
            continue

        box = element.get("bounding_box")

        if not isinstance(box, dict):
            continue

        x0, y0, x1, y1 = normalized_box(box)

        rect = (
            round(x0 * width),
            round(y0 * height),
            round(x1 * width),
            round(y1 * height),
        )

        label = str(
            element.get(
                "label",
                f"element-{index + 1}",
            )
        )

        color = str(
            element.get("color")
            or color_for(label, index)
        )

        draw.rectangle(
            rect,
            outline=color,
            width=stroke,
        )

        _draw_label(
            draw=draw,
            label=label,
            color=color,
            rect=rect,
            font=font,
        )

    image.save(output_path)

    return output_path


def export_bundle(
    annotation: dict[str, Any],
    source_image: str | Path,
    json_destination: str | Path,
    image_destination: str | Path,
) -> tuple[Path, Path]:
    payload = with_colors(annotation)

    json_path = export_json(
        payload,
        source_image,
        json_destination,
    )

    image_path = render_annotated_image(
        source_image,
        payload,
        image_destination,
    )

    return json_path, image_path


def export_comparison_bundle(
    comparison: dict[str, Any],
    reference_annotation: dict[str, Any],
    candidate_annotation: dict[str, Any],
    reference_image: str | Path,
    candidate_image: str | Path,
    destination: str | Path,
) -> tuple[Path, Path, Path]:
    output_dir = Path(destination)
    output_dir.mkdir(parents=True, exist_ok=True)

    reference_payload = build_annotation_payload(
        reference_annotation,
        reference_image,
    )

    candidate_payload = build_annotation_payload(
        candidate_annotation,
        candidate_image,
    )

    comparison_payload = deepcopy(comparison)
    comparison_payload["reference"] = reference_payload
    comparison_payload["candidate"] = candidate_payload

    json_path = output_dir / "comparison.json"
    reference_output = output_dir / "reference_annotated.png"
    candidate_output = output_dir / "candidate_annotated.png"

    _write_json(
        comparison_payload,
        json_path,
    )

    render_annotated_image(
        reference_image,
        reference_payload,
        reference_output,
    )

    render_annotated_image(
        candidate_image,
        candidate_payload,
        candidate_output,
    )

    return (
        json_path,
        reference_output,
        candidate_output,
    )


def _is_valid_hex_color(value: Any) -> bool:
    if not isinstance(value, str):
        return False

    if len(value) != 7 or not value.startswith("#"):
        return False

    try:
        int(value[1:], 16)
    except ValueError:
        return False

    return True


def _font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(
                candidate,
                size=size,
            )
        except OSError:
            continue

    return ImageFont.load_default()


def _draw_label(
    draw: ImageDraw.ImageDraw,
    label: str,
    color: str,
    rect: tuple[int, int, int, int],
    font: ImageFont.ImageFont,
) -> None:
    bbox = draw.textbbox(
        (0, 0),
        label,
        font=font,
    )

    label_width = bbox[2] - bbox[0] + 12
    label_height = bbox[3] - bbox[1] + 8

    label_x = rect[0]
    label_y = max(
        0,
        rect[1] - label_height,
    )

    draw.rectangle(
        (
            label_x,
            label_y,
            label_x + label_width,
            label_y + label_height,
        ),
        fill=color,
    )

    draw.text(
        (
            label_x + 6,
            label_y + 3,
        ),
        label,
        fill="white",
        font=font,
    )


def _write_json(
    payload: dict[str, Any],
    destination: Path,
) -> None:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    