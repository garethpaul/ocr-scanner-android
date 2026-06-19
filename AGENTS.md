# AGENTS.md

## Repository purpose

`garethpaul/ocr-scanner-android` is a legacy Android OCR camera and image-sharing sample.

## Project structure

- `Makefile` - repository verification targets
- `scripts` - static, host-runtime, and mutation checks
- `tests` - dependency-free host Java tests
- `docs` - plans, notes, and README assets
- `app` - Android application source and vendored runtime libraries
- `jni` - Android NDK native source
- `gradlew` - historical Gradle wrapper with documented provenance limits

## Development commands

- Full baseline: `make check`
- Host Java tests: `make host-test`
- Hostile static mutations: `make mutation-test`
- Android unit tests when a compatible SDK, JDK, and verified wrapper are available: `./gradlew test`
- Android debug build under the same conditions: `./gradlew assembleDebug`

## Change guidance

- Keep diffs focused and preserve the legacy public behavior unless the task explicitly changes it.
- Start with the narrowest relevant test, then run `make check`.
- Update tests and maintenance notes when lifecycle, privacy, validation, or toolchain behavior changes.
- Do not execute or replace the historical wrapper or vendored binaries without independent provenance evidence.
- Record skipped device, camera, OCR engine, SDK, NDK, and wrapper validation.

## Safety

- Captured images and OCR output are private user data and must remain local.
- Keep URI and file failure logs free of raw paths, provider data, and exception payloads.
- Preserve `allowBackup="false"`, disabled Tesseract debug logging, and credential-free checkout.
- Native or dependency modernization requires a dedicated compatibility change with device evidence.
