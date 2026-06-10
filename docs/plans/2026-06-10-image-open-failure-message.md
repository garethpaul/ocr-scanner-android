# Image Open Failure Message

status: completed

## Context

Shared-image OCR already handles null streams and bitmap decode failures with
user-facing result text. When opening a shared image URI throws
`FileNotFoundException`, the activity logs the failure but leaves the result
view unchanged.

## Objectives

- Show `Unable to open image.` when shared image URI opening fails.
- Preserve sanitized URI error logging without raw URI details.
- Preserve existing null-stream and bitmap decode failure handling.
- Extend docs and the active baseline checker for the image open failure
  message.

## Verification

- `scripts/check-baseline.py`
- `make check`
- `git diff --check`
