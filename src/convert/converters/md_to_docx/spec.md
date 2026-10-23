# Markdown → DOCX Converter Spec

## Input
- Format: Markdown (.md)
- Supported elements:
  - Headings (# to ######)
  - Bold (**text** or __text__)
  - Italic (*text* or _text_)
  - Lists (bullet and numbered)
  - Tables (pipe syntax)
  - Blockquotes (> text)
  - Horizontal rules (---, ***, ___)

## Output
- Format: Microsoft Word (.docx)
- Preserves formatting via python-docx styles
- Tables converted to Word tables with header row bolded
- Headings mapped to Word heading styles

## Dependencies
- python-docx >= 1.2.0
- lxml >= 3.1.0 (transitive)