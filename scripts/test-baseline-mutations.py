#!/usr/bin/env python3
"""Prove that lifecycle and ownership contracts reject hostile mutations."""

from pathlib import Path
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts/check-baseline.py"
MUTATIONS = [
    (
        "app/src/main/AndroidManifest.xml",
        'android:launchMode="singleTop"',
        'android:launchMode="standard"',
        "singleTop for reliable onNewIntent delivery",
    ),
    (
        "app/src/main/java/com/garethpaul/scanr/MainActivity.java",
        "handleSendIntent(intent);",
        "// removed new-intent handoff",
        "preserve share and camera state",
    ),
    (
        "app/src/main/java/com/garethpaul/scanr/MainActivity.java",
        "trainedDataTemp.renameTo(trainedDataFile)",
        "trainedDataTemp.exists()",
        "atomically stage and clean failed traineddata copies",
    ),
    (
        "app/src/main/java/com/garethpaul/scanr/ResultActivity.java",
        "CaptureFile.delete(photoPath)",
        "photoPath.length() == 0",
        "delete consumed camera captures",
    ),
    (
        "app/src/main/java/com/garethpaul/scanr/OCRTaskRunner.java",
        "Executors.newSingleThreadExecutor",
        "Executors.newCachedThreadPool",
        "order cleanup after accepted work",
    ),
    (
        "app/src/main/java/com/garethpaul/scanr/ResultActivity.java",
        "if (mDestroyed || ocrGeneration != mOCRGeneration)",
        "if (mDestroyed)",
        "reject stale OCR generations",
    ),
]


def main():
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for relative_path, old, new, expected in MUTATIONS:
        path = ROOT / relative_path
        original = path.read_text(encoding="utf-8")
        if original.count(old) != 1:
            raise SystemExit(f"mutation target must occur once: {relative_path}: {old}")
        try:
            path.write_text(original.replace(old, new, 1), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER)],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
            )
        finally:
            path.write_text(original, encoding="utf-8")
        output = result.stdout + result.stderr
        if result.returncode == 0 or expected not in output:
            raise SystemExit(
                f"mutation survived: {relative_path}: {old}\n{output}"
            )
    print(f"{len(MUTATIONS)} hostile baseline mutations rejected.")


if __name__ == "__main__":
    main()
