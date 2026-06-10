## OCR Scanner Android Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

OCR Scanner Android is a legacy Android sample for on-device optical character
recognition using native Tesseract and Leptonica bindings.

The repository is useful as a reference for wiring an Android app to JNI-based
OCR libraries, Gradle-era Android project structure, and packaged native
dependencies. Its value is in showing the integration boundaries clearly.

The goal is to make the sample reproducible and safe to study while separating
legacy build constraints from any future modernization work.

Current baseline: `make lint`, `make test`, `make build`, and `make check`
verify manifest privacy guardrails, Tesseract debug logging, bitmap decode
safety, HTTPS wrapper metadata, and docs.

The current focus is:

Priority:

- Preserve the Android app and JNI boundary
- Keep native OCR dependencies explicit
- Document Android SDK, NDK, and Gradle version assumptions
- Avoid changing recognition behavior without test material
- Keep Android backup disabled and native OCR debug logging off
- Keep generated NDK object files out of source control
- Keep camera captures from overwriting prior external-storage images
- Keep activity lifecycle and photo result paths free of stdout prints
- Keep image URI decode failures observable without stack trace dumps
- Keep shared image intents routed through explicit stream URI handling
- Keep share intent filters image-only for OCR entry points
- Keep shared image stream guards before OCR processing
- Keep the image open failure message visible for unreadable shared image URIs
- Keep OCR traineddata streams closed after asset-copy attempts
- Keep `make lint`, `make test`, `make build`, and `make check` on the
  SDK-free static baseline

Next priorities:

- Add setup notes for the required Android and NDK toolchain
- Document where trained OCR data should live and how it is licensed
- Add explicit cleanup guidance for timestamped capture files
- Add a small fixture-based smoke test for OCR initialization
- Modernize Gradle and Android plugin versions in a dedicated compatibility pass

Contribution rules:

- One PR = one focused build, JNI, OCR, or documentation change.
- Include device or emulator notes for runtime changes.
- Keep native dependency licenses visible.
- Do not mix modernization with behavior changes.
- Preserve shared image intent stream handling when changing OCR entry points.
- Preserve image-only share filters when changing manifest intent filters.
- Preserve shared image stream guards when changing shared-image OCR handling.
- Preserve the image open failure message when changing URI OCR.
- Preserve traineddata stream cleanup when changing OCR asset setup.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing
  manifest, OCR, or Gradle metadata changes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

OCR apps can process sensitive images and text. Future changes should keep all
sample processing local unless network behavior is explicit, documented, and
controlled by the user.
The image open failure message should keep unreadable shared image URIs visible
to the user without adding raw URI details to the UI.

## What We Will Not Merge (For Now)

- Silent image or text upload behavior
- Bundled trained data without license notes
- Native binary drops without source or provenance
- Broad Android rewrites that obscure the JNI learning path

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
