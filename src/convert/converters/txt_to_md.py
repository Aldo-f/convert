from convert.models import ConversionRequest, ConversionResult
from convert.registry import register


@register("txt", "md")
def convert(req: ConversionRequest) -> ConversionResult:
    req.target_path.write_text(req.source_path.read_text())
    return ConversionResult(req.target_path, "txt→md done")
