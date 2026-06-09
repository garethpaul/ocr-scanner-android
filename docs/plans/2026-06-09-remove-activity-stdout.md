# Remove Activity Stdout Plan

status: completed

## Context

The Android activities still printed lifecycle and photo-result messages to
stdout. Even when those strings are not OCR text, stdout logging encourages
noisy diagnostics near privacy-sensitive image and OCR flows.

## Objectives

- Remove `System.out.println` calls from `MainActivity` and `ResultActivity`.
- Extend the static checker so activity stdout prints cannot return silently.
- Document the quiet-by-default expectation for OCR lifecycle paths.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
