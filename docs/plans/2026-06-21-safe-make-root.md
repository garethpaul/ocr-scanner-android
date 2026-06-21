# Safe Make Root

## Problem

Whitespace-splitting Make functions and caller-controlled `MAKEFILE_LIST`
values could redirect static, Java host, and mutation verification.

## Change

- Resolve the raw Makefile path with POSIX-compatible system tooling.
- Reject non-file origins for GNU Make's automatic `MAKEFILE_LIST` value.
- Add SDK-free regressions for every public alias, spaces, a literal
  apostrophe, command-line and environment `ROOT`, and command-line and
  environment `MAKEFILE_LIST` injection.

## Validation

- Run static checks, Java host tests, hostile mutations, and root-policy tests.
- Confirm all nine public Make aliases retain the checkout-derived root under
  command-line and environment override attempts.
- Confirm pinned Ubuntu CI and CodeQL pass at the exact pull-request head.
