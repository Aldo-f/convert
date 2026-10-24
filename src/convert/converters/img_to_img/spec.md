# Image → Image Converter Spec

## Input
- Format: raster image (.png, .jpg, .jpeg, .webp, .gif)
- Any supported Pillow image mode (RGB, RGBA, L, P, etc.)

## Output
- Format: raster image (.png, .jpg, .jpeg, .webp, .gif)
- Same pixel content re-encoded in the target format
- JPEG output: alpha channel composited onto white background (JPEG has no transparency)
- Source and target must differ; identical-format conversion is rejected

## Dependencies
- Pillow
