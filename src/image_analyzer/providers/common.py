import json
import re
from image_analyzer.types import BoundingBox, ComparisonResult, DescriptionResult, Difference, ImageElement, SpatialRelation

def extract_json(text: str) -> dict:
    text = text.strip()
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {"value": value}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(match.group(0)) if match else {"description": text}

def description_from_dict(data: dict) -> DescriptionResult:
    elements = []
    for item in data.get("elements", []):
        box = None
        raw_box = item.get("bounding_box")
        if isinstance(raw_box, dict):
            try:
                box = BoundingBox(*(float(raw_box[k]) for k in ("x_min", "y_min", "x_max", "y_max")))
            except (KeyError, TypeError, ValueError):
                pass
        elements.append(ImageElement(
            label=str(item.get("label", "")),
            description=str(item.get("description", "")),
            location=str(item.get("location", "")),
            bounding_box=box,
            attributes=item.get("attributes", {}) if isinstance(item.get("attributes"), dict) else {},
        ))
    relations = tuple(SpatialRelation(str(x.get("subject","")), str(x.get("relation","")), str(x.get("object","")))
                      for x in data.get("relations", []) if isinstance(x, dict))
    return DescriptionResult(str(data.get("description", "")), tuple(elements), relations, data)

def comparison_from_dict(data: dict) -> ComparisonResult:
    similarity = data.get("similarity")
    try:
        similarity = float(similarity) if similarity is not None else None
    except (TypeError, ValueError):
        similarity = None
    differences = tuple(Difference(
        kind=str(x.get("kind", "changed")),
        description=str(x.get("description", "")),
        reference_element=x.get("reference_element"),
        candidate_element=x.get("candidate_element"),
    ) for x in data.get("differences", []) if isinstance(x, dict))
    return ComparisonResult(similarity, str(data.get("summary", "")), differences, data)
