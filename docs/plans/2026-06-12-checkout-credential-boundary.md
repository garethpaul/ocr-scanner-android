# Checkout Credential Boundary

status: completed

## Context

The recorded baseline describes hosted checkout as credential-free, but the
exact PR head still uses the checkout action's default credential persistence.
The Linux job only needs repository contents for the SDK-free static baseline.

## Objectives

- Disable checkout credential persistence without changing OCR behavior.
- Enforce one workflow, one read-only permission block, one checkout action,
  and one correctly nested non-persisted credential declaration.
- Preserve immutable action pins, Python 3.12, Ubuntu 24.04, timeout,
  concurrency, and `make check`.
- Correct documentation to match the exact workflow.

## Implementation Units

### Workflow And Checker

Files: `.github/workflows/check.yml` and `scripts/check-baseline.py`.

Add the checkout boundary and reject duplicate workflows, permissions,
checkout actions, write scopes, misplaced or contradictory settings, and
incomplete plan evidence.

### Documentation

Files: `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan.

Record the shorter credential lifetime while preserving the SDK-free hosted
boundary.

## Work Completed

- Added `persist-credentials: false` beneath the sole pinned checkout step.
- Added exact workflow, permission, checkout, nesting, contradiction, and plan
  evidence contracts to `scripts/check-baseline.py`.
- Updated hosted-validation documentation without changing Android, NDK,
  wrapper, OCR, or privacy behavior.

## Verification Completed

- `python3 scripts/check-baseline.py`
- `make lint`, `make test`, `make build`, and `make check`
- workflow YAML parse and `git diff --check`
- Hostile workflow and plan mutations

The local checks remain SDK-free and do not execute Gradle, Android, NDK,
camera, shared-image, or OCR operations. Canonical hosted push and pull-request
checks remain required at the exact successor head before owner merge.

## Boundaries

- Do not change Java, manifests, Gradle files, wrappers, native sources,
  vendored libraries, resources, or tests.
- Do not access camera or shared-image content, execute OCR, or run Android/NDK
  toolchains.
- Preserve the existing remediation PR and exact evidence.
