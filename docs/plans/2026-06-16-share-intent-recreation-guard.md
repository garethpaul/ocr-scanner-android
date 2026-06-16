---
title: Share Intent Recreation Guard
status: planned
date: 2026-06-16
---

# Share Intent Recreation Guard

## Priority

P1 user-flow correctness. Recreating the launcher activity can process the same
shared image again, launching duplicate result activities and OCR work.

## Problem

`MainActivity` uses `mHandledSendIntent` to keep `ACTION_SEND` one-shot only for
the current Java object. Activity rotation or process recreation resets that
field before `onResume`, so the unchanged launch intent is handled again.

## Approach

- Restore the handled flag from `savedInstanceState` during `onCreate`.
- Persist the flag in `onSaveInstanceState` before delegating to the framework.
- Keep first-launch share filtering, stream forwarding, camera capture, result
  generation, OCR lifecycle, and legacy toolchain behavior unchanged.
- Add mutation-sensitive static contracts, maintained guidance, changelog, and
  completed verification evidence.

## Files

- `app/src/main/java/com/garethpaul/scanr/MainActivity.java`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-share-intent-recreation-guard.md`

## Verification

- Prove restoration occurs in `onCreate` before `onResume` can process the
  launch intent.
- Prove `onSaveInstanceState` writes the current flag before calling `super`.
- Prove the existing one-shot `ACTION_SEND` guard remains in `onResume`.
- Run all repository and external-directory Make gates.
- Reject isolated key, restore, save, ordering, guard, guidance, changelog, and
  completed-plan mutations.
- Audit exact diff, Android/NDK/build artifacts, credentials, conflicts,
  binaries, large files, modes, protected paths, and whitespace.

## Scope Boundaries

- Do not change MIME filtering, URI forwarding, camera paths, permissions,
  result activity behavior, OCR worker/teardown ownership, SDK/NDK versions, or
  vendored binaries.
- Do not add AndroidX, dependencies, instrumentation, or generated build output.
- Keep PR #11 and its predecessors open and retain base-first stack ordering.

## Success Criteria

- A recreated launcher activity does not process an already-handled shared
  image intent again.
- A fresh share launch still forwards one valid image stream exactly once.
