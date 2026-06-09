# Traineddata Stream Cleanup

status: completed

## Context

`MainActivity` copies the bundled Tesseract traineddata asset into the legacy
external-storage OCR data directory on first launch. The copy path closed its
asset and output streams only after a complete successful transfer, so an
exception could leave a stream open. The failure log also appended raw exception
details.

## Objectives

- Close OCR traineddata streams in a `finally` path after copy attempts.
- Use a shared cleanup helper for both asset and output streams.
- Keep the asset-copy behavior and destination unchanged.
- Keep traineddata copy failure logs generic and tagged.
- Extend the static baseline and docs for traineddata stream cleanup.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
