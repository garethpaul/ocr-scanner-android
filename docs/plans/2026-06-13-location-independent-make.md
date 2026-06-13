# Location-Independent OCR Scanner Verification

status: in progress

## Context

The SDK-free Make aliases invoke `scripts/check-baseline.py` relative to the
caller's working directory. An absolute Makefile invocation from elsewhere can
therefore fail or inspect the wrong tree instead of this checkout.

## Objectives

- Resolve every Make alias from the checkout containing the loaded Makefile.
- Preserve the existing target graph and `PYTHON` override.
- Enforce the exact rooted recipe, operator guidance, completed status, and
  verification evidence in the active checker.
- Prove root and external-directory behavior with mutation-sensitive checks.

## Implementation Units

### Make Contract

Files: `Makefile` and `scripts/check-baseline.py`.

Derive one absolute root from the loaded Makefile and invoke the checker by
absolute path. Require the complete small Makefile so aliases, the Python
override, and path resolution cannot drift independently.

### Documentation And Evidence

Files: `README.md`, `CHANGES.md`, and this plan.

Document absolute Makefile invocation and record bounded local and hostile
mutation verification after it completes.

## Boundaries

- Do not change Android or JNI sources, manifests, Gradle files, wrappers,
  native libraries, resources, tests, workflows, OCR behavior, or privacy
  handling.
- Do not run Android, JNI, APK, emulator, device, or OCR builds.
- Preserve the existing stacked PR chain and exact-head evidence.
