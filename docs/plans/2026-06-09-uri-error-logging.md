# URI Error Logging

status: completed

## Context

`ResultActivity.uriOCR()` caught image URI open and close failures by calling
`printStackTrace()`. OCR image paths can point at private user captures, so
diagnostics should be routed through Android logging with stable, generic
messages instead of dumping raw stack traces.

## Objectives

- Preserve existing URI decode and OCR behavior.
- Replace `printStackTrace()` calls in `ResultActivity` with tagged `Log.e`
  diagnostics.
- Keep image URI error messages generic and free of configured paths.
- Extend `make check` to reject stack trace dumps around image URI handling.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
