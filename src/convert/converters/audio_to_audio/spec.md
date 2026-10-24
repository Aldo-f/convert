# Audio → Audio Converter Spec

## Input
- Format: audio file (.mp3, .wav, .ogg, .flac, .aac, .m4a)
- Any audio input ffmpeg can decode

## Output
- Format: audio file (.mp3, .wav, .ogg, .flac, .aac, .m4a)
- Audio re-encoded with the codec appropriate to the target format:
  - mp3 -> libmp3lame, wav -> pcm_s16le, ogg -> libvorbis,
  - flac -> flac, aac/m4a -> aac
- Source and target must differ only in format; same-format conversion is supported

## Dependencies
- ffmpeg (system binary)
