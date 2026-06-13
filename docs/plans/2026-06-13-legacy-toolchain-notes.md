# Legacy Toolchain Notes

status: planned

## Context

The repository labels the Android build as legacy but does not collect its
checked-in Gradle, Android SDK, support-library, and native-build assumptions in
one place. A future reader can easily mistake declared historical metadata for
a build that has been reproduced on a current workstation.

## Priorities

1. Record exact toolchain versions and API levels declared in tracked files.
2. Make undeclared JDK and NDK versions explicit rather than guessing them.
3. Explain the obsolete GNU STL, ABI, repository, and dependency constraints.
4. Keep static validation distinct from an Android/NDK rebuild claim.

## Implementation Units

### Toolchain Reference

File: `docs/legacy-toolchain.md`

Document Gradle 2.2.1, Android Gradle plugin 1.1.0, compile SDK 21, build tools
22.0.1, min/target SDK 18, support-v4 21.0.3, the vendored classes JAR, and the
native GNU STL/ABI declarations. Mark exact JDK and NDK versions as undeclared
and the current rebuild status as unverified.

### Repository Guidance

Files:

- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Link the toolchain note, preserve the no-modernization boundary, and warn that
historical repositories or packages may no longer resolve.

### Static Contract

Files:

- `scripts/check-baseline.py`
- `docs/plans/2026-06-13-legacy-toolchain-notes.md`

Require exact declared values, explicit unknowns, no-build-claim language,
completed plan status, and local verification evidence.

## Verification Plan

- `python3 -m py_compile scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- run the checker outside the repository working directory
- parse workflow YAML and Android manifest XML
- run focused hostile mutations against the toolchain-note contracts
- verify Gradle, wrapper, manifest, Java, JNI, and vendored binary paths have no
  diff
- `git diff --check`
- scan the intended diff for secrets and generated artifacts

## Boundaries

- Do not claim an Android, JNI, or OCR rebuild was completed.
- Do not guess a JDK or NDK version that is not declared in tracked metadata.
- Do not update Gradle, Android plugin, repositories, SDK levels, dependencies,
  ABIs, native sources, or vendored binaries.
- Do not download historical SDK or NDK components in this unit.
