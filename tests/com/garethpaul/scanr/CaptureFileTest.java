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
        assertTrue(!CaptureFile.delete(capture.getAbsolutePath()),
                "missing capture path must be rejected");

        File directory = File.createTempFile("ocr-capture-dir-", "");
        assertTrue(directory.delete(), "directory probe setup must clear the temp file");
        assertTrue(directory.mkdir(), "directory probe setup must create a directory");
        try {
            assertTrue(!CaptureFile.delete(directory.getAbsolutePath()),
                    "directory must not be reported as a deleted capture");
            assertTrue(directory.isDirectory(),
                    "directory must survive a capture delete attempt");
        } finally {
            directory.delete();
        }
        System.out.println("CaptureFile tests passed.");
    }

    private static void assertTrue(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
