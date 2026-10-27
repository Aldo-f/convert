"""Tests for audio-to-audio conversion (ffmpeg subprocess)."""

from click.testing import CliRunner

from convert.cli import cli

_AUDIO_FORMATS = ("mp3", "wav", "ogg", "flac", "aac", "m4a")


def _make_audio(tmp_path, name, fmt="wav"):
    """Generate a 1-second sine-wave audio file via ffmpeg."""
    src = tmp_path / name
    import subprocess

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
            "sine=frequency=440:duration=1",
            str(src),
        ],
        capture_output=True,
        check=True,
    )
    return src


def _probe_format(path):
    import json
    import subprocess

    out = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
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
    src = _make_audio(tmp_path, src_name)
    out = tmp_path / f"out.{dst_name}"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    return r, out


def test_mp3_to_wav(tmp_path):
    r, out = _convert(tmp_path, "in.mp3", "wav")
    assert r.exit_code == 0
    assert out.exists()
    assert _probe_format(out) == "pcm_s16le"


def test_wav_to_mp3(tmp_path):
    r, out = _convert(tmp_path, "in.wav", "mp3")
    assert r.exit_code == 0
    assert out.exists()
    assert _probe_format(out) == "mp3"


def test_wav_to_ogg(tmp_path):
    r, out = _convert(tmp_path, "in.wav", "ogg")
    assert r.exit_code == 0
    assert out.exists()
    assert _probe_format(out) == "vorbis"


def test_flac_to_aac(tmp_path):
    # Build flac via ffmpeg from sine source.
    import subprocess

    src = tmp_path / "in.flac"
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
            "sine=frequency=440:duration=1",
            str(src),
        ],
        capture_output=True,
        check=True,
    )
    out = tmp_path / "out.aac"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code == 0
    assert out.exists()
    assert _probe_format(out) == "aac"


def test_all_audio_ordered_pairs_registered(tmp_path):
    from convert.registry import registry

    for src in _AUDIO_FORMATS:
        for dst in _AUDIO_FORMATS:
            assert registry.get(src, dst) is not None, f"{src} -> {dst} not registered"


def test_non_audio_file_errors(tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("not audio")
    out = tmp_path / "out.mp3"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code != 0
