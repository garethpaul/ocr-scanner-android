package com.garethpaul.scanr;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

public final class OCRTaskRunnerTest {
    public static void main(String[] args) throws Exception {
        final OCRTaskRunner runner = new OCRTaskRunner();
        final CountDownLatch workStarted = new CountDownLatch(1);
        final CountDownLatch releaseWork = new CountDownLatch(1);
        final CountDownLatch cleanupFinished = new CountDownLatch(1);
        final StringBuilder order = new StringBuilder();

        assertTrue(runner.execute(new Runnable() {
            public void run() {
                order.append("work");
                workStarted.countDown();
                await(releaseWork);
            }
        }), "initial OCR work should be accepted");
        assertTrue(workStarted.await(5, TimeUnit.SECONDS), "OCR work did not start");

        long startedAt = System.nanoTime();
        runner.close(new Runnable() {
            public void run() {
                order.append("-cleanup");
                cleanupFinished.countDown();
            }
        });
        long closeMillis = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startedAt);

        assertTrue(closeMillis < 250, "close must not block on active OCR work");
        assertTrue(!runner.execute(new Runnable() {
            public void run() {
                throw new AssertionError("closed runner accepted work");
            }
        }), "closed runner must reject new OCR work");

        releaseWork.countDown();
        assertTrue(cleanupFinished.await(5, TimeUnit.SECONDS), "cleanup did not finish");
        assertTrue("work-cleanup".equals(order.toString()),
                "native cleanup must run after accepted OCR work");
        System.out.println("OCRTaskRunner tests passed.");
    }

    private static void await(CountDownLatch latch) {
        try {
            latch.await();
        } catch (InterruptedException error) {
            Thread.currentThread().interrupt();
            throw new AssertionError("unexpected interruption");
        }
    }

    private static void assertTrue(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
