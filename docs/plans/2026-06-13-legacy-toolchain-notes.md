# Legacy Toolchain Notes

status: completed

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

## Work Completed

- Added one reference for the exact Gradle, Android plugin, SDK, build-tools,
  support-library, JCenter, classes JAR, GNU STL, and ABI declarations.
- Marked exact JDK and NDK versions as undeclared and the Android/JNI rebuild as
  unverified.
- Clarified that Make targets run static contracts only and do not build an APK,
  compile native code, start an emulator, or exercise OCR.
- Added repository, security, vision, changelog, and static checker guardrails
  without changing build metadata, source, or binaries.

## Verification Completed

Completed locally on 2026-06-13:

- `python3 -m py_compile scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML and Android manifest XML parsed successfully
- the checker passed from an external working directory
- nine focused hostile mutations rejected a false rebuild claim, Gradle version
  drift, guessed JDK and NDK versions, a false Gradle-execution claim, a stale
  README link, compile SDK drift, incomplete status, and unfinished evidence
- protected build paths had no diff, including Gradle metadata, wrapper files,
  Android manifest and Java source, JNI makefiles and source, and vendored JARs
- `git diff --check`

The Make gates and hostile mutation suite first passed against a disposable
indexed copy with completed-plan evidence. The complete static gates were then
rerun against this completed plan in the repository worktree. No Android, JNI,
APK, emulator, device, or OCR build/runtime validation was claimed.

## Boundaries

- Do not claim an Android, JNI, or OCR rebuild was completed.
- Do not guess a JDK or NDK version that is not declared in tracked metadata.
- Do not update Gradle, Android plugin, repositories, SDK levels, dependencies,
  ABIs, native sources, or vendored binaries.
- Do not download historical SDK or NDK components in this unit.
