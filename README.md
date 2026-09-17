# ImageAnalyzer

Python 3.14 library for provider-independent image description and image comparison.

## Capabilities

- `describe(image)`: detailed scene description, detected elements, approximate normalized bounding boxes, attributes and spatial relationships.
- `compare(reference, candidate)`: image similarity and identification of missing, added, changed and moved elements.
- Local and OpenAI providers behind the same public API.
- JSON-serializable structured results.
- Visual examples with bounding-box and annotation export.

## Setup

Create the local environment file:

```bash
cp .env.example .env
```

Install ImageAnalyzer and all supported provider dependencies:

```bash
make
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Bootstrap the configured provider:

```bash
image-analyzer bootstrap
```

Validate the environment:

```bash
image-analyzer doctor
```

Edit `config/settings.yaml` to select the provider and model.

Example local configuration:

```yaml
model:
  provider: local
  name: Qwen/Qwen3-VL-4B-Instruct
```

Example OpenAI configuration:

```yaml
model:
  provider: openai
  name: YOUR_OPENAI_VISION_MODEL
```

For OpenAI, set `OPENAI_API_KEY` in `.env`.

### Deactivate the virtual environment

When finished:

```bash
deactivate
```

## Usage

```python
from image_analyzer import ImageAnalyzer

analyzer = ImageAnalyzer()

description = analyzer.describe("image.jpg")
print(description.to_json())

comparison = analyzer.compare(
    "reference.jpg",
    "candidate.jpg",
)
print(comparison.to_json())
```

## Examples

The repository includes sample images, visual annotation tools and export workflows.

### Describe

Run with the bundled sample image:

```bash
python examples/basic/describe.py
```

Or provide your own image:

```bash
python examples/basic/describe.py path/to/image.png
```

### Compare

Run with the bundled reference and candidate images:

```bash
python examples/basic/compare.py
```

Or provide your own images:

```bash
python examples/basic/compare.py \
  path/to/reference.png \
  path/to/candidate.png
```

### Annotation App

Run the visual annotation and export example:

```bash
python examples/annotation_app/app.py
```

It can preview bounding boxes, run the configured analyzer and export JSON and annotated image copies without modifying the originals.

See `examples/README.md` for more details.

## Local Model

The initial local configuration targets:

```text
Qwen/Qwen3-VL-4B-Instruct
```

The local runtime uses the provider abstraction, so the public `ImageAnalyzer` API does not depend on the underlying model.

## OpenAI

OpenAI uses the same public API.

Provider and model selection are configured through `config/settings.yaml`, while `OPENAI_API_KEY` is read from `.env`.

No OpenAI model is hard-coded into the library.

## Development

ImageAnalyzer is installed in editable mode by `make`.

To rebuild the environment from scratch:

```bash
make clean
make
```

Then activate it again:

```bash
source .venv/bin/activate
```

No tests are included at this stage.