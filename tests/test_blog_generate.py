import sys
from pathlib import Path
from unittest.mock import patch

# Make the standalone scripts/ directory importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from blog_generate import (
    extract_code_examples,
    fetch_release_notes,
    generate_blog_post,
)

SAMPLE_README = """# convert

Some intro text.

```bash
convert README.md README.docx
```

More text.

```python
print("hello")
```

No fence here.
"""


def test_extract_code_examples_returns_fenced_blocks():
    examples = extract_code_examples(SAMPLE_README)
    assert len(examples) == 2
    assert examples[0] == ("bash", "convert README.md README.docx")
    assert examples[1] == ("python", 'print("hello")')


def test_extract_code_examples_empty_when_no_fences():
    assert extract_code_examples("just plain text") == []


def test_generate_blog_post_contains_required_sections():
    markdown = generate_blog_post(
        "v1.0.0",
        "## v1.0.0\n- New feature",
        [("bash", "convert a.md b.txt")],
    )
    assert "# Release v1.0.0: New Features and Improvements" in markdown
    assert "## Introduction" in markdown
    assert "## Features" in markdown
    assert "## Code Examples" in markdown
    assert "## Conclusion" in markdown
    assert "convert a.md b.txt" in markdown
    assert "```bash" in markdown


def test_fetch_release_notes_falls_back_to_sample(monkeypatch):
    # Force gh to fail so the fallback path is exercised.
    def _boom(*_args, **_kwargs):
        raise FileNotFoundError("gh not found")

    with patch("subprocess.run", side_effect=_boom):
        notes = fetch_release_notes("v1.0.0")
    assert isinstance(notes, str)
    assert "v1.0.0" in notes
    assert "Features" in notes
