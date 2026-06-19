ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check host-test lint mutation-test static-check test verify

PYTHON ?= python3

check: verify

verify: static-check host-test mutation-test

lint build: static-check

test: static-check host-test

host-test:
	"$(ROOT)/scripts/run-host-tests.sh"

mutation-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/test-baseline-mutations.py"

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check-baseline.py"
