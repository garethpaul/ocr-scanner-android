# OCR Scanner Android Baseline Plan

status: completed

## Context

`ocr-scanner-android` is a legacy Android OCR sample that captures images,
stores Tesseract data on external storage, and displays recognized text.

## Risks

- App backup was enabled for an app that can process user images and OCR text.
- The manifest requested the invalid `android.permission.STORAGE` permission.
- Native Tesseract debug logging was enabled and the app printed its external
  storage data path.
- Bitmap downsampling could compute an invalid sample size for small images.
- Generated NDK object intermediates were tracked alongside source and binary
  runtime artifacts.

## Work Completed

- Disabled Android backup in the manifest.
- Removed the invalid storage permission while leaving explicit legacy
  read/write external storage permissions documented.
- Disabled Tesseract debug logging and stopped printing the data path.
- Guarded bitmap sample-size calculation and skipped OCR when decode fails.
- Removed generated NDK `obj/` intermediates from source control and ignored
  future local build outputs.
- Added `make check` and `scripts/check-baseline.py` static verification.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`

Full Android and NDK builds still require a compatible Android SDK/NDK host.
