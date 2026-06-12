# Remove Orphaned Gitlink

status: completed

## Context

The initial commit tracked `tesseract-android-tools` as a mode-`160000` gitlink
without a `.gitmodules` entry. The path cannot be initialized as a submodule,
is empty in normal checkouts, and causes the pinned checkout action to emit a
Git failure during post-job credential cleanup.

## Objectives

- Remove the unusable `tesseract-android-tools` gitlink from the archive.
- Preserve the vendored OCR and Leptonica source under `jni/`.
- Reject future orphaned gitlinks in the SDK-free baseline.
- Document that any future submodule needs explicit metadata and provenance.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
- Successful hosted validation without checkout cleanup warnings
