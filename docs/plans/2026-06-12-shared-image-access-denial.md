# Shared Image Access Denial

status: planned

## Context

`ResultActivity` handles missing shared-image files, null streams, and decode
failures, but `ContentResolver.openInputStream` can also throw
`SecurityException` when a URI grant is absent or revoked. That exception
currently escapes the activity. Existing error logs also include throwable
details, which can disclose provider or path information even though raw shared
image URIs are not logged directly.

## Objectives

- Catch denied shared-image URI access before it can crash the result screen.
- Reuse the existing user-facing `Unable to open image.` message for missing or
  denied access.
- Keep URI open and stream-close logs free of exception payloads and raw URI
  details.
- Preserve null-stream, failed-decode, successful OCR, and stream cleanup
  behavior.
- Extend the baseline checker and maintenance documentation for the access
  denial and sanitized logging contract.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- Mutations removing the `SecurityException` catch or restoring throwable
  logging are rejected by `make check`.
- `git diff --check`
