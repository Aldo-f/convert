"""Shared audio-to-audio conversion for mp3/wav/ogg/flac/aac/m4a.

Wraps ffmpeg (system binary) via subprocess; no new Python dependencies.
Registers every ordered audio pair (plus same-format) on import.
"""

import shutil
import subprocess

from convert.models import ConversionRequest, ConversionResult
from convert.registry import register

_FORMATS = ("mp3", "wav", "ogg", "flac", "aac", "m4a")
_CODEC = {
    "mp3": "libmp3lame",
    "wav": "pcm_s16le",
    "ogg": "libvorbis",
    "flac": "flac",
    "aac": "aac",
    "m4a": "aac",
}


def _ffmpeg_path() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise RuntimeError("ffmpeg not found on PATH; required for audio conversion")
    return path


def convert_audio(req: ConversionRequest) -> ConversionResult:
    src_fmt = req.src_fmt.lower()
    dst_fmt = req.dst_fmt.lower()

    if src_fmt not in _FORMATS or dst_fmt not in _FORMATS:
        raise ValueError(f"Unsupported conversion: {src_fmt} -> {dst_fmt}")

    codec = _CODEC[dst_fmt]
    ffmpeg = _ffmpeg_path()

    try:
        result = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(req.source_path),
                "-c:a",
                codec,
                str(req.target_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise ValueError(f"Failed to run ffmpeg: {exc}") from exc

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ValueError(f"ffmpeg failed ({src_fmt} -> {dst_fmt}): {detail}")

    return ConversionResult(req.target_path, f"{src_fmt}->{dst_fmt} done")


# Register every ordered audio pair, plus same-format.
for _src in _FORMATS:
    for _dst in _FORMATS:
        register(_src, _dst)(convert_audio)
