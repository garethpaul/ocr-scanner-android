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

The checked wrapper JAR has SHA-256
`e2b82129ab64751fd40437007bd2f7f2afb3c6e41a9198e628650b22d5824a14` and an
embedded Gradle 1.6 development timestamp from April 4, 2013. Its bytes do not
match the wrapper JAR in Gradle's official `v1.6` source tag
(`45b9815ae556ac12a4fefecefc724637232caf38adaacc0dd66f8db6ad37225e`) or
Gradle's published 2.2.1 wrapper checksum
(`5f73d431fd1c5dcc2cf11555b8e486c43249c1099f678ccc6088b05be600a2e1`).
The declared 2.2.1 all-distribution checksum is
`1d7c28b3731906fd1b2955946c1d052303881585fc14baedd675e4cf2bc1ecab`.
Because the historical wrapper's exact provenance remains unverified, this
review did not execute it.

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
