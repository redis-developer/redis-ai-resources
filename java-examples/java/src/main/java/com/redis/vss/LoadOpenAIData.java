package com.redis.vss;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;

import org.apache.commons.io.IOUtils;
import org.apache.commons.io.input.CountingInputStream;

import me.tongfei.progressbar.ProgressBar;
import me.tongfei.progressbar.ProgressBarBuilder;
import me.tongfei.progressbar.ProgressBarStyle;
import net.lingala.zip4j.ZipFile;

public class LoadOpenAIData {

    
    /** 
     * @param fileUrl
     * @param file
     * @throws IOException
     */
    public static void downloadUsingNIO(String fileUrl, String file) throws IOException {

        try {
            URL url = (new URI(fileUrl)).toURL();
            HttpURLConnection httpConnection = (HttpURLConnection) (url.openConnection());
            long completeFileSize = httpConnection.getContentLength();
            InputStream inputStream = url.openStream();
            CountingInputStream cis = new CountingInputStream(inputStream);
            FileOutputStream fileOS = new FileOutputStream(file);

            ProgressBarBuilder pbb = new ProgressBarBuilder()
                    .setInitialMax(Math.floorDiv(completeFileSize, 1000))
                    .setStyle(ProgressBarStyle.ASCII)
                    .setTaskName(file)
                    .setUnit("KB", 1)
                    .setUpdateIntervalMillis(1000)
                    .showSpeed();
            ProgressBar pb = pbb.build();

            new Thread(() -> {
                try {
                    IOUtils.copy(cis, fileOS);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }).start();

            while (cis.getByteCount() < completeFileSize) {
                pb.stepTo(Math.floorDiv(cis.getByteCount(), 1000));
            }

            pb.stepTo(Math.floorDiv(cis.getByteCount(), 1000));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    
    /** 
     * @param source
     * @param target
     * @throws IOException
     */
    public static void unzipZip4j(String source, String target)
            throws IOException {

        ZipFile sourceFile = new ZipFile(new File(source));
        sourceFile.extractAll(target);
    }
}
