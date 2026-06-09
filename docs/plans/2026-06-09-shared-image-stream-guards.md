# Shared Image Stream Guards

status: completed

## Context

Shared image intents route their `EXTRA_STREAM` URI into `ResultActivity` for
OCR. The path logged missing URI files, but a resolver that returned a null
stream or a stream that decoded to no bitmap could still fall through toward OCR
setup.

## Objectives

- Stop shared-image OCR when `openInputStream` returns null.
- Stop shared-image OCR when bitmap decoding fails.
- Keep existing tagged URI error logging.
- Extend the static baseline and docs for shared image stream guards.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
