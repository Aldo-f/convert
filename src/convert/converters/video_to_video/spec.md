# Video → Video Converter Spec

## Input
- Format: video file (.mp4, .webm, .mkv, .avi, .mov)
- Any video input ffmpeg can decode

## Output
- Format: video file (.mp4, .webm, .mkv, .avi, .mov)
- Video re-encoded with the codec appropriate to the target format:
  - mp4/mkv/avi/mov -> libx264, webm -> libvpx-vp9
  - Audio re-encoded to aac
- Same-format conversion is supported

## Dependencies
- ffmpeg (system binary)
