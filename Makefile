ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); /usr/bin/dirname -- "$$path")

.PHONY: build check host-test lint mutation-test root-test static-check test verify

PYTHON ?= python3

check: verify

verify: static-check host-test mutation-test root-test

lint build: static-check

test: static-check host-test

host-test:
	"$(ROOT)/scripts/run-host-tests.sh"

mutation-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/test-baseline-mutations.py"

root-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/test-makefile-root.py"

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check-baseline.py"
