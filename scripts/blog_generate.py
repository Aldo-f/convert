#!/usr/bin/env python3
"""Generate a blog post draft from GitHub release notes and README code examples.

Reads release notes for a given release tag from the GitHub API (via ``gh``),
extracts fenced code examples from the project README, and renders a Markdown
blog post draft with sections: title, intro, features, code examples, conclusion.

The script is intentionally standalone (not part of the ``convert`` package) so
it can be run manually or scheduled without installing the converter.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = "Aldo-f/convert"


def _default_readme() -> Path:
    """Return the README.md located at the project root (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent / "README.md"


def fetch_release_notes(release_tag: str, repo: str = DEFAULT_REPO) -> str:
    """Fetch the release notes (body) for *release_tag* via the GitHub API.

    Uses ``gh api /repos/{repo}/releases/tags/{tag}``.  When the release is
    missing, the API is unreachable, or ``gh`` is unavailable, falls back to a
    sample placeholder so a draft can still be generated.
    """
    try:
        completed = subprocess.run(
            ["gh", "api", f"/repos/{repo}/releases/tags/{release_tag}"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(completed.stdout)
        body = data.get("body") or ""
        if body.strip():
            return body
    except (subprocess.CalledProcessError, json.JSONDecodeError, OSError):
        pass
    return _sample_release_notes(release_tag)


def _sample_release_notes(release_tag: str) -> str:
    """Sample release notes used when GitHub cannot be reached."""
    return f"""## {release_tag}

### Features
- Universal type-x to type-y conversion
- Modular converter registry
- Markdown, DOCX, plaintext, audio, video and image support

### Improvements
- Better error messages
- Faster Docker builds
"""


def extract_code_examples(readme_text: str) -> list[tuple[str, str]]:
    """Extract fenced code blocks as ``(language, code)`` tuples from Markdown."""
    examples: list[tuple[str, str]] = []
    lines = readme_text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith("```"):
            language = stripped[3:].strip()
            index += 1
            code_lines: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            # Skip the closing fence.
            if index < len(lines):
                index += 1
            code = "\n".join(code_lines)
            if code.strip():
                examples.append((language, code))
        else:
            index += 1
    return examples


def generate_blog_post(
    release_tag: str, release_notes: str, code_examples: list[tuple[str, str]]
) -> str:
    """Render a Markdown blog post draft from release notes and code examples."""
    lines: list[str] = []
    lines.append(f"# Release {release_tag}: New Features and Improvements")
    lines.append("")

    lines.append("## Introduction")
    lines.append("")
    lines.append(
        f"We're excited to announce the release of **{release_tag}** of the "
        "convert project."
    )
    lines.append("")

    lines.append("## Features")
    lines.append("")
    lines.append(release_notes.strip())
    lines.append("")

    lines.append("## Code Examples")
    lines.append("")
    if code_examples:
        for number, (language, code) in enumerate(code_examples, start=1):
            lines.append(f"### Example {number}")
            lines.append("")
            fence = f"```{language}" if language else "```"
            lines.append(fence)
            lines.append(code)
            lines.append("```")
            lines.append("")
    else:
        lines.append("_No code examples found._")
        lines.append("")

    lines.append("## Conclusion")
    lines.append("")
    lines.append(f"Try out {release_tag} today and let us know what you think!")
    lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a blog post draft from release notes and README examples.",
    )
    parser.add_argument(
        "--release",
        required=True,
        help="Release tag/version (e.g. v1.0.0)",
    )
    parser.add_argument(
        "--output",
        help="Output file path (defaults to stdout)",
    )
    parser.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help="GitHub repository as owner/name (default: %(default)s)",
    )
    parser.add_argument(
        "--readme",
        default=None,
        help="Path to README (default: README.md at the project root)",
    )
    args = parser.parse_args(argv)

    release_notes = fetch_release_notes(args.release, args.repo)

    readme_path = Path(args.readme) if args.readme else _default_readme()
    code_examples: list[tuple[str, str]] = []
    if readme_path.exists():
        code_examples = extract_code_examples(readme_path.read_text(encoding="utf-8"))

    markdown = generate_blog_post(args.release, release_notes, code_examples)

    if args.output:
        Path(args.output).write_text(markdown, encoding="utf-8")
    else:
        sys.stdout.write(markdown if markdown.endswith("\n") else markdown + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
