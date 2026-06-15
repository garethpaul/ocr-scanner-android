# Remove Unused Launcher OCR Engine

status: planned

## Summary

Keep native OCR engine ownership in `ResultActivity`, the only activity that
performs OCR, instead of eagerly creating a second unused wrapper in the
launcher.

## Problem

`MainActivity` constructs `TessOCR` during launcher creation and destroys it
only when the launcher is destroyed, but never calls `getOCRResult`. This
duplicates native Tesseract initialization and retains native resources without
serving any launcher behavior.

## Requirements

- Remove the unused `MainActivity` OCR field, construction, and teardown.
- Preserve traineddata installation, camera capture, and shared-image routing.
- Preserve `ResultActivity` as the sole activity owner of `TessOCR`.
- Keep the existing synchronized result-screen OCR lifecycle guards unchanged.
- Add mutation-sensitive static contracts and maintenance guidance.

## Implementation

- Delete the launcher-only `mTessOCR` lifetime from `MainActivity`.
- Require that `MainActivity` contains no `TessOCR` reference while
  `ResultActivity` still constructs, uses, and tears down its wrapper.
- Record the narrower native ownership model in repository guidance.

## Verification

- Run every Make gate and external-directory `make check`.
- Reject mutations that restore a launcher field, construction, or teardown,
  or remove the result-screen owner and documentation contracts.
- Audit the exact diff, whitespace, generated artifacts, conflict markers,
  intended paths, binary/large files, and changed-line credentials.

## Risks

- Android, JNI, APK, emulator, camera, and live OCR execution remain outside
  this Linux-hosted validation boundary.
- The change must remain stacked on PR #7 and must not be merged or closed
  without explicit owner authorization.
