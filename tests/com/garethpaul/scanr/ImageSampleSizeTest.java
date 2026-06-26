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
        System.out.println("ImageSampleSize tests passed.");
    }

    private static void expect(int expected, int actual, String message) {
        if (expected != actual) {
            throw new AssertionError(message + ": expected " + expected
                    + ", got " + actual);
        }
    }
}
