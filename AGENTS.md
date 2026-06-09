# AGENTS.md

## Repository purpose

`garethpaul/ocr-scanner-android` is an Android application or sample. An OCR Scanner for Android

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `app` - application source or app module
- `jni` - Android NDK native source
- `build.gradle` - Gradle build configuration
- `gradlew` - checked-in Gradle wrapper

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Combined verification: `make verify`
- Android unit tests when the SDK is configured: `./gradlew test`
- Android debug build when the SDK is configured: `./gradlew assembleDebug`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: C++ (10), C/C++ headers (5), C (4), Java (3).
- Use the checked-in Gradle wrapper for Android builds when an SDK is configured.

## Testing guidance

- No dedicated test files were detected; treat `make check` as the minimum baseline.
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- The app processes camera images and OCR text. Android `allowBackup` is disabled and Tesseract debug logging should remain off.
- The legacy code still uses external storage for image and Tesseract data; do not commit captured images, OCR output, or generated device data.
- Timestamped capture files are still private user data and should remain local to the device or test fixture environment.
- Keep stdout clear of OCR lifecycle and photo result details.
- Avoid stack trace dumps around private image URI handling.
- Checked-in binary libraries are present; do not replace them without documenting toolchain and checksums.
- Native/NDK changes need toolchain, ABI list, and smoke-test notes before replacing runtime libraries.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
