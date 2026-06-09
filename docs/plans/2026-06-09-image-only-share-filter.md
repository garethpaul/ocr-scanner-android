# Image-Only Share Filter

status: completed

## Context

`MainActivity` only handles shared content when the MIME type starts with
`image/` and an `EXTRA_STREAM` URI is present. The manifest still advertised
`text/plain`, causing Android to offer the OCR scanner for content the app
cannot process.

## Objectives

- Preserve shared image OCR handling.
- Remove the unsupported `text/plain` share filter.
- Keep the `image/*` share filter in place.
- Extend static checks and docs so the manifest remains image-only.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
