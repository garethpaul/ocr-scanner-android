package com.garethpaul.scanr;

final class ImageSampleSize {
    private ImageSampleSize() {
    }

    static int forBounds(int width, int height, int targetWidth,
            int targetHeight) {
        if (width <= 0 || height <= 0 || targetWidth <= 0 || targetHeight <= 0) {
            return 0;
        }

        long widthRatio = ((long) width + targetWidth - 1) / targetWidth;
        long heightRatio = ((long) height + targetHeight - 1) / targetHeight;
        long requiredRatio = Math.max(widthRatio, heightRatio);
        int sampleSize = 1;

        while (sampleSize < requiredRatio
                && sampleSize <= Integer.MAX_VALUE / 2) {
            sampleSize *= 2;
        }
        return sampleSize;
    }
}
