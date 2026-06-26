package com.garethpaul.scanr;

import android.app.ActionBar;
import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;

public class ResultActivity extends Activity implements View.OnClickListener {

    private ProgressDialog mProgressDialog;
    private ImageView mImage;
    private TessOCR mTessOCR;
    private final OCRTaskRunner mOCRTasks = new OCRTaskRunner();
    private TextView mResult;
    private volatile boolean mDestroyed;
    private volatile int mOCRGeneration;
    private static final int REQUEST_TAKE_PHOTO = 1;
    private static final int REQUEST_PICK_PHOTO = 2;
    private static final int TARGET_IMAGE_WIDTH = 500;
    private static final int TARGET_IMAGE_HEIGHT = 500;
    private static final String TAG = "OCR";
    private String mCurrentPhotoPath;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        ActionBar ab = getActionBar();
        if (ab != null) {
            ab.setDisplayShowTitleEnabled(false);
            ab.setDisplayHomeAsUpEnabled(true);
        }
        setContentView(R.layout.activity_result);
        mTessOCR = new TessOCR();
        mResult = (TextView) findViewById(R.id.tv_result);
        mImage = (ImageView) findViewById(R.id.image);

        Bundle extras = getIntent().getExtras();
        if (extras != null) {
            String value = extras.getString("IMAGE_URI");
            if (value != null) {
                mCurrentPhotoPath = value;
                setPic();
                return;
            }

            Uri imageUri = (Uri) extras.getParcelable(Intent.EXTRA_STREAM);
            if (imageUri != null) {
                uriOCR(imageUri);
            }
        }
    }

    private void uriOCR(Uri uri) {
        if (uri != null) {
            try {
                Bitmap bitmap = decodeSharedBitmap(uri);
                if (bitmap == null) {
                    mResult.setText("Unable to decode image.");
                    return;
                }
                mImage.setImageBitmap(bitmap);
                doOCR(bitmap);
            } catch (FileNotFoundException e) {
                Log.e(TAG, "Unable to open image URI");
                mResult.setText("Unable to open image.");
            } catch (SecurityException e) {
                Log.e(TAG, "Image URI access denied");
                mResult.setText("Unable to open image.");
            }
        }
    }

    private Bitmap decodeSharedBitmap(Uri uri) throws FileNotFoundException {
        BitmapFactory.Options bounds = new BitmapFactory.Options();
        bounds.inJustDecodeBounds = true;
        InputStream boundsStream = getContentResolver().openInputStream(uri);
        if (boundsStream == null) {
            throw new FileNotFoundException();
        }
        try {
            BitmapFactory.decodeStream(boundsStream, null, bounds);
        } finally {
            closeImageStream(boundsStream);
        }

        int sampleSize = ImageSampleSize.forBounds(bounds.outWidth,
                bounds.outHeight, TARGET_IMAGE_WIDTH, TARGET_IMAGE_HEIGHT);
        if (sampleSize == 0) {
            return null;
        }

        BitmapFactory.Options options = new BitmapFactory.Options();
        options.inSampleSize = sampleSize;
        options.inPurgeable = true;
        InputStream imageStream = getContentResolver().openInputStream(uri);
        if (imageStream == null) {
            throw new FileNotFoundException();
        }
        try {
            return BitmapFactory.decodeStream(imageStream, null, options);
        } finally {
            closeImageStream(imageStream);
        }
    }

    private void closeImageStream(InputStream stream) {
        try {
            stream.close();
        } catch (IOException e) {
            Log.e(TAG, "Unable to close image URI stream");
        }
    }

    private void doOCR(final Bitmap bitmap) {
        if (bitmap == null) {
            mResult.setText("Unable to decode image.");
            return;
        }

        final TessOCR tessOCR = mTessOCR;
        if (mDestroyed || tessOCR == null) {
            return;
        }
        final int ocrGeneration = ++mOCRGeneration;

        if (mProgressDialog == null) {
            mProgressDialog = ProgressDialog.show(this, "Processing",
                    "Doing OCR...", true);
        }
        else {
            mProgressDialog.show();
        }

        mOCRTasks.execute(new Runnable() {
            public void run() {
                if (mDestroyed || ocrGeneration != mOCRGeneration) {
                    return;
                }
                final String result = tessOCR.getOCRResult(bitmap);
                if (mDestroyed) {
                    return;
                }
                if (ocrGeneration != mOCRGeneration) {
                    return;
                }

                runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        // TODO Auto-generated method stub
                        if (mDestroyed) {
                            return;
                        }
                        if (ocrGeneration != mOCRGeneration) {
                            return;
                        }
                        if (result != null && !result.equals("")) {
                            mResult.setText(result);
                        }

                        if (mProgressDialog != null) {
                            mProgressDialog.dismiss();
                            mProgressDialog = null;
                        }
                    }

                });

            };
        });
    }


    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        // TODO Auto-generated method stub
        super.onWindowFocusChanged(hasFocus);
        mResult = (TextView) findViewById(R.id.tv_result);
        mImage = (ImageView) findViewById(R.id.image);
    }

    private void setPic() {
        String photoPath = mCurrentPhotoPath;
        mCurrentPhotoPath = null;
        try {
        // Get the dimensions of the bitmap
        BitmapFactory.Options bmOptions = new BitmapFactory.Options();
        bmOptions.inJustDecodeBounds = true;
        BitmapFactory.decodeFile(photoPath, bmOptions);
        int photoW = bmOptions.outWidth;
        int photoH = bmOptions.outHeight;
        // Determine how much to scale down the image
        int sampleSize = ImageSampleSize.forBounds(photoW, photoH,
                TARGET_IMAGE_WIDTH, TARGET_IMAGE_HEIGHT);
        if (sampleSize == 0) {
            mResult.setText("Unable to decode image.");
            return;
        }

        // Decode the image file into a Bitmap sized to fill the View
        bmOptions.inJustDecodeBounds = false;
        bmOptions.inSampleSize = sampleSize;
        bmOptions.inPurgeable = true;

        Bitmap bitmap = BitmapFactory.decodeFile(photoPath, bmOptions);
        if (bitmap == null) {
            mResult.setText("Unable to decode image.");
            return;
        }
        mImage.setImageBitmap(bitmap);
        doOCR(bitmap);
        } finally {
            if (!CaptureFile.delete(photoPath)) {
                Log.e(TAG, "Unable to delete camera image");
            }
        }
    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        // TODO Auto-generated method stub
        if (requestCode == REQUEST_TAKE_PHOTO
                && resultCode == Activity.RESULT_OK) {
            setPic();
        }
    }

    @Override
    protected void onResume() {
        // TODO Auto-generated method stub
        super.onResume();
    }

    @Override
    protected void onPause() {
        // TODO Auto-generated method stub
        super.onPause();
    }



    @Override
	protected void onDestroy() {
			// TODO Auto-generated method stub
			mDestroyed = true;
        mOCRGeneration++;
        if (mProgressDialog != null) {
            mProgressDialog.dismiss();
            mProgressDialog = null;
        }
        final TessOCR tessOCR = mTessOCR;
        mTessOCR = null;
        if (tessOCR != null) {
			mOCRTasks.close(new Runnable() {
				public void run() {
					tessOCR.onDestroy();
				}
			});
		} else {
			mOCRTasks.close(new Runnable() {
				public void run() {
				}
			});
		}
		super.onDestroy();
	}

    @Override
    public void onClick(View v) {

    }
}
