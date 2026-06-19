package com.garethpaul.scanr;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ThreadFactory;

final class OCRTaskRunner {
    private final ExecutorService executor = Executors.newSingleThreadExecutor(
            new ThreadFactory() {
                public Thread newThread(Runnable runnable) {
                    return new Thread(runnable, "ocr-worker");
                }
            });
    private boolean closed;

    synchronized boolean execute(Runnable task) {
        if (closed) {
            return false;
        }
        try {
            executor.execute(task);
            return true;
        } catch (RejectedExecutionException error) {
            return false;
        }
    }

    synchronized void close(Runnable cleanup) {
        if (closed) {
            return;
        }
        closed = true;
        executor.execute(cleanup);
        executor.shutdown();
    }
}
