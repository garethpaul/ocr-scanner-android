---
title: Camera Path Recreation Guard
status: completed
date: 2026-06-17
---

# Camera Path Recreation Guard

## Priority

P1 camera-flow correctness. The path allocated for an external camera capture
currently exists only in the launcher activity instance while the camera app is
open.

## Problem

`dispatchTakePictureIntent` stores the pending output path in
`mCurrentPhotoPath`, and `onActivityResult` forwards that field to
`ResultActivity`. Activity or process recreation between those callbacks resets
the field to null, so an otherwise successful capture can no longer be opened.

## Approach

- Restore the pending camera path from `savedInstanceState` during `onCreate`.
- Persist the current path alongside the existing handled-share flag before
  delegating from `onSaveInstanceState`.
- Require a non-null pending path before forwarding a successful camera result,
  and report a controlled diagnostic when the state is unavailable.
- Preserve camera intent resolution, file creation, share-intent handling, OCR
  generation ownership, nonblocking teardown, and the legacy toolchain.
- Add mutation-sensitive static contracts, maintained guidance, changelog, and
  completed verification evidence.

## Files

- `app/src/main/java/com/garethpaul/scanr/MainActivity.java`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-17-camera-path-recreation-guard.md`

## Verification

- Prove restoration occurs during `onCreate` before a camera result can be
  delivered to the recreated activity.
- Prove `onSaveInstanceState` persists both the handled-share flag and pending
  camera path before calling `super`.
- Prove a successful camera result starts `ResultActivity` only with a non-null
  restored or live path and otherwise logs a controlled failure.
- Run all repository and external-directory Make gates.
- Reject isolated key, restore, save, ordering, result guard, forwarding,
  guidance, changelog, and completed-plan mutations.
- Audit the exact diff, Android/NDK/build artifacts, credentials, conflicts,
  binaries, large files, modes, protected paths, and whitespace.

## Scope Boundaries

- Do not change camera permissions, URI strategy, MIME filtering, share
  handling, result rendering, OCR worker/teardown ownership, SDK/NDK versions,
  or vendored binaries.
- Do not add AndroidX, dependencies, instrumentation, or generated build output.
- Keep PR #12 and its predecessors open and retain base-first stack ordering.

## Success Criteria

- A successful camera capture survives launcher activity recreation while the
  external camera is active.
- A missing pending path does not launch a broken result flow or throw an
  uncontrolled exception.

## Work Completed

- Added one saved-state key for the pending camera output path and restored it
  alongside the handled-share flag before launcher UI setup.
- Persisted the path before delegating from `onSaveInstanceState`.
- Snapshotted, null-guarded, and consumed the path before opening
  `ResultActivity`; missing state now produces a controlled generic log entry.
- Added portable source-ordering contracts and synchronized lifecycle guidance.

## Verification Completed

- Python checker compilation and all four Make gates passed from the repository
  root, and the absolute Makefile check passed from an external directory.
- Twelve isolated hostile mutations were rejected across the state key,
  restore, save, save ordering, path snapshot, null guard, forwarding, state
  consumption, controlled failure, README guidance, changelog, and completed
  plan status.
- The implementation preserves camera intent resolution, collision-resistant
  file allocation, share-intent state, result OCR ownership, and nonblocking
  teardown contracts.
- Sequential lifecycle, correctness, security, simplicity, and maintainability
  review found no actionable issue.
- Exact seven-file diff, generated Android/NDK/Python artifact, secret-signature,
  conflict-marker, binary, large-file, mode, and whitespace audits passed.

## Risks

- Android SDK, emulator, device recreation, external camera, and live OCR
  execution remain unavailable on this Linux host.
- The legacy external-storage URI strategy and Android/NDK toolchain remain
  unchanged.
- This change is stacked on PR #12, which must remain open and merge first.
