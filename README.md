# convert

[![CI](https://github.com/Aldo-f/convert/actions/workflows/ci.yml/badge.svg)](https://github.com/Aldo-f/convert/actions)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Universal type-x to type-y converter. Lightweight, modular CLI tool for converting between document formats.

## Install

### Quick Start

```bash
pip install convert-cli
convert --help
```

Requires Python 3.12+.

### Development Install

```bash
git clone https://github.com/Aldo-f/convert.git
cd convert
pip install -e .
```

> **Note on the `convert` command name:** ImageMagick also provides `/usr/bin/convert`, which takes precedence on most `PATH`s. To use this project's CLI, run the full path or adjust `PATH`:
> ```bash
> /home/aldo/hermes/bin/convert ...
> # or
> PATH=/home/aldo/hermes/bin:$PATH convert ...
> # or
> python -m convert.cli ...
> ```

## Usage

```bash
# Convert Markdown to DOCX (auto-detects from extension)
convert README.md README.docx

# Convert Markdown to plaintext
convert file.md file.txt

# Convert plaintext to Markdown
convert notes.txt notes.md

# Check all converter specs (flag form, works with no subcommand)
convert --check-specs

# Check all converter specs (subcommand form)
convert check-specs

# Show help
convert --help
convert convert --help
```

## Supported Conversions

| Source → Target | Command Example |
|-----------------|-----------------|
| Markdown → DOCX | `convert file.md file.docx` |
| Markdown → Plaintext | `convert file.md file.txt` |
| Plaintext → Markdown | `convert file.txt file.md` |
| Audio → Audio (mp3/wav/ogg/flac/aac/m4a, any pair) | `convert in.mp3 out.wav` |
| Video → Video (mp4/webm/mkv/avi/mov, any pair) | `convert in.mp4 out.webm` |
| Image → Image (png/jpg/jpeg/webp/gif, any pair) | `convert in.png out.jpg` |
| PNG/WEBP → same format (background removal) | `convert in.png out.png --remove-background` |

## Examples

### Markdown → Plaintext

**Input (`notes.md`):**
```markdown
# Meeting Notes

**Action items:**
- Review PR #42
- Update documentation

> Due: Friday
```

**Command:**
```bash
convert notes.md notes.txt
```

**Output (`notes.txt`):**
```
Meeting Notes

Action items:
- Review PR #42
- Update documentation

Due: Friday
```

### Text → Markdown

**Input (`todo.txt`):**
```
Buy groceries
Walk the dog
```

**Command:**
```bash
convert todo.txt todo.md
```

**Output (`todo.md`):**
```
Buy groceries
Walk the dog
```

## Adding a New Converter

1. Create a new file in `src/convert/converters/` (e.g., `html_to_pdf.py`)
2. Implement a `convert(req: ConversionRequest) -> ConversionResult` function
3. Decorate it with `@register("html", "pdf")`
4. Add a `spec.md` in a subdirectory (e.g., `src/convert/converters/html_to_pdf/spec.md`) or, for formats served by a shared implementation, place `spec.md` directly in `src/convert/converters/` with required sections:
   - `## Input`
   - `## Output`
   - `## Dependencies`
5. Import the converter in `src/convert/converters/__init__.py`
6. Write tests in `tests/`
7. Run `convert check-specs` to verify

## Example: Creating a Converter

```python
# src/convert/converters/html_to_pdf.py
from pathlib import Path
from convert.models import ConversionRequest, ConversionResult
from convert.registry import register

@register("html", "pdf")
def convert(req: ConversionRequest) -> ConversionResult:
    # Your conversion logic here
    req.target_path.write_bytes(b"PDF content")
    return ConversionResult(req.target_path, "html→pdf done")
```

```markdown
# src/convert/converters/html_to_pdf/spec.md
## Input
- Format: HTML (.html)

## Output
- Format: PDF (.pdf)

## Dependencies
- weasyprint >= 60.0
```

## Development

```bash
# Run tests with coverage (gate is 85%)
pytest --cov=convert --cov-fail-under=85

# Lint
ruff check src tests

# Format
ruff format src tests

# Spec check (all converter specs valid)
python -m convert.cli check-specs

# Validation order (run all three): pytest -> ruff -> check-specs

# PEP 668 note: system pip is externally managed. Install + test in an
# isolated venv instead of pip-installing into system Python:
#   python3 -m venv /tmp/opencode/convert-venv
#   /tmp/opencode/convert-venv/bin/pip install -e /mnt/HDD1/dev/scripts/convert
#   /tmp/opencode/convert-venv/bin/pip install pytest pytest-cov Pillow
#   /tmp/opencode/convert-venv/bin/python -m pytest tests/   (run from convert/)
```

## Architecture

- **CLI**: `src/convert/cli.py` - Click-based command interface
- **Registry**: `src/convert/registry.py` - Converters self-register via the `@register` decorator when imported
- **Models**: `src/convert/models.py` - `ConversionRequest` and `ConversionResult` dataclasses
- **Converters**: `src/convert/converters/` - One file per source→target pair

### Adding an ffmpeg-based converter

When many formats share one tool (e.g. audio: mp3/wav/ogg/flac/aac/m4a; video: mp4/webm/mkv/avi/mov),
use a **single shared implementation module** instead of one thin file per pair. Pattern:

1. Define a format tuple + a codec map (`_FORMATS`, `_CODEC`/`_VIDEO_CODEC`/`_AUDIO_CODEC`).
2. Implement the conversion by invoking the system `ffmpeg` binary (located via `shutil.which`)
   through `subprocess.run`, mapping stderr to a `ValueError` on failure.
3. Register every ordered pair (+ same-format) with a single loop after the function definition.
4. Add a `spec.md` in a `spec.md`-named subdirectory (e.g. `audio_to_audio/spec.md`).

`check-specs` recognizes shared modules: when the per-pair module (`png_to_jpg`) is absent it falls
back to the shared spec (`audio_to_audio/spec.md`, `video_to_video/spec.md`, or the image shared
`spec.md`) for that format family. Tests generate 1-second source clips with `ffmpeg -f lavfi`
and assert on `ffprobe` codec output. See `converters/audio_to_audio.py` and `converters/video_to_video.py`
as live templates.

## License

MIT
