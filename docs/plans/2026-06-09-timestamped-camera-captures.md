# Timestamped Camera Captures

status: completed

## Context

`MainActivity.createImageFile()` always created `JPEG_.jpg` in the legacy
external-storage `TessOCR` directory. A new camera capture could overwrite the
previous image before OCR review or manual cleanup.

## Objectives

- Preserve the existing camera intent and external-storage location.
- Use timestamped capture filenames so captures do not collide by default.
- Fail image creation when the capture directory cannot be created.
- Extend `make check` and documentation for the camera file boundary.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`

Full Android and NDK builds still require a compatible Android SDK/NDK host.
