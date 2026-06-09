#!/usr/bin/env python3
"""Static baseline checks for the legacy Android OCR scanner."""

from pathlib import Path
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
    "docs/plans/2026-06-09-timestamped-camera-captures.md",
    "docs/plans/2026-06-09-remove-activity-stdout.md",
    "docs/plans/2026-06-09-uri-error-logging.md",
    "docs/plans/2026-06-09-shared-image-intent.md",
    "docs/plans/2026-06-09-image-only-share-filter.md",
    "docs/plans/2026-06-09-shared-image-stream-guards.md",
    "docs/plans/2026-06-09-make-gate-aliases.md",
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
        manifest_text = read("app/src/main/AndroidManifest.xml")
        if 'android:mimeType="text/plain"' in manifest_text:
            failures.append("share intent filter must not advertise text/plain input")
        if 'android:mimeType="image/*"' not in manifest_text:
            failures.append("share intent filter must keep image/* input")
    except ET.ParseError as error:
        failures.append(f"AndroidManifest.xml must parse as XML: {error}")

    tess = read("app/src/main/java/com/garethpaul/scanr/TessOCR.java")
    if "mTess.setDebug(false)" not in tess:
        failures.append("TessOCR must keep native OCR debug logging disabled")
    if "System.out.println(DATA_PATH" in tess:
        failures.append("TessOCR must not print external storage paths")
    if "if (bitmap == null)" not in tess:
        failures.append("TessOCR must tolerate failed bitmap decodes")

    main = read("app/src/main/java/com/garethpaul/scanr/MainActivity.java")
    if "System.out.println" in main:
        failures.append("MainActivity must not print OCR lifecycle details to stdout")
    main_super = main.find("super.onCreate(savedInstanceState)")
    main_actionbar = main.find("getActionBar()")
    if main_super == -1 or main_actionbar == -1 or main_super > main_actionbar:
        failures.append("MainActivity must call super.onCreate before ActionBar access")
    if "if (ab != null)" not in main:
        failures.append("MainActivity must guard ActionBar access")
    if "if (mTessOCR != null)" not in main:
        failures.append("MainActivity must guard OCR cleanup")
    for phrase in [
        "mHandledSendIntent",
        "Intent.EXTRA_STREAM",
        'type.startsWith("image/")',
        'Log.e(TAG, "ACTION_SEND missing image stream")',
        "startActivity(resultIntent)",
    ]:
        if phrase not in main:
            failures.append(f"MainActivity shared image handling must include {phrase}")
    for phrase in [
        'new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US)',
        'String imageFileName = "JPEG_" + timeStamp',
        "if (!dir.exists() && !dir.mkdirs())",
        'new File(dir, imageFileName + ".jpg")',
    ]:
        if phrase not in main:
            failures.append(f"MainActivity camera capture files must include {phrase}")

    result = read("app/src/main/java/com/garethpaul/scanr/ResultActivity.java")
    if "System.out.println" in result:
        failures.append("ResultActivity must not print OCR lifecycle details to stdout")
    if "printStackTrace()" in result:
        failures.append("ResultActivity must not dump image handling stack traces")
    result_super = result.find("super.onCreate(savedInstanceState)")
    result_actionbar = result.find("getActionBar()")
    if result_super == -1 or result_actionbar == -1 or result_super > result_actionbar:
        failures.append("ResultActivity must call super.onCreate before ActionBar access")
    for phrase in [
        "if (ab != null)",
        "Math.max(1, Math.min",
        "Math.max(1, scaleFactor << 1)",
        "if (bitmap == null)",
        "Unable to decode image.",
        "if (mProgressDialog != null)",
        "if (mTessOCR != null)",
        'Log.e(TAG, "Unable to open image URI", e)',
        'Log.e(TAG, "Unable to close image URI stream", e)',
        "if (is == null)",
        'mResult.setText("Unable to open image.")',
        "extras.getParcelable(Intent.EXTRA_STREAM)",
        "uriOCR(imageUri)",
    ]:
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

    makefile = read("Makefile")
    for phrase in [
        ".PHONY: build check lint static-check test verify",
        "check: verify",
        "verify: static-check",
        "lint test build: static-check",
        "PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/check-baseline.py",
    ]:
        if phrase not in makefile:
            failures.append(f"Makefile must include standard gate alias: {phrase}")

    docs = "\n".join(read(path) for path in ["README.md", "SECURITY.md", "VISION.md"])
    for phrase in ["make lint", "make test", "make build", "make check", "OCR", "external storage", "allowBackup", "generated NDK", "timestamped", "stdout", "stack trace", "shared image", "image-only", "shared image stream"]:
        if phrase.lower() not in docs.lower():
            failures.append(f"docs must mention {phrase}")

    plan = read("docs/plans/2026-06-08-ocr-scanner-baseline.md")
    if "status: completed" not in plan or "make check" not in plan:
        failures.append("plan must record completed status and verification")
    capture_plan = read("docs/plans/2026-06-09-timestamped-camera-captures.md")
    if "status: completed" not in capture_plan or "timestamped" not in capture_plan:
        failures.append("capture plan must record completed status and verification")
    stdout_plan = read("docs/plans/2026-06-09-remove-activity-stdout.md")
    if "status: completed" not in stdout_plan or "stdout" not in stdout_plan:
        failures.append("stdout plan must record completed status and verification")
    uri_plan = read("docs/plans/2026-06-09-uri-error-logging.md")
    if "status: completed" not in uri_plan or "printStackTrace" not in uri_plan:
        failures.append("URI error logging plan must record completed status and verification")
    shared_image_plan = read("docs/plans/2026-06-09-shared-image-intent.md")
    if "status: completed" not in shared_image_plan or "shared image" not in shared_image_plan:
        failures.append("shared image intent plan must record completed status and verification")
    image_only_plan = read("docs/plans/2026-06-09-image-only-share-filter.md")
    if "status: completed" not in image_only_plan or "image-only" not in image_only_plan:
        failures.append("image-only share filter plan must record completed status and verification")
    shared_stream_plan = read("docs/plans/2026-06-09-shared-image-stream-guards.md")
    if "status: completed" not in shared_stream_plan or "shared image stream" not in shared_stream_plan:
        failures.append("shared image stream guard plan must record completed status and verification")
    make_gate_plan_path = ROOT / "docs/plans/2026-06-09-make-gate-aliases.md"
    make_gate_plan = make_gate_plan_path.read_text(encoding="utf-8") if make_gate_plan_path.exists() else ""
    if "status: completed" not in make_gate_plan or "make lint" not in make_gate_plan or "make build" not in make_gate_plan:
        failures.append("make gate alias plan must record completed status and verification")

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
