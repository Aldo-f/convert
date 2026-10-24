# DOCX → Markdown Converter Spec

## Input
- Format: Word document (.docx)
- Reads headings, list items, blockquotes, paragraphs, and tables

## Output
- Format: Markdown (.md)
- Headings 1–6 mapped to `#`–`######`
- Bullets mapped to `- `, numbers mapped to `1. `, blockquotes mapped to `> `
- Tables rendered as `| cell | cell |` rows

## Dependencies
- python-docx
