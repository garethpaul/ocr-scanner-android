#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BUILD_DIR=${TMPDIR:-/tmp}/ocr-scanner-host-tests-$$
trap 'rm -rf "$BUILD_DIR"' EXIT HUP INT TERM

mkdir -p "$BUILD_DIR"
javac -d "$BUILD_DIR" \
  "$ROOT/app/src/main/java/com/garethpaul/scanr/CaptureFile.java" \
  "$ROOT/app/src/main/java/com/garethpaul/scanr/OCRTaskRunner.java" \
  "$ROOT/tests/com/garethpaul/scanr/CaptureFileTest.java" \
  "$ROOT/tests/com/garethpaul/scanr/OCRTaskRunnerTest.java"

java -cp "$BUILD_DIR" com.garethpaul.scanr.CaptureFileTest
java -cp "$BUILD_DIR" com.garethpaul.scanr.OCRTaskRunnerTest
