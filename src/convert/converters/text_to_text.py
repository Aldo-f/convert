"""Shared text-to-text conversion implementation.

Registers all ordered text-format pairs (txt↔md, txt↔docx, md↔docx)
via a single loop on import. No per-pair thin modules needed.

Wraps Python stdlib only — no extra dependencies.
"""

from convert.models import ConversionRequest, ConversionResult
from convert.registry import register

# All supported text formats.
FORMATS = ("txt", "md", "docx")

# Ordered pairs to register (same-format pairs are handled by the loop below).
PAIRS = [
    ("txt", "md"),
    ("md", "txt"),
    ("txt", "docx"),
    ("docx", "txt"),
    ("md", "docx"),
    ("docx", "md"),
]


def _convert_txt_to_md(req: ConversionRequest) -> ConversionResult:
    """Convert plain text to Markdown — identity, just copy."""
    content = req.source_path.read_text(encoding="utf-8")
    req.target_path.write_text(content, encoding="utf-8")
    return ConversionResult(req.target_path, "txt→md done")


def _convert_md_to_txt(req: ConversionRequest) -> ConversionResult:
    """Convert Markdown to plain text — strip formatting."""
    content = req.source_path.read_text(encoding="utf-8")
    # Strip Markdown: remove headings, bold/italic, code fences, tables, links
    import re

    lines = content.splitlines()
    out_lines = []
    in_code_fence = False
    for line in lines:
        stripped = line.strip()
        # Fenced code blocks: drop the ``` fence lines, keep code lines only if desired.
        # Here we just strip the fence markers.
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            out_lines.append(line)
            continue
        # Headings: strip leading #{1,6} + space.
        m = re.match(r"#{1,6}\s+(.*)", stripped)
        if m:
            out_lines.append(m.group(1))
            continue
        # Bold/italic markers removed (keep inner text).
        line = re.sub(r"\*\*([^*]*)\*\*", r"\1", line)
        line = re.sub(r"__([^_]*)__", r"\1", line)
        line = re.sub(r"\*([^*]*)\*", r"\1", line)
        line = re.sub(r"_([^_]*)_", r"\1", line)
        # Links [text](url) -> text; images ![alt](url) -> alt.
        line = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
        # Table separator row: skip.
        if _is_table_separator(stripped):
            continue
        # Table row: trim outer pipes, replace inner "|" with " | ".
        if "|" in stripped:
            cleaned = stripped.strip()
            if cleaned.startswith("|") and cleaned.endswith("|"):
                cleaned = cleaned[1:-1]
            out_lines.append(" | ".join(part.strip() for part in cleaned.split("|")))
            continue
        out_lines.append(line)
    req.target_path.write_text("\n".join(out_lines), encoding="utf-8")
    return ConversionResult(req.target_path, "md→txt done")


def _is_table_separator(stripped: str) -> bool:
    """True for Markdown table separator rows like |---|---| or |:---|---:|."""
    if "|" not in stripped or "-" not in stripped:
        return False
    core = stripped.replace("|", "").replace("-", "").replace(":", "").replace(" ", "")
    return core == ""


def _convert_txt_to_docx(req: ConversionRequest) -> ConversionResult:
    """Convert plain text to DOCX."""
    try:
        from docx import Document
    except Exception as exc:
        raise ValueError(
            "python-docx is required for txt→docx conversion; install it via pip"
        ) from exc
    content = req.source_path.read_text(encoding="utf-8")
    doc = Document()
    for line in content.splitlines():
        doc.add_paragraph(line)
    doc.save(req.target_path)
    return ConversionResult(req.target_path, "txt→docx done")


def _convert_docx_to_txt(req: ConversionRequest) -> ConversionResult:
    """Convert DOCX to plain text."""
    try:
        from docx import Document as _Doc
    except Exception as exc:
        raise ValueError(
            "python-docx is required for docx→txt conversion; install it via pip"
        ) from exc
    doc = _Doc(req.source_path)
    text_parts = []
    for para in doc.paragraphs:
        text_parts.append(para.text)
    req.target_path.write_text("\n".join(text_parts), encoding="utf-8")
    return ConversionResult(req.target_path, "docx→txt done")


def _convert_md_to_docx(req: ConversionRequest) -> ConversionResult:
    """Convert Markdown to DOCX — strip Markdown, create DOCX."""
    try:
        from docx import Document
    except Exception as exc:
        raise ValueError(
            "python-docx is required for md→docx conversion; install it via pip"
        ) from exc
    content = req.source_path.read_text(encoding="utf-8")
    # Strip Markdown (same logic as md→txt, just identity after stripping)
    stripped_content = _strip_markdown(content)
    doc = Document()
    for line in stripped_content.splitlines():
        doc.add_paragraph(line)
    doc.save(req.target_path)
    return ConversionResult(req.target_path, "md→docx done")


def _convert_docx_to_md(req: ConversionRequest) -> ConversionResult:
    """Convert DOCX to Markdown."""
    try:
        from docx import Document as _Doc
    except Exception as exc:
        raise ValueError(
            "python-docx is required for docx→md conversion; install it via pip"
        ) from exc
    doc = _Doc(req.source_path)
    text_parts = []
    for para in doc.paragraphs:
        text_parts.append(para.text)
    # Simple conversion: just extract text as paragraphs
    md_text = "\n".join(text_parts)
    req.target_path.write_text(md_text, encoding="utf-8")
    return ConversionResult(req.target_path, "docx→md done")


def _strip_markdown(content: str) -> str:
    """Minimal Markdown stripping for DOCX conversion."""
    import re
    lines = content.splitlines()
    out_lines = []
    in_code_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            out_lines.append(line)
            continue
        m = re.match(r"#{1,6}\s+(.*)", stripped)
        if m:
            out_lines.append(m.group(1))
            continue
        line = re.sub(r"\*\*([^*]*)\*\*", r"\1", line)
        line = re.sub(r"__([^_]*)__", r"\1", line)
        line = re.sub(r"\*([^*]*)\*", r"\1", line)
        line = re.sub(r"_([^_]*)_", r"\1", line)
        line = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
        if "|" in stripped and not stripped.strip().startswith("|"):
            # Very naive table handling: skip entire lines with pipes
            continue
        out_lines.append(line)
    return "\n".join(out_lines)


# --- Registration loop: one entry per ordered pair ---

for src, tgt in PAIRS:
    # Bind the correct conversion function via a closure.
    if src == "txt" and tgt == "md":
        fn = _convert_txt_to_md
    elif src == "md" and tgt == "txt":
        fn = _convert_md_to_txt
    elif src == "txt" and tgt == "docx":
        fn = _convert_txt_to_docx
    elif src == "docx" and tgt == "txt":
        fn = _convert_docx_to_txt
    elif src == "md" and tgt == "docx":
        fn = _convert_md_to_docx
    elif src == "docx" and tgt == "md":
        fn = _convert_docx_to_md
    else:
        # Should never reach here, but keep the module importable.
        raise RuntimeError(f"no conversion function for ({src}, {tgt})")

    register(src, tgt)(fn)
