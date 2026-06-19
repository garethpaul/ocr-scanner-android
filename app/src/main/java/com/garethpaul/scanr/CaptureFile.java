package com.garethpaul.scanr;

import java.io.File;

final class CaptureFile {
    private CaptureFile() {
    }

    static boolean delete(String path) {
        if (path == null || path.length() == 0) {
            return false;
        }
        try {
            File file = new File(path);
            return file.isFile() && file.delete();
        } catch (SecurityException error) {
            return false;
        }
    }
}
