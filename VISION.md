## OCR Scanner Android Vision

OCR Scanner Android is a legacy Android sample for on-device optical character
recognition using native Tesseract and Leptonica bindings.

The repository is useful as a reference for wiring an Android app to JNI-based
OCR libraries, Gradle-era Android project structure, and packaged native
dependencies. Its value is in showing the integration boundaries clearly.

The goal is to make the sample reproducible and safe to study while separating
legacy build constraints from any future modernization work.

The current focus is:

Priority:

- Preserve the Android app and JNI boundary
- Keep native OCR dependencies explicit
- Document Android SDK, NDK, and Gradle version assumptions
- Avoid changing recognition behavior without test material

Next priorities:

- Add setup notes for the required Android and NDK toolchain
- Document where trained OCR data should live and how it is licensed
- Add a small fixture-based smoke test for OCR initialization
- Modernize Gradle and Android plugin versions in a dedicated compatibility pass

Contribution rules:

- One PR = one focused build, JNI, OCR, or documentation change.
- Include device or emulator notes for runtime changes.
- Keep native dependency licenses visible.
- Do not mix modernization with behavior changes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)


OCR apps can process sensitive images and text. Future changes should keep all
sample processing local unless network behavior is explicit, documented, and
controlled by the user.

## What We Will Not Merge (For Now)

- Silent image or text upload behavior
- Bundled trained data without license notes
- Native binary drops without source or provenance
- Broad Android rewrites that obscure the JNI learning path

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
