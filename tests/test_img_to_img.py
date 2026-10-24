from click.testing import CliRunner
from PIL import Image

from convert.cli import cli

_FORMATS = ("png", "jpg", "jpeg", "webp", "gif")


def _make_image(tmp_path, name, mode="RGB", color=(255, 0, 0)):
    path = tmp_path / name
    Image.new(mode, (10, 10), color).save(path)
    return path


def _opened_format(path):
    with Image.open(path) as img:
        img.load()
        return img.format, img.mode


def _convert(tmp_path, src_name, dst_name):
    src = _make_image(tmp_path, src_name)
    out = tmp_path / f"out.{dst_name}"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    return r, out


def _convert_with_bg_removal(tmp_path, src_name, dst_name, color="white"):
    src = _make_image(tmp_path, src_name, mode="RGBA", color=(255, 0, 0, 128))
    out = tmp_path / f"out.{dst_name}"
    r = CliRunner().invoke(
        cli,
        ["convert", str(src), str(out), "--remove-background", "--bg-color", color],
    )
    return r, out


def test_png_to_jpg(tmp_path):
    r, out = _convert(tmp_path, "in.png", "jpg")
    assert r.exit_code == 0
    assert out.exists()
    fmt, mode = _opened_format(out)
    assert fmt == "JPEG"
    assert mode == "RGB"


def test_png_remove_background(tmp_path):
    # Source: top half white (background), bottom half red (foreground).
    src = tmp_path / "in.png"
    img = Image.new("RGBA", (10, 10), (255, 255, 255, 255))
    for y in range(5, 10):
        for x in range(10):
            img.putpixel((x, y), (255, 0, 0, 255))
    img.save(src)
    out = tmp_path / "out.png"
    r = CliRunner().invoke(
        cli,
        ["convert", str(src), str(out), "--remove-background", "--bg-color", "white"],
    )
    assert r.exit_code == 0
    with Image.open(out) as result:
        result.load()
        assert result.mode == "RGBA"
        # top half: background removed -> transparent
        assert result.getpixel((0, 0)) == (0, 0, 0, 0)
        # bottom half: foreground preserved opaque red
        assert result.getpixel((0, 9)) == (255, 0, 0, 255)


def test_png_remove_background_webp(tmp_path):
    src = tmp_path / "in.png"
    Image.new("RGBA", (10, 10), (255, 255, 255, 255)).save(src)
    out = tmp_path / "out.webp"
    r = CliRunner().invoke(
        cli,
        ["convert", str(src), str(out), "--remove-background", "--bg-color", "#FFFFFF"],
    )
    assert r.exit_code == 0
    fmt, mode = _opened_format(out)
    assert fmt == "WEBP"
    assert mode == "RGBA"


def test_png_rgba_to_jpg(tmp_path):
    src = _make_image(tmp_path, "in.png", mode="RGBA", color=(255, 0, 0, 128))
    out = tmp_path / "out.jpg"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code == 0
    fmt, mode = _opened_format(out)
    assert fmt == "JPEG"
    assert mode == "RGB"


def test_jpg_to_png(tmp_path):
    r, out = _convert(tmp_path, "in.jpg", "png")
    assert r.exit_code == 0
    fmt, mode = _opened_format(out)
    assert fmt == "PNG"


def test_jpeg_to_webp(tmp_path):
    r, out = _convert(tmp_path, "in.jpeg", "webp")
    assert r.exit_code == 0
    fmt, _ = _opened_format(out)
    assert fmt == "WEBP"


def test_webp_to_gif(tmp_path):
    r, out = _convert(tmp_path, "in.webp", "gif")
    assert r.exit_code == 0
    fmt, _ = _opened_format(out)
    assert fmt == "GIF"


def test_gif_to_webp(tmp_path):
    src = _make_image(tmp_path, "in.gif", mode="P", color=128)
    out = tmp_path / "out.webp"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code == 0
    fmt, _ = _opened_format(out)
    assert fmt == "WEBP"


def test_all_ordered_pairs_registered(tmp_path):
    from convert.registry import registry

    for src in _FORMATS:
        for dst in _FORMATS:
            if src != dst:
                assert registry.get(src, dst) is not None, f"{src} -> {dst} not registered"


def test_non_image_file_errors(tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("not an image")
    out = tmp_path / "out.png"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code != 0
