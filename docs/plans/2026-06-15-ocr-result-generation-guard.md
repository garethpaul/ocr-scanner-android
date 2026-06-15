# OCR Result Generation Guard

Status: planned

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
