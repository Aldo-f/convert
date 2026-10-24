# DOCX → Text Converter Spec

## Input
- Format: Word document (.docx)
- Reads body paragraphs and tables

## Output
- Format: Plain text (.txt)
- Paragraphs preserved in order; table rows rendered as "cell1 | cell2 | ..."
- Each table followed by a blank line

## Dependencies
- python-docx
