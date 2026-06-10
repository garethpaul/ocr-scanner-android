# Hosted Static Validation

status: completed

## Context

The repository has an SDK-free baseline for its legacy Android and OCR safety
invariants, but no hosted validation. It also checks in a Gradle wrapper JAR,
which is executable build tooling without an integrity allowlist.

## Priorities

1. Run the canonical static gate on hosted Linux for pushes and pull requests.
2. Pin workflow actions, Python, permissions, runner, timeout, and concurrency.
3. Verify the checked-in Gradle wrapper JAR against a reviewed SHA-256 value.
4. Enforce the workflow contract from `scripts/check-baseline.py`.
5. Keep the obsolete Android build separate from the portable integrity gate.

## Implementation Units

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Add a commit-pinned, read-only Python 3.12 workflow that runs `make check` on
`ubuntu-24.04`. Hash the wrapper JAR before accepting the static baseline, and
require the hosted workflow contract from the checker.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted Linux `Check` workflow for the pushed commit

## Boundaries

- Do not execute or modernize the obsolete Android/Gradle toolchain in this pass.
- Do not replace native OCR binaries or trained data without provenance review.
- Do not change application behavior.
