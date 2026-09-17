# Examples

The examples demonstrate the two main `ImageAnalyzer` operations:

- `describe(image)`
- `compare(reference, candidate)`

They also provide visual bounding-box inspection and JSON export.

## Describe

From the repository root:

```bash
python examples/basic/describe.py
```

The bundled reference image is used by default.

A custom image can also be provided:

```bash
python examples/basic/describe.py path/to/image.png
```

Outputs are written to:

```text
examples/annotation_app/outputs/describe/
├── json/
└── annotated/
```

## Compare

Run:

```bash
python examples/basic/compare.py
```

The bundled reference and candidate images are used by default.

Custom images can also be provided:

```bash
python examples/basic/compare.py \
  path/to/reference.png \
  path/to/candidate.png
```

Outputs are written to:

```text
examples/annotation_app/outputs/compare/
├── comparison.json
├── reference_annotated.png
└── candidate_annotated.png
```

The comparison pipeline performs:

```text
reference ──> describe ──┐
                         │
candidate ──> describe ──┼──> export
                         │
reference + candidate ──> compare
```

This allows the comparison result to be inspected together with bounding boxes for both images.

## Annotation Export App

A small Tk/Pillow application is included for visual inspection.

Run:

```bash
python examples/annotation_app/app.py
```

It can:

- preview bundled images;
- display bounding boxes and labels;
- assign and persist colors for detected elements;
- analyze an image using the configured `ImageAnalyzer`;
- export JSON;
- export annotated image copies;
- export all bundled sample annotations.

Original images are never modified.

## Headless Export

To verify the rendering and export pipeline without loading a model:

```bash
python examples/annotation_app/export_samples.py
```

Generated files are stored under:

```text
examples/annotation_app/outputs/
```