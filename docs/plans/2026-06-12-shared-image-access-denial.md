# Shared Image Access Denial

status: completed

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

## Work Completed

- Caught `SecurityException` from denied or revoked shared-image URI grants.
- Reused the existing `Unable to open image.` result state.
- Removed throwable payloads from URI open, access-denied, and stream-close
  logs.
- Preserved successful OCR, null-stream, decode-failure, and cleanup behavior.

## Verification Completed

- `make lint` passed on 2026-06-12.
- `make test` passed on 2026-06-12.
- `make build` passed on 2026-06-12.
- `make check` passed on 2026-06-12.
- `make check` rejected a mutation removing the `SecurityException` catch on
  2026-06-12.
- `make check` rejected a mutation restoring the throwable payload on the image
  URI open log on 2026-06-12.
- `make check` rejected a mutation removing the denied-access user message on
  2026-06-12.
- `git diff --check` passed on 2026-06-12.
- `python3 -m py_compile scripts/check-baseline.py` passed on 2026-06-12.
- Canonical push run `27398025031` and pull-request run `27398031226`
  completed successfully at exact head
  `bbe4ce1f337f73f27477849a195bf732bcdfe5fb`.
- The implementation preserves `catch (SecurityException e)`,
  `Log.e(TAG, "Image URI access denied")`, and
  `mResult.setText("Unable to open image.")` without exception payloads.
