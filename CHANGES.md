# Changes

## 2026-06-08

- Disabled app backup for the OCR scanner sample.
- Removed the invalid `android.permission.STORAGE` manifest permission.
- Disabled Tesseract debug logging and stopped printing external storage paths.
- Guarded bitmap downsampling for small or failed image decodes.
- Added lifecycle cleanup and ActionBar null guards around the legacy OCR
  activities.
- Added `make check` static verification for the legacy Android baseline.
- Removed tracked generated NDK `obj/` intermediates and ignored future outputs.
