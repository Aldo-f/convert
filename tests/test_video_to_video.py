"""Tests for video-to-video conversion (ffmpeg subprocess)."""

from click.testing import CliRunner

from convert.cli import cli

_VIDEO_FORMATS = ("mp4", "webm", "mkv", "avi", "mov")

_VIDEO_SOURCE_CODEC = {
    "mp4": ("libx264", "aac"),
    "webm": ("libvpx-vp9", "libvorbis"),
    "mkv": ("libx264", "aac"),
    "avi": ("libx264", "aac"),
    "mov": ("libx264", "aac"),
}


def _make_video(tmp_path, name, fmt="mp4"):
    """Generate a 1-second test video via ffmpeg."""
    src = tmp_path / name
    import subprocess

    vcodec, acodec = _VIDEO_SOURCE_CODEC[fmt]
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc=duration=1:size=160x120:rate=15",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            "-c:v",
            vcodec,
            "-c:a",
            acodec,
            "-shortest",
            str(src),
        ],
        capture_output=True,
        check=True,
    )
    return src


def _probe_video_codec(path):
    import json
    import subprocess

    out = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(out.stdout)["streams"][0]["codec_name"]


def _convert(tmp_path, src_name, dst_name):
    src_fmt = src_name.split(".")[-1]
    src = _make_video(tmp_path, src_name, fmt=src_fmt)
    out = tmp_path / f"out.{dst_name}"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    return r, out


def test_mp4_to_webm(tmp_path):
    r, out = _convert(tmp_path, "in.mp4", "webm")
    assert r.exit_code == 0
    assert out.exists()
    assert _probe_video_codec(out) == "vp9"


def test_webm_to_mp4(tmp_path):
    r, out = _convert(tmp_path, "in.webm", "mp4")
    assert r.exit_code == 0
    assert out.exists()
    assert _probe_video_codec(out) == "h264"


def test_mkv_to_avi(tmp_path):
    import subprocess

    src = tmp_path / "in.mkv"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc=duration=1:size=160x120:rate=15",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-shortest",
            str(src),
        ],
        capture_output=True,
        check=True,
    )
    out = tmp_path / "out.avi"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code == 0
    assert out.exists()
    assert _probe_video_codec(out) == "h264"


def test_all_video_ordered_pairs_registered(tmp_path):
    from convert.registry import registry

    for src in _VIDEO_FORMATS:
        for dst in _VIDEO_FORMATS:
            assert registry.get(src, dst) is not None, f"{src} -> {dst} not registered"


def test_non_video_file_errors(tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("not video")
    out = tmp_path / "out.mp4"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code != 0
