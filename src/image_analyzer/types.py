from __future__ import annotations
from dataclasses import asdict, dataclass, field
import json
from typing import Any

@dataclass(frozen=True, slots=True)
class BoundingBox:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

@dataclass(frozen=True, slots=True)
class ImageElement:
    label: str
    description: str = ""
    location: str = ""
    bounding_box: BoundingBox | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class SpatialRelation:
    subject: str
    relation: str
    object: str

@dataclass(frozen=True, slots=True)
class DescriptionResult:
    description: str
    elements: tuple[ImageElement, ...] = ()
    relations: tuple[SpatialRelation, ...] = ()
    raw: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

@dataclass(frozen=True, slots=True)
class Difference:
    kind: str
    description: str
    reference_element: str | None = None
    candidate_element: str | None = None

@dataclass(frozen=True, slots=True)
class ComparisonResult:
    similarity: float | None
    summary: str
    differences: tuple[Difference, ...] = ()
    raw: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)
