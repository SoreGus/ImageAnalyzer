# ImageAnalyzer

Python 3.14 library for provider-independent image description and image comparison.

## Capabilities

- `describe(image)`: detailed scene description, detected elements, approximate normalized bounding boxes, attributes and spatial relationships.
- `compare(reference, candidate)`: image similarity and identification of missing, added, changed and moved elements.
- Local and OpenAI providers behind the same public API.
- JSON-serializable structured results.
- Provider-independent model selection through configuration.

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

## Configuration

Provider and model selection are configured in:

```text
config/settings.yaml
```

### Local provider

```yaml
model:
  provider: local
  name: Qwen/Qwen3-VL-4B-Instruct

local:
  backend: transformers
  device: mps
  model_dir: .models

generation:
  max_new_tokens: 2048
  temperature: 0.1
```

The local provider uses Hugging Face Transformers.

On Apple Silicon, `mps` can be used to run supported model workloads on the GPU.

### OpenAI provider

```yaml
model:
  provider: openai
  name: gpt-5-nano

local:
  backend: transformers
  device: mps
  model_dir: .models

generation:
  max_new_tokens: 2048
  temperature: 0.1
```

For OpenAI, configure the API key in `.env`:

```text
OPENAI_API_KEY=your_api_key
```

No provider-specific model is hard-coded into the public `ImageAnalyzer` API.

## Usage

```python
from image_analyzer import ImageAnalyzer

analyzer = ImageAnalyzer()

description = analyzer.describe(
    "image.jpg"
)

print(
    description.to_json()
)
```

Image comparison uses the same analyzer instance:

```python
comparison = analyzer.compare(
    "reference.jpg",
    "candidate.jpg",
)

print(
    comparison.to_json()
)
```

## Describe

`describe(image)` analyzes a single image and returns structured information including:

- overall scene description;
- visible elements;
- approximate normalized bounding boxes;
- human-readable locations;
- visual attributes;
- spatial and semantic relationships.

Bounding-box coordinates are normalized from `0.0` to `1.0` with the origin at the top-left.

## Compare

`compare(reference, candidate)` compares two images and returns structured information including:

- overall similarity;
- comparison summary;
- missing elements;
- added elements;
- changed elements;
- moved elements;
- appearance differences.

The reference image represents the expected or original state, while the candidate image represents the image being evaluated.

## Providers

ImageAnalyzer exposes the same public API regardless of the configured provider.

The current providers are:

- `local`
- `openai`

Provider selection is performed through `config/settings.yaml`.

Application code does not need to change when switching providers.

## Local Runtime

The current local model is:

```text
Qwen/Qwen3-VL-4B-Instruct
```

The local provider loads the model through Transformers and automatically initializes it when required.

Model files are stored in the configured local model directory:

```text
.models
```

The runtime may distribute model components across available devices depending on hardware and memory availability.

## OpenAI

The current OpenAI model is:

```text
gpt-5-nano
```

The OpenAI provider uses the same `describe()` and `compare()` interfaces as the local provider.

Authentication is performed through:

```text
OPENAI_API_KEY
```

The API key is read from the environment and is not stored in source code.

## CLI

Bootstrap the configured environment:

```bash
image-analyzer bootstrap
```

Validate the current setup:

```bash
image-analyzer doctor
```

These commands use the provider selected in `config/settings.yaml`.

## Development

ImageAnalyzer is installed in editable mode by `make`.

To rebuild the environment from scratch:

```bash
make clean
make
```

Activate the environment again:

```bash
source .venv/bin/activate
```

When finished:

```bash
deactivate
```