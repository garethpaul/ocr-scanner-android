package com.garethpaul.scanr;

import android.graphics.Bitmap;
import android.os.Environment;

import com.googlecode.tesseract.android.TessBaseAPI;

public class TessOCR {
	private TessBaseAPI mTess;
    public static final String DATA_PATH = Environment
            .getExternalStorageDirectory().toString() + "/tesseract/";

    public TessOCR() {
		// TODO Auto-generated constructor stub
		mTess = new TessBaseAPI();
        mTess.setDebug(true);
        System.out.println(DATA_PATH.toString());
        mTess.init(DATA_PATH, "eng");

	}
	
	public String getOCRResult(Bitmap bitmap) {
		mTess.setImage(bitmap);
		String result = mTess.getUTF8Text();
		return result;
    }
	
	public void onDestroy() {
		if (mTess != null)
			mTess.end();
	}
	
}
