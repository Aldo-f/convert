# Text → DOCX Converter Spec

## Input
- Format: Plain text (.txt)
- Each line becomes a paragraph in the document

## Output
- Format: Word document (.docx)
- One paragraph per input line; empty lines produce empty paragraphs

## Dependencies
- python-docx
