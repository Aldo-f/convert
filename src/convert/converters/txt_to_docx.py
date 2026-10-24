from docx import Document

from convert.models import ConversionRequest, ConversionResult
from convert.registry import register


@register("txt", "docx")
def convert(req: ConversionRequest) -> ConversionResult:
    content = req.source_path.read_text(encoding="utf-8")
    doc = Document()
    for line in content.splitlines():
        doc.add_paragraph(line)
    doc.save(req.target_path)
    return ConversionResult(req.target_path, "txt→docx done")
