# Legacy Android Toolchain

Verification status: declared metadata only; Android and JNI rebuild not run

## Declared Android Build

The tracked Gradle files declare this historical build surface:

- Gradle wrapper distribution: `gradle-2.2.1-all.zip`
- Android Gradle plugin: `com.android.tools.build:gradle:1.1.0`
- compile SDK: 21
- Android build tools: 22.0.1
- minimum SDK: 18
- target SDK: 18
- Android support library: `com.android.support:support-v4:21.0.3`
- local Java dependency: `app/libs/classes.jar`
- dependency repository: JCenter

These are declarations in tracked files, not proof that the historical
artifacts still resolve or build on a current workstation. The repository does
not pin an exact JDK version.

## Declared Native Build

`jni/Application.mk` requests `gnustl_static` and the `armeabi`, `armeabi-v7a`,
`x86`, and `mips` ABIs. Those components require an older Android NDK family;
the repository does not pin an exact NDK version. Modern NDK releases removed
GNU STL and some declared ABIs, so a current NDK is not a compatible substitute
without a dedicated migration.

The native build compiles vendored Tesseract and Leptonica sources under
`jni/`. Generated `obj/` output is intentionally excluded from source control.

## Reproduction Boundary

The SDK-free `make lint`, `make test`, `make build`, and `make check` targets run
static repository contracts only. They do not invoke Gradle, install Android
SDK or NDK packages, compile JNI code, build an APK, start an emulator, or run
OCR.

A future compatibility pass should first identify a known-good JDK and NDK from
independent evidence, archive required historical packages lawfully, and record
whether JCenter and the support-library coordinate still resolve. If the legacy
build cannot be reproduced, modernize it in a dedicated change that preserves
the JNI learning boundary and documents behavior differences.

## Local Files And Secrets

Keep `local.properties`, SDK paths, signing keys, APKs, generated Gradle state,
and NDK intermediates out of Git. Do not replace the vendored classes JAR,
native source, wrapper JAR, or OCR data with unverified downloads.
