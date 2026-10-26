# Text → Text Converter Spec

## Input
- Format: plain text (.txt) or Markdown (.md) or DOCX (.docx)
- All text-based conversions supported via stdlib + python-docx for docx pairs

## Output
- Format: plain text (.txt), Markdown (.md), or DOCX (.docx)
- Text pairs: identity / simple formatting strip (md→txt); docx requires python-docx
- Same-format pairs (txt→txt etc.) are supported but not registered explicitly — the loop skips same-format pairs; only ordered cross-format pairs registered.

## Dependencies
- Python stdlib (re, pathlib)
- python-docx (only for pairs involving .docx)
