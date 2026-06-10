package com.garethpaul.scanr;

import java.io.Closeable;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

import android.app.ActionBar;
import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;

public class MainActivity extends Activity implements OnClickListener {
	private TessOCR mTessOCR;
	private ProgressDialog mProgressDialog;
	private ImageButton imageButton;
	private String mCurrentPhotoPath;
	private boolean mHandledSendIntent;
	private static final int REQUEST_TAKE_PHOTO = 1;
	private static final int REQUEST_PICK_PHOTO = 2;
    public static final String DATA_PATH = Environment
            .getExternalStorageDirectory().toString() + "/tesseract/";
    private static String TAG = "OCR";
    public static final String lang = "eng";

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
        ActionBar ab = getActionBar();
        if (ab != null) {
            ab.setDisplayShowTitleEnabled(false);
            ab.setDisplayHomeAsUpEnabled(false);
            ab.setHomeAsUpIndicator(R.drawable.none);
        }

        String[] paths = new String[] { DATA_PATH, DATA_PATH + "tessdata/" };

        for (String path : paths) {
            File dir = new File(path);
            if (!dir.exists()) {
                if (!dir.mkdirs()) {
                    Log.v(TAG, "ERROR: Creation of directory " + path + " on sdcard failed");
                    return;
                } else {
                    Log.v(TAG, "Created directory " + path + " on sdcard");
                }
            }

        }

        // You can get them at:
        // http://code.google.com/p/tesseract-ocr/downloads/list
        // This area needs work and optimization
        if (!(new File(DATA_PATH + "tessdata/" + lang + ".traineddata")).exists()) {
            InputStream in = null;
            OutputStream out = null;
            try {

                AssetManager assetManager = getAssets();
                in = assetManager.open("tessdata/" + lang + ".traineddata");
                //GZIPInputStream gin = new GZIPInputStream(in);
                out = new FileOutputStream(DATA_PATH
                        + "tessdata/" + lang + ".traineddata");

                // Transfer bytes from in to out
                byte[] buf = new byte[1024];
                int len;
                //while ((lenf = gin.read(buff)) > 0) {
                while ((len = in.read(buf)) > 0) {
                    out.write(buf, 0, len);
                }
                //gin.close();

                Log.v(TAG, "Copied " + lang + " traineddata");
            } catch (IOException e) {
                Log.e(TAG, "Was unable to copy " + lang + " traineddata");
            } finally {
                closeQuietly(out, "Unable to close OCR traineddata output");
                closeQuietly(in, "Unable to close OCR traineddata asset");
            }
        }

		setContentView(R.layout.activity_main);
		imageButton = (ImageButton) findViewById(R.id.imageButton);
		imageButton.setOnClickListener(this);
		mTessOCR = new TessOCR();
	}



	@Override
	protected void onResume() {
		// TODO Auto-generated method stub
		super.onResume();

		Intent intent = getIntent();
		if (!mHandledSendIntent && Intent.ACTION_SEND.equals(intent.getAction())) {
			mHandledSendIntent = true;
			Uri imageUri = (Uri) intent.getParcelableExtra(Intent.EXTRA_STREAM);
			String type = intent.getType();
			if (imageUri != null && type != null && type.startsWith("image/")) {
				Intent resultIntent = new Intent(this, ResultActivity.class);
				resultIntent.setType(type);
				resultIntent.putExtra(Intent.EXTRA_STREAM, imageUri);
				startActivity(resultIntent);
			} else {
				Log.e(TAG, "ACTION_SEND missing image stream");
			}
		}
	}

	@Override
	protected void onPause() {
		// TODO Auto-generated method stub
		super.onPause();
	}

	@Override
	protected void onDestroy() {
		// TODO Auto-generated method stub
		super.onDestroy();

		if (mTessOCR != null) {
			mTessOCR.onDestroy();
		}
	}

    private void closeQuietly(Closeable closeable, String message) {
        if (closeable != null) {
            try {
                closeable.close();
            } catch (IOException e) {
                Log.e(TAG, message);
            }
        }
    }

	private void dispatchTakePictureIntent() {
		Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
		// Ensure that there's a camera activity to handle the intent
		if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
			// Create the File where the photo should go
			File photoFile = null;
			try {
				photoFile = createImageFile();
			} catch (IOException ex) {
				Log.e(TAG, "Unable to create camera image");
			}
			// Continue only if the File was successfully created
			if (photoFile != null) {
				takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT,
						Uri.fromFile(photoFile));
				startActivityForResult(takePictureIntent, REQUEST_TAKE_PHOTO);
			}
		}
	}

	/**
	 * http://developer.android.com/training/camera/photobasics.html
	 */
	private File createImageFile() throws IOException {
		// Create an image file name
		String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(new Date());
		String imageFileName = "JPEG_" + timeStamp;
		String storageDir = Environment.getExternalStorageDirectory()
                + "/TessOCR";
		File dir = new File(storageDir);
		if (!dir.exists() && !dir.mkdirs()) {
			throw new IOException("Unable to create image directory");
		}

		File image = File.createTempFile(imageFileName + "_", ".jpg", dir);

		// Save a file: path for use with ACTION_VIEW intents
		mCurrentPhotoPath = image.getAbsolutePath();
		return image;
	}

	@Override
	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
		// TODO Auto-generated method stub
		if (requestCode == REQUEST_TAKE_PHOTO
				&& resultCode == Activity.RESULT_OK) {
            Intent i = new Intent(getApplicationContext(), ResultActivity.class);
            i.putExtra("IMAGE_URI",mCurrentPhotoPath);
            startActivity(i);
            //setPic();
		}
    }

	@Override
	public void onClick(View v) {
		// TODO Auto-generated method stub
		takePhoto();
	}

	private void takePhoto() {
		dispatchTakePictureIntent();
	}


}
