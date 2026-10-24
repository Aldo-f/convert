"""Shared image-to-image conversion implementation for png/jpg/jpeg/webp/gif.

Registers every ordered image pair (plus same-format png->png and webp->webp
for background removal) on import. Thin per-pair modules were removed; the
registration loop below replaces them.
"""

from PIL import Image, ImageColor, UnidentifiedImageError

from convert.models import ConversionRequest, ConversionResult
from convert.registry import register

_FORMATS = ("png", "jpg", "jpeg", "webp", "gif")
_PIL_FORMAT = {
    "png": "PNG",
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "webp": "WEBP",
    "gif": "GIF",
}
_JPEG_FORMAT = "JPEG"
_TRANSPARENT_FORMATS = ("PNG", "WEBP")


def _prepare_image(img: Image.Image, pil_format: str) -> Image.Image:
    """Convert image to a mode compatible with the target format."""
    if pil_format == _JPEG_FORMAT:
        if img.mode in ("RGBA", "LA", "PA"):
            img = img.convert("RGBA")
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            return background
        if img.mode not in ("RGB", "L"):
            return img.convert("RGB")
    return img


def _parse_bg_color(bg_color: str):
    """Return an RGB triple for *bg_color*, defaulting to white on failure."""
    try:
        return ImageColor.getrgb(bg_color)[:3]
    except ValueError:
        return ImageColor.getrgb("white")[:3]


def convert_image(req: ConversionRequest):
    src_fmt = req.src_fmt.lower()
    dst_fmt = req.dst_fmt.lower()
    remove_background = req.remove_background
    bg_color = req.bg_color

    if src_fmt not in _FORMATS or dst_fmt not in _FORMATS:
        raise ValueError(f"Unsupported conversion: {src_fmt} -> {dst_fmt}")
    if src_fmt == dst_fmt and not remove_background:
        raise ValueError(f"Source and target format are the same: {src_fmt}")

    pil_format = _PIL_FORMAT[dst_fmt]

    try:
        with Image.open(req.source_path) as img:
            img.load()
            out = img.copy()

            if remove_background and pil_format in _TRANSPARENT_FORMATS:
                out = out.convert("RGBA")
                target = _parse_bg_color(bg_color)
                data = out.getdata()
                new_data = []
                for item in data:
                    if item[:3] == target:
                        new_data.append((0, 0, 0, 0))
                    else:
                        new_data.append(item)
                out.putdata(new_data)
            else:
                out = _prepare_image(img, pil_format)

            save_kwargs = {}
            if pil_format == _JPEG_FORMAT:
                save_kwargs["quality"] = 85
            out.save(req.target_path, format=pil_format, **save_kwargs)
    except UnidentifiedImageError as exc:
        raise ValueError(f"Not a valid image file: {req.source_path}") from exc

    return ConversionResult(req.target_path, f"{src_fmt}->{dst_fmt} done")


# Register every ordered image pair, plus same-format for transparent formats
# (background removal). Keys are lowercase to match CLI suffix parsing.
for _src in _FORMATS:
    for _dst in _FORMATS:
        if _src != _dst:
            register(_src, _dst)(convert_image)
for _fmt in ("png", "webp"):
    register(_fmt, _fmt)(convert_image)
