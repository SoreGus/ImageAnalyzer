# Annotation Export App

This example provides a visual inspection and export workflow for `ImageAnalyzer`.

It includes local sample images and annotations so the rendering and export pipeline can be tested without loading a vision model.

## Run

From the repository root:

```bash
python examples/annotation_app/app.py
```

The bundled annotations are loaded immediately.

Use **Analyze Current** to run the configured `ImageAnalyzer` provider on the selected image.

## Describe Outputs

Describe exports are written to:

```text
outputs/describe/
├── json/
└── annotated/
```

Each JSON file contains:

- the image description;
- detected elements;
- normalized bounding boxes;
- a persisted color for each drawable element;
- spatial relations;
- source image metadata;
- image dimensions;
- bounding-box coordinate metadata.

Example:

```json
{
  "label": "sofa",
  "color": "#1E88E5",
  "bounding_box": {
    "x_min": 0.10,
    "y_min": 0.42,
    "x_max": 0.62,
    "y_max": 0.82
  }
}
```

The corresponding annotated image contains the same bounding boxes, labels and colors.

Original files under `images/` are never modified.

## Compare Outputs

The comparison example writes:

```text
outputs/compare/
├── comparison.json
├── reference_annotated.png
└── candidate_annotated.png
```

`comparison.json` contains the semantic comparison together with the reference and candidate image analyses.

## Headless Sample Export

Run:

```bash
python examples/annotation_app/export_samples.py
```

This exports all bundled sample annotations without opening the GUI or invoking a vision model.