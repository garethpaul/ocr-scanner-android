#!/usr/bin/env python3
"""Static baseline checks for the legacy Android OCR scanner."""

from pathlib import Path
import hashlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MAKEFILE = """ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint static-check test verify

PYTHON ?= python3

check: verify

verify: static-check

lint test build: static-check

static-check:
\tPYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check-baseline.py"
"""
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"
GRADLE_WRAPPER_SHA256 = "e2b82129ab64751fd40437007bd2f7f2afb3c6e41a9198e628650b22d5824a14"
HOSTED_VALIDATION_PLAN = "docs/plans/2026-06-10-hosted-static-validation.md"
UNIQUE_CAPTURE_PLAN = "docs/plans/2026-06-10-unique-camera-captures.md"
ORPHANED_GITLINK_PLAN = "docs/plans/2026-06-10-remove-orphaned-gitlink.md"
SHARED_IMAGE_ACCESS_PLAN = "docs/plans/2026-06-12-shared-image-access-denial.md"
CHECKOUT_CREDENTIAL_PLAN = "docs/plans/2026-06-12-checkout-credential-boundary.md"
TOOLCHAIN_PLAN = "docs/plans/2026-06-13-legacy-toolchain-notes.md"
LOCATION_INDEPENDENT_MAKE_PLAN = "docs/plans/2026-06-13-location-independent-make.md"
OCR_LIFECYCLE_PLAN = "docs/plans/2026-06-14-ocr-worker-lifecycle-guard.md"
LAUNCHER_OCR_PLAN = "docs/plans/2026-06-15-remove-unused-launcher-ocr.md"
LAUNCHER_PROGRESS_PLAN = "docs/plans/2026-06-15-remove-unused-launcher-progress.md"
OCR_RESULT_GENERATION_PLAN = "docs/plans/2026-06-15-ocr-result-generation-guard.md"
NONBLOCKING_OCR_TEARDOWN_PLAN = "docs/plans/2026-06-15-nonblocking-ocr-teardown.md"
SHARE_INTENT_RECREATION_PLAN = "docs/plans/2026-06-16-share-intent-recreation-guard.md"
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
    TOOLCHAIN_PLAN,
    LOCATION_INDEPENDENT_MAKE_PLAN,
    OCR_LIFECYCLE_PLAN,
    LAUNCHER_OCR_PLAN,
    LAUNCHER_PROGRESS_PLAN,
    OCR_RESULT_GENERATION_PLAN,
    NONBLOCKING_OCR_TEARDOWN_PLAN,
    SHARE_INTENT_RECREATION_PLAN,
    "docs/legacy-toolchain.md",
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
    if "bitmap == null" not in tess:
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
    for forbidden_launcher_ocr in [
        "private TessOCR mTessOCR;",
        "mTessOCR = new TessOCR()",
        "mTessOCR.onDestroy()",
    ]:
        if forbidden_launcher_ocr in main:
            failures.append(
                "MainActivity must not own an unused OCR engine: "
                + forbidden_launcher_ocr
            )
    for forbidden_launcher_progress in [
        "import android.app.ProgressDialog;",
        "private ProgressDialog mProgressDialog;",
    ]:
        if forbidden_launcher_progress in main:
            failures.append(
                "MainActivity must not retain unused progress dialog state: "
                + forbidden_launcher_progress
            )
    for phrase in [
        "mHandledSendIntent",
        "Intent.EXTRA_STREAM",
        'type.startsWith("image/")',
        'Log.e(TAG, "ACTION_SEND missing image stream")',
        "startActivity(resultIntent)",
    ]:
        if phrase not in main:
            failures.append(f"MainActivity shared image handling must include {phrase}")
    state_key = 'private static final String STATE_HANDLED_SEND_INTENT = "handledSendIntent";'
    restore_guard = "if (savedInstanceState != null)"
    restore_value = "mHandledSendIntent = savedInstanceState.getBoolean("
    on_save = main.split("protected void onSaveInstanceState(Bundle outState)", 1)[-1].split("\n\t}", 1)[0]
    on_resume = main.split("protected void onResume()", 1)[-1].split("\n\t}", 1)[0]
    restore_guard_index = main.find(restore_guard)
    restore_value_index = main.find(restore_value)
    restore_key_index = main.find("STATE_HANDLED_SEND_INTENT, false", restore_value_index)
    main_actionbar = main.find("getActionBar()")
    save_value_index = on_save.find(
        "outState.putBoolean(STATE_HANDLED_SEND_INTENT, mHandledSendIntent)"
    )
    save_super_index = on_save.find("super.onSaveInstanceState(outState)")
    resume_guard_index = on_resume.find(
        "if (!mHandledSendIntent && Intent.ACTION_SEND.equals(intent.getAction()))"
    )
    handled_index = on_resume.find("mHandledSendIntent = true", resume_guard_index)
    stream_index = on_resume.find("intent.getParcelableExtra(Intent.EXTRA_STREAM)")
    launch_index = on_resume.find("startActivity(resultIntent)")
    if not (
        main.count(state_key) == 1
        and main.count("protected void onSaveInstanceState(Bundle outState)") == 1
        and 0 <= main_super < restore_guard_index < restore_value_index < restore_key_index < main_actionbar
        and 0 <= save_value_index < save_super_index
        and 0 <= resume_guard_index < handled_index < stream_index < launch_index
    ):
        failures.append("MainActivity must preserve one-shot share handling across recreation")
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
    for phrase in [
        "private volatile boolean mDestroyed",
        "final TessOCR tessOCR = mTessOCR",
        "tessOCR.getOCRResult(bitmap)",
        "mProgressDialog = null",
        "mTessOCR = null",
    ]:
        if phrase not in result:
            failures.append(f"ResultActivity OCR lifecycle guard must include {phrase}")
    if result.count("new TessOCR()") != 1:
        failures.append("ResultActivity must remain the sole activity OCR engine owner")
    for required_result_progress in [
        "import android.app.ProgressDialog;",
        "private ProgressDialog mProgressDialog;",
        "mProgressDialog = ProgressDialog.show(",
        "mProgressDialog.dismiss()",
    ]:
        if required_result_progress not in result:
            failures.append(
                "ResultActivity must retain active OCR progress ownership: "
                + required_result_progress
            )
    if result.count("if (mDestroyed)") < 2:
        failures.append("ResultActivity must guard both worker posting and UI result delivery after destruction")
    do_ocr = result.split("private void doOCR", 1)[-1].split("public void onWindowFocusChanged", 1)[0]
    generation_capture_index = do_ocr.find("final int ocrGeneration = ++mOCRGeneration")
    worker_generation_index = do_ocr.find("if (ocrGeneration != mOCRGeneration)")
    ui_handoff_index = do_ocr.find("runOnUiThread(new Runnable()")
    ui_generation_index = do_ocr.find("if (ocrGeneration != mOCRGeneration)", worker_generation_index + 1)
    result_mutation_index = do_ocr.find("mResult.setText(result)")
    progress_dismiss_index = do_ocr.find("mProgressDialog.dismiss()")
    if not (
        "private volatile int mOCRGeneration;" in result
        and 0 <= generation_capture_index < worker_generation_index < ui_handoff_index
        and ui_handoff_index < ui_generation_index < result_mutation_index
        and ui_generation_index < progress_dismiss_index
        and do_ocr.count("if (ocrGeneration != mOCRGeneration)") == 2
    ):
        failures.append("ResultActivity must reject stale OCR generations before worker handoff and UI mutation")
    destroyed_index = result.find("mDestroyed = true")
    generation_invalidation_index = result.find("mOCRGeneration++", destroyed_index)
    dialog_index = result.find("mProgressDialog.dismiss()", destroyed_index)
    dialog_clear_index = result.find("mProgressDialog = null", dialog_index)
    wrapper_capture_index = result.find("final TessOCR tessOCR = mTessOCR", destroyed_index)
    wrapper_clear_index = result.find("mTessOCR = null", wrapper_capture_index)
    teardown_thread_index = result.find("new Thread(new Runnable()", wrapper_clear_index)
    teardown_index = result.find("tessOCR.onDestroy()", teardown_thread_index)
    teardown_name_index = result.find('}, "ocr-teardown").start()', teardown_index)
    super_destroy_index = result.find("super.onDestroy()", destroyed_index)
    if not (
        destroyed_index != -1
        and generation_invalidation_index > destroyed_index
        and dialog_index > generation_invalidation_index
        and dialog_clear_index > dialog_index
        and wrapper_capture_index > dialog_clear_index
        and wrapper_clear_index > wrapper_capture_index
        and teardown_thread_index > wrapper_clear_index
        and teardown_index > teardown_thread_index
        and teardown_name_index > teardown_index
        and super_destroy_index > teardown_name_index
        and "mTessOCR.onDestroy()" not in result
    ):
        failures.append("ResultActivity destruction must detach OCR and schedule named serialized teardown before super")

    tess_ocr = read("app/src/main/java/com/garethpaul/scanr/TessOCR.java")
    for phrase in [
        "public synchronized String getOCRResult(Bitmap bitmap)",
        "if (bitmap == null || mTess == null)",
        "public synchronized void onDestroy()",
        "mTess.end()",
        "mTess = null",
    ]:
        if phrase not in tess_ocr:
            failures.append(f"TessOCR lifecycle ownership must include {phrase}")

    wrapper = read("gradle/wrapper/gradle-wrapper.properties")
    if "https\\://services.gradle.org/distributions/gradle-2.2.1-all.zip" not in wrapper:
        failures.append("Gradle wrapper URL must stay HTTPS")
    wrapper_jar = (ROOT / "gradle/wrapper/gradle-wrapper.jar").read_bytes()
    if hashlib.sha256(wrapper_jar).hexdigest() != GRADLE_WRAPPER_SHA256:
        failures.append("Gradle wrapper JAR checksum changed without a reviewed baseline update")

    root_gradle = read("build.gradle")
    app_gradle = read("app/build.gradle")
    native_application = read("jni/Application.mk")
    for path, text, phrases in [
        ("build.gradle", root_gradle, ["com.android.tools.build:gradle:1.1.0", "jcenter()"]),
        ("app/build.gradle", app_gradle, [
            "compileSdkVersion 21",
            'buildToolsVersion "22.0.1"',
            "minSdkVersion 18",
            "targetSdkVersion 18",
            "com.android.support:support-v4:21.0.3",
            "libs/classes.jar",
        ]),
        ("jni/Application.mk", native_application, [
            "APP_STL := gnustl_static",
            "APP_ABI := armeabi armeabi-v7a x86 mips",
        ]),
    ]:
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{path} must retain declared legacy toolchain value {phrase}")

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
    if makefile != EXPECTED_MAKEFILE:
        failures.append(
            "Makefile must exactly preserve rooted SDK-free aliases and the Python override"
        )

    readme = read("README.md")
    docs = " ".join("\n".join(
        [readme, read("SECURITY.md"), read("VISION.md")]
    ).split())
    location_independent_make_plan = read(LOCATION_INDEPENDENT_MAKE_PLAN)
    if "make -f /path/to/ocr-scanner-android/Makefile check" not in readme:
        failures.append("README must document location-independent Makefile invocation")
    if not all(
        evidence in location_independent_make_plan.lower()
        for evidence in [
            "status: completed",
            "root and external-directory",
            "six isolated hostile mutations",
        ]
    ):
        failures.append(
            "location-independent Make plan must record completed root, external, and mutation verification"
        )
    for phrase in ["make lint", "make test", "make build", "make check", "OCR", "external storage", "allowBackup", "generated NDK", "timestamped", "stdout", "stack trace", "shared image", "image-only", "shared image stream", "image open failure message", "denied shared image access", "traineddata streams", "Gradle wrapper JAR", "hosted Linux", "OCR worker lifecycle guard", "native OCR engine ownership", "launcher progress state"]:
        if phrase.lower() not in docs.lower():
            failures.append(f"docs must mention {phrase}")
    guidance_documents = [
        read(path).lower() for path in ["README.md", "SECURITY.md", "VISION.md"]
    ]
    if not all("native ocr engine ownership" in document for document in guidance_documents):
        failures.append("all guidance must keep the result-screen OCR ownership boundary")
    if not all("launcher progress state" in document for document in guidance_documents):
        failures.append("all guidance must document removal of unused launcher progress state")
    for path in ["README.md", "SECURITY.md", "VISION.md", "CHANGES.md"]:
        if "share intent recreation guard" not in read(path).lower():
            failures.append(f"{path} must document the share intent recreation guard")

    toolchain = " ".join(read("docs/legacy-toolchain.md").split())
    for phrase in [
        "Verification status: declared metadata only; Android and JNI rebuild not run",
        "gradle-2.2.1-all.zip",
        "com.android.tools.build:gradle:1.1.0",
        "compile SDK: 21",
        "Android build tools: 22.0.1",
        "minimum SDK: 18",
        "target SDK: 18",
        "com.android.support:support-v4:21.0.3",
        "app/libs/classes.jar",
        "dependency repository: JCenter",
        "does not pin an exact JDK version",
        "does not pin an exact NDK version",
        "gnustl_static",
        "armeabi-v7a",
        "They do not invoke Gradle",
    ]:
        if phrase not in toolchain:
            failures.append(f"legacy toolchain note must include {phrase}")
    if "[`docs/legacy-toolchain.md`](docs/legacy-toolchain.md)" not in read("README.md"):
        failures.append("README must link the legacy toolchain note")

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

    toolchain_plan = read(TOOLCHAIN_PLAN)
    toolchain_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", toolchain_plan)
    toolchain_work = markdown_section(toolchain_plan, "Work Completed")
    toolchain_verification = markdown_section(toolchain_plan, "Verification Completed")
    if toolchain_status != ["completed"] or not toolchain_work:
        failures.append("legacy toolchain plan must record completed status and work")
    if not toolchain_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", toolchain_verification
    ):
        failures.append("legacy toolchain plan must record completed verification")
    for evidence in [
        "python3 -m py_compile scripts/check-baseline.py",
        "make lint",
        "make test",
        "make build",
        "make check",
        "external working directory",
        "hostile mutations rejected",
        "protected build paths had no diff",
        "git diff --check",
    ]:
        if evidence not in toolchain_verification:
            failures.append(f"legacy toolchain verification must record {evidence}")

    lifecycle_plan = read(OCR_LIFECYCLE_PLAN)
    lifecycle_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", lifecycle_plan)
    lifecycle_work = markdown_section(lifecycle_plan, "Work Completed")
    lifecycle_verification = markdown_section(lifecycle_plan, "Verification Completed")
    if (lifecycle_status != ["completed"] or not lifecycle_work or
            not lifecycle_verification or re.search(
                r"(?i)\b(?:pending|todo|tbd|not run|to be recorded)\b",
                lifecycle_verification,
            )):
        failures.append("OCR worker lifecycle plan must record completed work and verification")
    for evidence in [
        "python3 -m py_compile scripts/check-baseline.py",
        "make lint",
        "make test",
        "make build",
        "make check",
        "external working directory",
        "hostile mutations",
        "git diff --check",
    ]:
        if evidence not in lifecycle_verification:
            failures.append(f"OCR worker lifecycle verification must record {evidence}")

    launcher_ocr_plan = read(LAUNCHER_OCR_PLAN)
    launcher_ocr_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", launcher_ocr_plan)
    launcher_ocr_work = markdown_section(launcher_ocr_plan, "Work Completed")
    launcher_ocr_verification = markdown_section(
        launcher_ocr_plan, "Verification Completed"
    )
    if (launcher_ocr_status != ["completed"] or not launcher_ocr_work or
            not launcher_ocr_verification or re.search(
                r"(?i)\b(?:pending|todo|tbd|not run|to be recorded)\b",
                launcher_ocr_verification,
            )):
        failures.append("launcher OCR ownership plan must record completed work and verification")
    for evidence in [
        "python3 -m py_compile scripts/check-baseline.py",
        "make lint",
        "make test",
        "make build",
        "make check",
        "external working directory",
        "Six isolated hostile mutations",
        "git diff --check",
        "protected Gradle, manifest, JNI, wrapper, asset, and binary path checks",
    ]:
        if evidence not in launcher_ocr_verification:
            failures.append(f"launcher OCR ownership verification must record {evidence}")

    launcher_progress_plan = read(LAUNCHER_PROGRESS_PLAN)
    launcher_progress_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", launcher_progress_plan)
    launcher_progress_work = markdown_section(launcher_progress_plan, "Work Completed")
    launcher_progress_verification = markdown_section(
        launcher_progress_plan, "Verification Completed"
    )
    if (launcher_progress_status != ["completed"] or not launcher_progress_work or
            not launcher_progress_verification or re.search(
                r"(?i)\b(?:pending|todo|tbd|not run|to be recorded)\b",
                launcher_progress_verification,
            )):
        failures.append("launcher progress cleanup plan must record completed work and verification")
    for evidence in [
        "python3 -m py_compile scripts/check-baseline.py",
        "make lint",
        "make test",
        "make build",
        "make check",
        "external working directory",
        "Five isolated hostile mutations",
        "git diff --check",
        "protected Gradle, manifest, JNI, wrapper, asset, and binary path checks",
    ]:
        if evidence not in launcher_progress_verification:
            failures.append(f"launcher progress cleanup verification must record {evidence}")

    result_generation_plan = read(OCR_RESULT_GENERATION_PLAN)
    result_generation_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", result_generation_plan)
    result_generation_verification = markdown_section(
        result_generation_plan, "Verification Completed"
    )
    if (result_generation_status != ["completed"] or
            "All four Make gates passed" not in result_generation_verification or
            "Seven isolated hostile mutations were rejected" not in result_generation_verification or
            "external directory" not in result_generation_verification or
            re.search(r"(?i)\b(?:pending|todo|tbd|not run|to be recorded)\b",
                      result_generation_verification)):
        failures.append("OCR result generation guard plan must record completed verification")
    for path in ["README.md", "SECURITY.md", "VISION.md", "CHANGES.md"]:
        if "ocr result generation guard" not in read(path).lower():
            failures.append(f"{path} must document the OCR result generation guard")

    nonblocking_teardown_plan = read(NONBLOCKING_OCR_TEARDOWN_PLAN)
    nonblocking_teardown_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", nonblocking_teardown_plan
    )
    nonblocking_teardown_verification = markdown_section(
        nonblocking_teardown_plan, "Verification Completed"
    )
    if (nonblocking_teardown_status != ["completed"] or
            "All four Make gates passed" not in nonblocking_teardown_verification or
            "Seven isolated hostile mutations were rejected" not in nonblocking_teardown_verification or
            "external directory" not in nonblocking_teardown_verification or
            re.search(r"(?i)\b(?:pending|todo|tbd|not run|to be recorded)\b",
                      nonblocking_teardown_verification)):
        failures.append("nonblocking OCR teardown plan must record completed verification")
    for path in ["README.md", "SECURITY.md", "VISION.md", "CHANGES.md"]:
        if "nonblocking ocr teardown" not in read(path).lower():
            failures.append(f"{path} must document nonblocking OCR teardown")

    share_recreation_plan = read(SHARE_INTENT_RECREATION_PLAN)
    share_recreation_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", share_recreation_plan
    )
    share_recreation_verification = markdown_section(
        share_recreation_plan, "Verification Completed"
    )
    if (share_recreation_status != ["completed"] or
            "All four Make gates passed" not in share_recreation_verification or
            "Eight isolated hostile mutations were rejected" not in share_recreation_verification or
            "external directory" not in share_recreation_verification or
            re.search(r"(?i)\b(?:pending|todo|tbd|not run|to be recorded)\b",
                      share_recreation_verification)):
        failures.append("share intent recreation guard plan must record completed verification")

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
