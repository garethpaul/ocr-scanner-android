# Shared Image Intent Plan

status: completed

## Context

The manifest accepts `ACTION_SEND` with image data, and `ResultActivity` already
has a URI-based OCR path. `MainActivity` launched `ResultActivity` for shared
content without forwarding the shared image stream, leaving the result screen
without an image to decode.

## Objectives

- Forward shared image `EXTRA_STREAM` URIs from `MainActivity` to
  `ResultActivity`.
- Require the shared content MIME type to start with `image/`.
- Route shared streams through the existing `uriOCR` path.
- Avoid repeated handling of the same share intent while the activity resumes.
- Extend static checks and docs for the shared image intent boundary.

## Verification

- `make check`
- `git diff --check`
