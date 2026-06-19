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
	private ImageButton imageButton;
	private String mCurrentPhotoPath;
	private boolean mHandledSendIntent;
	private static final String STATE_HANDLED_SEND_INTENT = "handledSendIntent";
	private static final String STATE_CURRENT_PHOTO_PATH = "currentPhotoPath";
	private static final int REQUEST_TAKE_PHOTO = 1;
	private static final int REQUEST_PICK_PHOTO = 2;
    public static final String DATA_PATH = Environment
            .getExternalStorageDirectory().toString() + "/tesseract/";
    private static String TAG = "OCR";
    public static final String lang = "eng";

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		if (savedInstanceState != null) {
			mHandledSendIntent = savedInstanceState.getBoolean(
					STATE_HANDLED_SEND_INTENT, false);
			mCurrentPhotoPath = savedInstanceState.getString(
					STATE_CURRENT_PHOTO_PATH);
		}
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
		File trainedDataFile = new File(DATA_PATH + "tessdata/" + lang + ".traineddata");
		if (!trainedDataFile.exists()) {
			File trainedDataTemp = new File(trainedDataFile.getAbsolutePath() + ".tmp");
			InputStream in = null;
			OutputStream out = null;
			boolean installed = false;
			try {
				CaptureFile.delete(trainedDataTemp.getAbsolutePath());
				AssetManager assetManager = getAssets();
				in = assetManager.open("tessdata/" + lang + ".traineddata");
				out = new FileOutputStream(trainedDataTemp);

				byte[] buf = new byte[1024];
				int len;
				while ((len = in.read(buf)) > 0) {
					out.write(buf, 0, len);
				}
				out.close();
				out = null;
				in.close();
				in = null;
				if (!trainedDataTemp.renameTo(trainedDataFile)) {
					throw new IOException("Unable to install OCR traineddata");
				}
				installed = true;
				Log.v(TAG, "Copied " + lang + " traineddata");
			} catch (IOException e) {
				Log.e(TAG, "Was unable to copy " + lang + " traineddata");
			} finally {
				closeQuietly(out, "Unable to close OCR traineddata output");
				closeQuietly(in, "Unable to close OCR traineddata asset");
				if (!installed) {
					CaptureFile.delete(trainedDataTemp.getAbsolutePath());
				}
			}
		}

		setContentView(R.layout.activity_main);
		imageButton = (ImageButton) findViewById(R.id.imageButton);
		imageButton.setOnClickListener(this);
	}

	@Override
	protected void onSaveInstanceState(Bundle outState) {
		outState.putBoolean(STATE_HANDLED_SEND_INTENT, mHandledSendIntent);
		outState.putString(STATE_CURRENT_PHOTO_PATH, mCurrentPhotoPath);
		super.onSaveInstanceState(outState);
	}



	@Override
	protected void onResume() {
		super.onResume();
		handleSendIntent(getIntent());
	}

	@Override
	protected void onNewIntent(Intent intent) {
		super.onNewIntent(intent);
		setIntent(intent);
		mHandledSendIntent = false;
		handleSendIntent(intent);
	}

	private void handleSendIntent(Intent intent) {
		if (!mHandledSendIntent && Intent.ACTION_SEND.equals(intent.getAction())) {
			mHandledSendIntent = true;
			Uri imageUri = (Uri) intent.getParcelableExtra(Intent.EXTRA_STREAM);
			String type = intent.getType();
			if (imageUri != null && type != null && type.startsWith("image/")) {
				Intent resultIntent = new Intent(this, ResultActivity.class);
				resultIntent.setType(type);
				resultIntent.putExtra(Intent.EXTRA_STREAM, imageUri);
				resultIntent.addFlags(intent.getFlags()
						& Intent.FLAG_GRANT_READ_URI_PERMISSION);
				try {
					startActivity(resultIntent);
				} catch (RuntimeException error) {
					Log.e(TAG, "Unable to open shared image");
				}
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
					try {
						startActivityForResult(takePictureIntent, REQUEST_TAKE_PHOTO);
					} catch (RuntimeException error) {
						String photoPath = mCurrentPhotoPath;
						mCurrentPhotoPath = null;
						deleteCapture(photoPath);
						Log.e(TAG, "Unable to launch camera");
					}
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
		if (requestCode == REQUEST_TAKE_PHOTO) {
			String photoPath = mCurrentPhotoPath;
			mCurrentPhotoPath = null;
			if (resultCode == Activity.RESULT_OK) {
				if (photoPath != null) {
					Intent i = new Intent(getApplicationContext(), ResultActivity.class);
					i.putExtra("IMAGE_URI", photoPath);
					try {
						startActivity(i);
					} catch (RuntimeException error) {
						deleteCapture(photoPath);
						Log.e(TAG, "Unable to open captured image");
					}
				} else {
					Log.e(TAG, "Camera result missing image path");
				}
			} else {
				deleteCapture(photoPath);
			}
			return;
		}
		super.onActivityResult(requestCode, resultCode, data);
	}

	private void deleteCapture(String photoPath) {
		if (photoPath != null && !CaptureFile.delete(photoPath)) {
			Log.e(TAG, "Unable to delete camera image");
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
