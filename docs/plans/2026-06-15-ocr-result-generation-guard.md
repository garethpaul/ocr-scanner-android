# OCR Result Generation Guard

Status: completed

## Problem

Each `ResultActivity.doOCR` call starts a raw worker, but callbacks carry no
request identity. If a newer image starts processing before an older worker
posts back, the stale completion can replace the newer result and dismiss the
newer progress state.

## Scope

- Assign a monotonically increasing generation to each OCR start.
- Allow only the current generation to post and apply UI completion.
- Invalidate all outstanding generations during activity destruction.
- Preserve native OCR ownership, destruction synchronization, progress-dialog
  cleanup, bitmap decoding, and user-facing failure behavior.
- Add ordering-sensitive static contracts and synchronized guidance.

## Verification

- Run checker compilation and all four Make gates from the repository plus the
  canonical external-directory check with explicit timeouts.
- Reject isolated mutations for missing capture, missing worker/UI comparison,
  missing destroy invalidation, stale result/progress mutation, missing
  guidance, and stale plan status.
- Audit the exact diff, generated artifacts, credential patterns, protected
  Android/Gradle/JNI/wrapper/asset/binary paths, conflicts, modes, and intended
  paths.

## Risks

- The legacy raw-thread model is retained; this change only makes completion
  ordering deterministic.
- No Android SDK, APK, emulator, device, camera, shared image, or live OCR was
  exercised on Linux.
- The change must remain stacked on PR #9; neither pull request may be merged or
  closed without explicit owner authorization.

## Work Completed

- Added a volatile monotonically increasing OCR generation and captured it for
  each worker start.
- Rejected stale generations before posting to the UI thread and again before
  result or progress mutation.
- Invalidated outstanding generations during destruction before progress and
  native OCR teardown.
- Added ordering-sensitive static contracts and synchronized guidance.

## Verification Completed

- All four Make gates passed from the repository and the canonical check passed
  from an external directory.
- Seven isolated hostile mutations were rejected for missing capture, missing
  worker or UI comparison, missing destruction invalidation, reordered stale UI
  mutation, missing guidance, and stale plan status.
- Checker compilation, exact diff, artifact, credential, protected-path,
  conflict-marker, binary, mode, whitespace, and intended-path audits passed.
- No Android SDK, APK, emulator, device, camera, shared image, or live OCR was
  exercised.
