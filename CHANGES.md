# Changes

## 2026-06-10

- Added pinned, read-only hosted Linux validation for the SDK-free baseline.
- Added a SHA-256 integrity guard for the checked-in Gradle wrapper JAR.
- Added an image open failure message so unreadable shared image URIs update
  the result screen instead of only logging the failure.
- Made timestamped camera captures collision-resistant within the same second
  and added sanitized image-file creation failure logging.
- Removed the unusable `tesseract-android-tools` gitlink, which had no
  `.gitmodules` metadata and caused hosted checkout cleanup warnings.

## 2026-06-08

- Disabled app backup for the OCR scanner sample.
- Removed the invalid `android.permission.STORAGE` manifest permission.
- Disabled Tesseract debug logging and stopped printing external storage paths.
- Guarded bitmap downsampling for small or failed image decodes.
- Added lifecycle cleanup and ActionBar null guards around the legacy OCR
  activities.
- Wrote camera captures to timestamped external-storage image files and checked
  image directory creation before launching the camera intent.
- Removed activity stdout prints from OCR lifecycle and photo result paths.
- Replaced image URI `printStackTrace()` calls with tagged Android logging.
- Routed shared image intents through explicit `EXTRA_STREAM` URI handling.
- Narrowed the share intent filter to image-only content.
- Added shared image stream guards before OCR processing.
- Added `make lint`, `make test`, and `make build` aliases so the standard
  gate commands run the same SDK-free static baseline as `make check`.
- Closed OCR traineddata streams after asset-copy attempts and kept copy
  failure logs generic.
- Added `make check` static verification for the legacy Android baseline.
- Removed tracked generated NDK `obj/` intermediates and ignored future outputs.
