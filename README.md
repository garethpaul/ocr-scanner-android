# ocr-scanner-android

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/ocr-scanner-android` is an Android application or sample. An OCR Scanner for Android

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: C++ (10), C/C++ headers (5), C (4), Java (3).

## Repository Contents

- `CHANGES.md` - baseline change log
- `Makefile` - local static verification entry point
- `build.gradle` - Android or Gradle build configuration
- `app` - source or example code
- `gradle` - source or example code
- `gradlew` - Android or Gradle build configuration
- `jni` - source or example code
- `scripts/check-baseline.py` - static baseline checks
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: app, gradle, jni
- Dependency and build manifests: build.gradle, gradlew
- Entry points or build surfaces: Gradle build files
- Test-looking files: no obvious test files detected

## Getting Started

### Prerequisites

- Git
- Android Studio or a compatible Android SDK
- Gradle or the checked-in Gradle wrapper when present

### Setup

```bash
git clone https://github.com/garethpaul/ocr-scanner-android.git
cd ocr-scanner-android
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Use Android Studio to open the project or run `./gradlew assembleDebug` when the Android SDK is configured.
- Camera captures are written to timestamped files under the legacy
  external-storage `TessOCR` directory so a new capture does not overwrite the
  previous image.
- Activity lifecycle and photo result paths should not print OCR details to
  stdout.
- Image URI decode failures use tagged Android logging instead of dumping stack
  traces.
- Shared image intents forward their `EXTRA_STREAM` URI into the result screen
  instead of launching an empty OCR flow.

## Testing and Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `./gradlew test` or Android Studio's test runner when the SDK is configured

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.

## Security and Privacy Notes

- The app processes camera images and OCR text. Android `allowBackup` is
  disabled and Tesseract debug logging should remain off.
- The legacy code still uses external storage for image and Tesseract data; do
  not commit captured images, OCR output, or generated device data.
- Timestamped capture files are still private user data and should remain local
  to the device or test fixture environment.
- Keep stdout clear of OCR lifecycle and photo result details.
- Avoid stack trace dumps around private image URI handling.
- Shared image intent handling should require an image MIME type and a stream
  URI before OCR processing starts.
- Generated NDK outputs under `obj/` are intentionally ignored and should not
  be committed; keep only source, packaged OCR assets, and documented native
  library drops in git.
- Review changes touching authentication or token handling; examples from the scan include jni/com_googlecode_tesseract_android/glibc/glob.c.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include app/src/main/AndroidManifest.xml, app/src/main/java/com/garethpaul/scanr/MainActivity.java, app/src/main/res/layout/activity_main.xml, app/src/main/res/layout/activity_result.xml, and 6 more.
- Review changes touching mobile permissions or privacy-sensitive device data; examples from the scan include app/src/main/AndroidManifest.xml, app/src/main/java/com/garethpaul/scanr/MainActivity.java, gradlew, jni/com_googlecode_leptonica_android/box.cpp, and 6 more.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include app/src/main/AndroidManifest.xml, app/src/main/java/com/garethpaul/scanr/MainActivity.java, app/src/main/java/com/garethpaul/scanr/ResultActivity.java, app/src/main/res/layout/activity_result.xml, and 6 more.

## Maintenance Notes

- This looks like a legacy Android project or sample. Expect Android SDK, Gradle, and support-library versions to matter.
- Run `make check` before changing manifest permissions, OCR setup, image
  decode paths, or Gradle metadata.
- Keep generated NDK intermediates, APKs, local SDK config, and signing
  material out of the repository.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
