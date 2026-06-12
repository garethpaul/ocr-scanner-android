#!/usr/bin/env python3
"""Static baseline checks for the legacy Android OCR scanner."""

from pathlib import Path
import hashlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"
GRADLE_WRAPPER_SHA256 = "e2b82129ab64751fd40437007bd2f7f2afb3c6e41a9198e628650b22d5824a14"
HOSTED_VALIDATION_PLAN = "docs/plans/2026-06-10-hosted-static-validation.md"
UNIQUE_CAPTURE_PLAN = "docs/plans/2026-06-10-unique-camera-captures.md"
ORPHANED_GITLINK_PLAN = "docs/plans/2026-06-10-remove-orphaned-gitlink.md"
SHARED_IMAGE_ACCESS_PLAN = "docs/plans/2026-06-12-shared-image-access-denial.md"
CHECKOUT_CREDENTIAL_PLAN = "docs/plans/2026-06-12-checkout-credential-boundary.md"
REQUIRED = [
    ".github/workflows/check.yml",
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
    "docs/plans/2026-06-09-traineddata-stream-cleanup.md",
    "docs/plans/2026-06-10-image-open-failure-message.md",
    HOSTED_VALIDATION_PLAN,
    UNIQUE_CAPTURE_PLAN,
    ORPHANED_GITLINK_PLAN,
    SHARED_IMAGE_ACCESS_PLAN,
    CHECKOUT_CREDENTIAL_PLAN,
    "docs/readme-overview.svg",
    "gradle/wrapper/gradle-wrapper.jar",
    "gradle/wrapper/gradle-wrapper.properties",
]


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def markdown_section(text, heading):
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


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
        'File.createTempFile(imageFileName + "_", ".jpg", dir)',
        'Log.e(TAG, "Unable to create camera image")',
    ]:
        if phrase not in main:
            failures.append(f"MainActivity camera capture files must include {phrase}")
    if 'new File(dir, imageFileName + ".jpg")' in main:
        failures.append("MainActivity camera captures must not reuse second-resolution paths")
    for phrase in [
        "InputStream in = null",
        "OutputStream out = null",
        'closeQuietly(out, "Unable to close OCR traineddata output")',
        'closeQuietly(in, "Unable to close OCR traineddata asset")',
        "private void closeQuietly(Closeable closeable, String message)",
    ]:
        if phrase not in main:
            failures.append(f"MainActivity traineddata stream cleanup must include {phrase}")
    if "e.toString()" in main:
        failures.append("MainActivity must not append raw exception details to OCR traineddata logs")

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
        'Log.e(TAG, "Unable to open image URI")',
        'catch (SecurityException e)',
        'Log.e(TAG, "Image URI access denied")',
        'Log.e(TAG, "Unable to close image URI stream")',
        "if (is == null)",
        'mResult.setText("Unable to open image.")',
        "extras.getParcelable(Intent.EXTRA_STREAM)",
        "uriOCR(imageUri)",
    ]:
        if phrase not in result:
            failures.append(f"ResultActivity bitmap decode must include {phrase}")
    if (
        "catch (FileNotFoundException e)" not in result
        or result.count('mResult.setText("Unable to open image.")') < 3
    ):
        failures.append("ResultActivity must show a user-facing message when image URI opening fails")
    for unsafe_log in [
        'Log.e(TAG, "Unable to open image URI", e)',
        'Log.e(TAG, "Image URI access denied", e)',
        'Log.e(TAG, "Unable to close image URI stream", e)',
    ]:
        if unsafe_log in result:
            failures.append("ResultActivity image URI logs must not include exception payloads")

    wrapper = read("gradle/wrapper/gradle-wrapper.properties")
    if "https\\://services.gradle.org/distributions/gradle-2.2.1-all.zip" not in wrapper:
        failures.append("Gradle wrapper URL must stay HTTPS")
    wrapper_jar = (ROOT / "gradle/wrapper/gradle-wrapper.jar").read_bytes()
    if hashlib.sha256(wrapper_jar).hexdigest() != GRADLE_WRAPPER_SHA256:
        failures.append("Gradle wrapper JAR checksum changed without a reviewed baseline update")

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

    tracked_gitlinks = [
        line
        for line in subprocess.run(
            ["git", "ls-files", "--stage"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        if line.startswith("160000 ")
    ]
    if tracked_gitlinks:
        failures.append("repository must not track orphaned gitlinks without submodule metadata")

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
    for phrase in ["make lint", "make test", "make build", "make check", "OCR", "external storage", "allowBackup", "generated NDK", "timestamped", "stdout", "stack trace", "shared image", "image-only", "shared image stream", "image open failure message", "denied shared image access", "traineddata streams", "Gradle wrapper JAR", "hosted Linux"]:
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
    traineddata_stream_plan = read("docs/plans/2026-06-09-traineddata-stream-cleanup.md")
    if "status: completed" not in traineddata_stream_plan or "traineddata streams" not in traineddata_stream_plan:
        failures.append("traineddata stream cleanup plan must record completed status and verification")
    image_open_message_plan = read("docs/plans/2026-06-10-image-open-failure-message.md")
    if "status: completed" not in image_open_message_plan or "image open failure message" not in image_open_message_plan.lower():
        failures.append("image open failure message plan must record completed status and verification")
    hosted_plan = read(HOSTED_VALIDATION_PLAN)
    workflow = read(".github/workflows/check.yml")
    workflow_files = [
        *sorted((ROOT / ".github/workflows").glob("*.yml")),
        *sorted((ROOT / ".github/workflows").glob("*.yaml")),
    ]
    if "status: completed" not in hosted_plan or "wrapper JAR" not in hosted_plan:
        failures.append("hosted static validation plan must record completed status and wrapper verification")
    unique_capture_plan = read(UNIQUE_CAPTURE_PLAN)
    if "status: completed" not in unique_capture_plan or "File.createTempFile" not in unique_capture_plan:
        failures.append("unique camera capture plan must record completed status and verification")
    orphaned_gitlink_plan = read(ORPHANED_GITLINK_PLAN)
    if "status: completed" not in orphaned_gitlink_plan or "tesseract-android-tools" not in orphaned_gitlink_plan:
        failures.append("orphaned gitlink plan must record completed status and verification")
    shared_image_access_plan = read(SHARED_IMAGE_ACCESS_PLAN)
    shared_image_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", shared_image_access_plan)
    shared_image_work = markdown_section(shared_image_access_plan, "Work Completed")
    shared_image_verification = markdown_section(shared_image_access_plan, "Verification Completed")
    if shared_image_status != ["completed"] or not shared_image_work:
        failures.append("shared image access denial plan must record one completed status and completed work")
    if not shared_image_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", shared_image_verification
    ):
        failures.append("shared image access denial plan must record completed verification")
    for evidence in [
        "make lint",
        "make test",
        "make build",
        "make check",
        "git diff --check",
        "python3 -m py_compile scripts/check-baseline.py",
        "27398025031",
        "27398031226",
        "bbe4ce1f337f73f27477849a195bf732bcdfe5fb",
        "catch (SecurityException e)",
        'Log.e(TAG, "Image URI access denied")',
        'mResult.setText("Unable to open image.")',
    ]:
        if evidence not in shared_image_verification:
            failures.append(f"shared image access verification must record {evidence}")
    for expected in [
        "permissions:\n  contents: read",
        "cancel-in-progress: true",
        "runs-on: ubuntu-24.04",
        "timeout-minutes: 10",
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        'python-version: "3.12"',
        "run: make check",
    ]:
        if expected not in workflow:
            failures.append(f"Check workflow must keep {expected}")

    checkout_action = (
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10"
    )
    checkout_blocks = re.findall(
        rf"(?m)^(?P<indent> *)- +uses: +{re.escape(checkout_action)}[^\n]*\n"
        rf"(?P=indent)  with:\n"
        rf"(?P=indent)    persist-credentials: +false *$",
        workflow,
    )
    checkout_actions = re.findall(
        r"(?m)^\s*-\s+uses:\s+actions/checkout@",
        workflow,
    )
    if not (
        len(workflow_files) == 1
        and workflow.count("permissions:") == 1
        and workflow.count("contents: read") == 1
        and not re.search(r"(?m)^\s*[A-Za-z-]+:\s*write\s*$", workflow)
        and len(checkout_actions) == 1
        and workflow.count(checkout_action) == 1
        and len(checkout_blocks) == 1
        and workflow.count("persist-credentials: false") == 1
        and "persist-credentials: true" not in workflow
    ):
        failures.append(
            "Check workflow must keep one read-only permission block and one "
            "pinned, credential-free checkout"
        )

    checkout_plan = read(CHECKOUT_CREDENTIAL_PLAN)
    checkout_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", checkout_plan)
    checkout_work = markdown_section(checkout_plan, "Work Completed")
    checkout_verification = markdown_section(checkout_plan, "Verification Completed")
    if not (
        checkout_status == ["completed"]
        and checkout_work
        and "make check" in checkout_verification
    ):
        failures.append(
            "checkout credential plan must record one completed status, "
            "completed work, and make check verification"
        )

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
