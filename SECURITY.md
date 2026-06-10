# Security Policy

## Supported Versions

The supported security scope for `ocr-scanner-android` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: An OCR Scanner for Android

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/ocr-scanner-android` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be an Android mobile application or sample. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Dependency manifests detected: build.gradle. Dependency updates should preserve lockfiles when present and avoid introducing packages without a clear maintenance reason.
- Run `make lint`, `make test`, `make build`, and `make check` after changing
  manifest permissions, OCR setup, image decode behavior, Gradle metadata, or
  security documentation.
- Camera images, external storage OCR data, and recognized text should be
  treated as private user data. Android backup must remain disabled and native
  OCR debug logging should stay off.
- Timestamped camera captures reduce accidental overwrites but remain private
  external-storage data.
- Activity lifecycle and photo result paths should not print OCR details to
  stdout.
- Image URI decode failures should use tagged Android logging instead of stack
  trace dumps.
- Shared image intents should require an image MIME type and `EXTRA_STREAM` URI
  before OCR processing.
- The share intent filter should stay image-only so unsupported text/plain
  content is not routed into OCR image handling.
- Shared image stream guards should stop OCR when an incoming image stream
  cannot be opened or decoded.
- The image open failure message should tell users when a shared image URI
  cannot be opened without exposing raw URI details.
- OCR traineddata streams should be closed after asset-copy attempts, and copy
  failures should use generic tagged logging.
- Generated NDK objects, APKs, local SDK paths, and signing material are local
  build outputs and must not be committed.

## Mobile Privacy Notes

If this project requests device permissions such as location, camera, microphone, contacts, Bluetooth, health data, or local storage access, reports should describe the permission involved and whether sensitive data can be accessed, persisted, or transmitted unexpectedly. Please avoid testing against real third-party user data or accounts you do not control.

## Dependency and Supply Chain Security

- The checked-in Gradle wrapper JAR is pinned by SHA-256 in the static baseline.
  Treat checksum changes as executable build-tool updates requiring provenance
  review.
- Pinned, read-only hosted Linux validation runs the same baseline used locally.

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
