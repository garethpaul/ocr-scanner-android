package com.garethpaul.scanr;

public final class ImageSampleSizeTest {
    public static void main(String[] args) {
        expect(0, ImageSampleSize.forBounds(0, 100, 500, 500),
                "reject zero width");
        expect(0, ImageSampleSize.forBounds(100, -1, 500, 500),
                "reject negative height");
        expect(1, ImageSampleSize.forBounds(500, 500, 500, 500),
                "retain target-sized image");
        expect(2, ImageSampleSize.forBounds(1000, 500, 500, 500),
                "bound wide image");
        expect(4, ImageSampleSize.forBounds(2000, 1200, 500, 500),
                "bound both dimensions with power-of-two sampling");
        expect(8388608,
                ImageSampleSize.forBounds(Integer.MAX_VALUE, Integer.MAX_VALUE,
                        500, 500),
                "avoid overflow for hostile dimensions");
        expect(1073741824,
                forBoundsWithinTimeout(Integer.MAX_VALUE, Integer.MAX_VALUE, 1, 1),
                "terminate for extreme target ratios");
        System.out.println("ImageSampleSize tests passed.");
    }

    // The existing 500x500 cases never reach the sampleSize <= Integer.MAX_VALUE / 2
    // bound. At targetWidth 1 the doubling overflows past 2^30 without it and the
    // loop never terminates, so run on a watched thread to turn a hang into a
    // failure rather than a CI timeout.
    private static int forBoundsWithinTimeout(final int width, final int height,
            final int targetWidth, final int targetHeight) {
        final int[] captured = new int[] { -1 };
        Thread worker = new Thread(new Runnable() {
            public void run() {
                captured[0] = ImageSampleSize.forBounds(width, height,
                        targetWidth, targetHeight);
            }
        });
        worker.setDaemon(true);
        worker.start();
        try {
            worker.join(5000);
        } catch (InterruptedException error) {
            Thread.currentThread().interrupt();
            throw new AssertionError("unexpected interruption");
        }
        if (worker.isAlive()) {
            throw new AssertionError(
                    "forBounds must terminate for extreme target ratios");
        }
        return captured[0];
    }

    private static void expect(int expected, int actual, String message) {
        if (expected != actual) {
            throw new AssertionError(message + ": expected " + expected
                    + ", got " + actual);
        }
    }
}
