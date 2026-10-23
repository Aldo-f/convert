# Markdown → Plaintext Converter Spec

## Input
- Format: Markdown (.md)
- Supported elements: headings, bold/italic, inline code, links, images, blockquotes, tables, fenced code blocks

## Output
- Format: Plain text (.txt)
- Markdown syntax stripped; inner text preserved
- Table rows converted to "cell1 | cell2" plain text; separator rows dropped
- Fenced code blocks: fence lines dropped, code lines kept

## Dependencies
- None (stdlib only)
