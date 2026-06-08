#!/usr/bin/env python3
"""Static baseline checks for the legacy Android OCR scanner."""

from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"
REQUIRED = [
    ".gitignore",
    "CHANGES.md",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "app/build.gradle",
    "app/src/main/AndroidManifest.xml",
    "app/src/main/java/com/garethpaul/scanr/MainActivity.java",
    "app/src/main/java/com/garethpaul/scanr/ResultActivity.java",
    "app/src/main/java/com/garethpaul/scanr/TessOCR.java",
    "docs/plans/2026-06-08-ocr-scanner-baseline.md",
    "docs/readme-overview.svg",
    "gradle/wrapper/gradle-wrapper.properties",
]


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def main():
    failures = []
    for path in REQUIRED:
        if not (ROOT / path).is_file():
            failures.append(f"required file missing: {path}")

    manifest_path = ROOT / "app/src/main/AndroidManifest.xml"
    try:
        manifest = ET.parse(manifest_path).getroot()
        application = manifest.find("application")
        if application is None or application.attrib.get(ANDROID_NS + "allowBackup") != "false":
            failures.append("Android manifest must disable backup for OCR image/text data")
        permissions = {
            node.attrib.get(ANDROID_NS + "name")
            for node in manifest.findall("uses-permission")
        }
        if "android.permission.STORAGE" in permissions:
            failures.append("manifest must not request the invalid android.permission.STORAGE permission")
        for permission in ["android.permission.READ_EXTERNAL_STORAGE", "android.permission.WRITE_EXTERNAL_STORAGE"]:
            if permission not in permissions:
                failures.append(f"manifest must explicitly document legacy {permission} usage")
    except ET.ParseError as error:
        failures.append(f"AndroidManifest.xml must parse as XML: {error}")

    tess = read("app/src/main/java/com/garethpaul/scanr/TessOCR.java")
    if "mTess.setDebug(false)" not in tess:
        failures.append("TessOCR must keep native OCR debug logging disabled")
    if "System.out.println(DATA_PATH" in tess:
        failures.append("TessOCR must not print external storage paths")

    result = read("app/src/main/java/com/garethpaul/scanr/ResultActivity.java")
    for phrase in ["Math.max(1, Math.min", "Math.max(1, scaleFactor << 1)", "if (bitmap != null)"]:
        if phrase not in result:
            failures.append(f"ResultActivity bitmap decode must include {phrase}")

    wrapper = read("gradle/wrapper/gradle-wrapper.properties")
    if "https\\://services.gradle.org/distributions/gradle-2.2.1-all.zip" not in wrapper:
        failures.append("Gradle wrapper URL must stay HTTPS")

    gitignore = read(".gitignore")
    for expected in ["local.properties", ".gradle", "build/", "obj/", "*.apk", "*.jks", "*.keystore"]:
        if expected not in gitignore:
            failures.append(f".gitignore must include {expected}")

    tracked_obj = subprocess.run(
        ["git", "ls-files", "obj"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if tracked_obj:
        failures.append("generated NDK obj files must not be tracked: " + ", ".join(tracked_obj[:5]))

    docs = "\n".join(read(path) for path in ["README.md", "SECURITY.md", "VISION.md"])
    for phrase in ["make check", "OCR", "external storage", "allowBackup", "generated NDK"]:
        if phrase.lower() not in docs.lower():
            failures.append(f"docs must mention {phrase}")

    plan = read("docs/plans/2026-06-08-ocr-scanner-baseline.md")
    if "status: completed" not in plan or "make check" not in plan:
        failures.append("plan must record completed status and verification")

    try:
        ET.parse(ROOT / "docs/readme-overview.svg")
    except ET.ParseError as error:
        failures.append(f"docs/readme-overview.svg must parse as XML: {error}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("ocr-scanner-android baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
