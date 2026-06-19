# OCR Worker Lifecycle Guard

status: completed

## Context

`ResultActivity` starts OCR on a raw worker thread. Activity destruction can
currently call `TessBaseAPI.end()` while that worker is using the same native
engine, and the worker can later post view and dialog updates to a destroyed
activity. This creates a native ownership race and a stale UI callback path.

## Priorities

1. Serialize OCR execution and native engine teardown.
2. Prevent worker and UI callbacks from touching a destroyed activity.
3. Dismiss and clear the progress dialog during destruction.
4. Keep teardown idempotent and preserve existing OCR result behavior.

## Implementation Units

### Native Engine Ownership

File: `app/src/main/java/com/garethpaul/scanr/TessOCR.java`

- Synchronize OCR execution and teardown on the same wrapper instance.
- Return an empty result if the bitmap or native engine is unavailable.
- End and clear the native engine exactly once.

### Activity Lifecycle Boundary

File: `app/src/main/java/com/garethpaul/scanr/ResultActivity.java`

- Track destroyed state with a worker-visible flag.
- Capture the active OCR wrapper before starting the worker.
- Stop before posting and again before applying UI results after destruction.
- Mark destroyed, dismiss the dialog, and tear down OCR in a fixed order.

### Static Contract And Documentation

Files: `scripts/check-baseline.py`, `README.md`, `SECURITY.md`, `VISION.md`,
`CHANGES.md`

- Require the source ordering, synchronized ownership, lifecycle guards,
  documentation, and completed verification evidence.

## Work Completed

- Serialized `TessOCR.getOCRResult` and `TessOCR.onDestroy` on the wrapper
  instance and made native teardown idempotent by clearing the engine.
- Captured the OCR wrapper before worker launch and added destroyed-state checks
  before posting and before applying UI results.
- Ordered activity teardown to mark destroyed state, dismiss and clear the
  dialog, end and clear OCR, then call the superclass.
- Added mutation-sensitive source, ordering, documentation, and plan contracts.

## Verification Completed

- `python3 -m py_compile scripts/check-baseline.py` passed.
- `make lint`, `make test`, `make build`, and `make check` passed the SDK-free
  Java, manifest, project, workflow, and documentation contracts.
- The checker passed from an external working directory through the absolute
  Makefile path.
- Seven isolated hostile mutations removing synchronization, either destroyed
  guard, dialog cleanup, teardown ordering, documentation, or completed plan
  evidence were rejected.
- Protected Gradle, manifest, native, wrapper, asset, and binary paths had no
  diff.
- `git diff --check` passed.

## Boundaries

- Do not claim Android, JNI, camera, or live OCR execution on this Linux host.
- Do not modernize the legacy Gradle, SDK, NDK, ABI, or storage model in this
  focused change.
