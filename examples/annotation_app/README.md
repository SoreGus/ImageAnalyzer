# Annotation Export App

This example provides a visual inspection and export workflow for `ImageAnalyzer`.

It includes local sample images and annotations so the rendering and export pipeline can be tested without loading a vision model.

## Requirements

The graphical application uses Python's `tkinter`.

### macOS with Homebrew Python

When using Python 3.14 installed through Homebrew, install the matching Tk package:

```bash
brew install python-tk@3.14
```

`tkinter` is a Python system dependency and is therefore not declared in the project's `pyproject.toml`.

You can verify that Tk is available with:

```bash
python -c "import tkinter; print(tkinter.TkVersion)"
```

## Run

From the repository root, activate the project's virtual environment:

```bash
source .venv/bin/activate
```

Then run:

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

The corresponding annotated image contains the same bounding boxes, labels, and colors.

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

The bundled annotations can also be exported without opening the GUI or invoking a vision model:

```bash
python examples/annotation_app/export_samples.py
```

This exports all bundled sample annotations using the same export pipeline as the graphical application.

Because this command does not use `tkinter`, it can also be used in headless environments.