---
title: Bounded Shared Image Decode
status: completed
date: 2026-06-26
---

# Bounded Shared Image Decode

## Problem

Camera files were sampled before OCR, but shared content URIs used a direct
`BitmapFactory.decodeStream` call. A valid high-resolution shared image could
therefore allocate its full bitmap and exhaust the legacy app process before
OCR began.

## Decision

- Read shared-image dimensions without allocating pixels.
- Calculate the smallest power-of-two sample that bounds both axes to the
  reviewed 500-by-500 target, using long arithmetic for hostile dimensions.
- Reopen the content URI only after the sample is configured and close both
  streams with generic logs.
- Reuse the helper for camera-file decoding so both OCR entry paths share the
  same dimension policy.
- Keep URI permission, failure messaging, capture deletion, OCR generation,
  worker teardown, and legacy toolchain behavior unchanged.

## Verification Completed

- The host test initially failed because `ImageSampleSize` did not exist.
- Dependency-free Java tests passed for invalid, target-sized, wide, two-axis,
  and `Integer.MAX_VALUE` dimensions.
- All four Make gates passed from the repository root, and the absolute
  Makefile gate passed from an external directory.
- Eight hostile baseline mutations were rejected, including bypassing bounded
  shared decoding and weakening the maximum-axis ratio to a minimum.
- Android SDK, APK build, emulator, device camera, shared content provider, and
  live native OCR execution were unavailable on this Linux host.

## Scope Boundaries

This change does not modernize the Android storage model, replace `file://`
camera output, update Tesseract or Gradle, change OCR language data, or claim a
runtime memory ceiling from static and host-only evidence.
