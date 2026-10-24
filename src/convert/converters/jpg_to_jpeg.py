from convert.converters.img_to_img import convert_image
from convert.models import ConversionRequest
from convert.registry import register


@register("jpg", "jpeg")
def convert(req: ConversionRequest):
    return convert_image(req)
