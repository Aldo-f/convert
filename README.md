# convert

Universal type-x to type-y converter. Lightweight, modular CLI tool for converting between document formats.

## Install

```bash
pip install -e .
```

Requires Python 3.12+.

## Usage

```bash
# Convert Markdown to DOCX (auto-detects from extension)
convert README.md README.docx

# Convert plaintext to Markdown
convert notes.txt notes.md

# Check all converter specs
convert check-specs

# Show help
convert --help
convert convert --help
```

## Supported Conversions

| Source → Target | Command Example |
|-----------------|-----------------|
| Markdown → DOCX | `convert file.md file.docx` |
| Plaintext → Markdown | `convert file.txt file.md` |

## Adding a New Converter

1. Create a new file in `src/convert/converters/` (e.g., `html_to_pdf.py`)
2. Implement a `convert(req: ConversionRequest) -> ConversionResult` function
3. Decorate it with `@register("html", "pdf")`
4. Add a `spec.md` in a subdirectory (e.g., `src/convert/converters/html_to_pdf/spec.md`) with required sections:
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
# Run tests with coverage
pytest --cov=convert --cov-fail-under=85

# Lint
ruff check src tests

# Format
ruff format src tests
```

## Architecture

- **CLI**: `src/convert/cli.py` - Click-based command interface
- **Registry**: `src/convert/registry.py` - Auto-discovers converters via `@register` decorator
- **Models**: `src/convert/models.py` - `ConversionRequest` and `ConversionResult` dataclasses
- **Converters**: `src/convert/converters/` - One file per source→target pair

## License

MIT