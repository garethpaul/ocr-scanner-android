# Unique Camera Captures

status: completed

## Context

Camera filenames include a timestamp with one-second precision. Two captures
started within the same second can therefore reuse the same external-storage
path and overwrite or race with prior private image data.

## Objectives

- Preserve the readable timestamp prefix and existing capture directory.
- Use `File.createTempFile` to guarantee a unique path for each capture.
- Log image-file creation failures without exposing private filesystem paths.
- Extend the SDK-free checker and project guidance for the collision guard.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`

Full Android and NDK builds still require a compatible legacy SDK/NDK host.
