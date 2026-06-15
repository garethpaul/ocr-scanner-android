# Remove Unused Launcher Progress State

status: in_progress

## Context

After removing the launcher's unused OCR engine, `MainActivity` still imports
`ProgressDialog` and retains `mProgressDialog` even though neither participates
in launcher behavior. The active OCR progress dialog belongs to
`ResultActivity` and must remain unchanged.

## Goal

Remove only the dead launcher progress state and make the activity ownership
boundary explicit in portable checks and guidance.

## Scope

- Remove the unused `ProgressDialog` import and field from `MainActivity`.
- Preserve `ResultActivity` progress creation, display, dismissal, and teardown.
- Add static contracts and synchronized guidance for the launcher/result-screen
  ownership boundary.
- Do not modernize the legacy Android toolchain, alter OCR execution, or claim
  an APK/emulator build from this Linux host.

## Verification Plan

- Run checker compilation, all four Make gates, and the absolute Makefile check
  from an external directory.
- Reject five isolated hostile mutations covering the import, field, result
  ownership, guidance, and completed plan evidence.
- Run `git diff --check` and audit exact paths, generated artifacts, protected
  Gradle/manifest/JNI/assets/binaries, modes, and credential-shaped additions.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and validation.
