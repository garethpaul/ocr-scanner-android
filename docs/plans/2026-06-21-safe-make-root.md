# Safe Make Root

## Problem

Whitespace-splitting Make functions and caller-controlled `MAKEFILE_LIST`
values could redirect static, Java host, and mutation verification.

## Change

- Resolve the raw Makefile path with POSIX-compatible system tooling.
- Reject non-file origins for GNU Make's automatic `MAKEFILE_LIST` value.
- Add SDK-free regressions for spaces, a literal apostrophe, and injection.

## Validation

- Run static checks, Java host tests, hostile mutations, and root-policy tests.
- Confirm pinned Ubuntu CI and CodeQL pass at the exact pull-request head.
