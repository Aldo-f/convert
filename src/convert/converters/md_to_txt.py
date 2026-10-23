import re
from convert.models import ConversionRequest, ConversionResult
from convert.registry import register


def _is_table_separator(stripped: str) -> bool:
    """True for Markdown table separator rows like |---|---| or |:---|---:|."""
    if "|" not in stripped or "-" not in stripped:
        return False
    core = stripped.replace("|", "").replace("-", "").replace(":", "").replace(" ", "")
    return core == ""


@register("md", "txt")
def convert(req: ConversionRequest) -> ConversionResult:
    content = req.source_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    out_lines = []
    in_code_fence = False
    for line in lines:
        stripped = line.strip()

        # Fenced code blocks: drop the ``` fence lines, keep code lines.
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

        # Blockquote: remove leading "> ".
        if stripped.startswith("> "):
            out_lines.append(stripped[2:])
            continue

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

        # Links [text](url) -> text; images ![alt](url) -> alt.
        line = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)

        # Bold/italic markers **, __, *, _ removed (keep inner text).
        line = re.sub(r"\*\*([^*]*)\*\*", r"\1", line)
        line = re.sub(r"__([^_]*)__", r"\1", line)
        line = re.sub(r"\*([^*]*)\*", r"\1", line)
        line = re.sub(r"_([^_]*)_", r"\1", line)

        # Inline code backticks removed (keep inner text).
        line = re.sub(r"`([^`]*)`", r"\1", line)

        out_lines.append(line)

    req.target_path.write_text("\n".join(out_lines), encoding="utf-8")
    return ConversionResult(req.target_path, "md->txt done")
