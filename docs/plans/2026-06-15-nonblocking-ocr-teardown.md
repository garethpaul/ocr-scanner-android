# Nonblocking OCR Teardown

Status: planned

## Problem

`TessOCR.getOCRResult` and `TessOCR.onDestroy` correctly synchronize access to
the native Tesseract engine. However, `ResultActivity.onDestroy` invokes that
synchronized teardown on the activity thread. If recognition is still in
progress, destruction can block the UI thread until the entire OCR call
returns.

## Scope

- Preserve the shared synchronization boundary between recognition and native
  teardown.
- Detach the active wrapper from the activity during destruction.
- Run only the potentially waiting native teardown call on a named background
  thread.
- Preserve destroyed-state and generation invalidation, progress cleanup,
  stale-result rejection, and the existing raw OCR worker model.
- Add ordering-sensitive static contracts and synchronized guidance.

## Verification

- Run checker compilation and all four Make gates from the repository plus the
  canonical external-directory check with explicit timeouts.
- Reject isolated mutations for direct UI-thread teardown, missing wrapper
  capture or clear, missing named teardown thread, reordered lifecycle steps,
  missing guidance, and stale plan status.
- Audit the exact diff, generated artifacts, credential patterns, protected
  Android/Gradle/JNI/wrapper/asset/binary paths, conflicts, modes, and intended
  paths.

## Risks

- Native teardown becomes asynchronous with respect to activity destruction,
  but remains serialized after any active OCR call by the wrapper lock.
- No Android SDK, APK, emulator, device, camera, shared image, or live OCR is
  available on this Linux host.
- The change must remain stacked on PR #10; neither pull request may be merged
  or closed without explicit owner authorization.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and verification.
