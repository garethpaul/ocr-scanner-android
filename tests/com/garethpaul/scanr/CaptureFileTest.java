package com.garethpaul.scanr;

import java.io.File;
import java.io.FileOutputStream;

public final class CaptureFileTest {
    public static void main(String[] args) throws Exception {
        File capture = File.createTempFile("ocr-capture-", ".jpg");
        FileOutputStream output = new FileOutputStream(capture);
        output.write(1);
        output.close();

        assertTrue(CaptureFile.delete(capture.getAbsolutePath()),
                "owned capture should be deleted");
        assertTrue(!capture.exists(), "deleted capture must not remain on disk");
        assertTrue(!CaptureFile.delete(null), "null capture path must be rejected");
        assertTrue(!CaptureFile.delete(""), "empty capture path must be rejected");
    }

    private static void assertTrue(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
