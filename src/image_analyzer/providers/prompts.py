DESCRIBE_PROMPT = """
Analyze this image carefully and return ONLY valid JSON.

{
  "description": "detailed overall description",
  "elements": [{
    "label": "stable name",
    "description": "visual description",
    "location": "human-readable position",
    "bounding_box": {"x_min": 0.0, "y_min": 0.0, "x_max": 1.0, "y_max": 1.0},
    "attributes": {}
  }],
  "relations": [{"subject": "label", "relation": "relationship", "object": "label"}]
}

Bounding boxes use normalized coordinates from 0 to 1, origin at top-left.
Include only visually supported information.
""".strip()

COMPARE_PROMPT = """
Compare the two images carefully. First = REFERENCE, second = CANDIDATE.
Return ONLY valid JSON.

{
  "similarity": 0.0,
  "summary": "overall comparison",
  "differences": [{
    "kind": "missing|added|changed|moved|appearance",
    "description": "difference in candidate relative to reference",
    "reference_element": null,
    "candidate_element": null
  }]
}

Similarity must be between 0 and 1. Compare semantic content, layout, geometry,
object presence, position, proportions, colors/materials and meaningful visual changes.
""".strip()
