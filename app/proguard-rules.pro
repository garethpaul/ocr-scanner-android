# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to the flags specified in the
# Android SDK's proguard-android.txt, which build.gradle pulls in via
# getDefaultProguardFile(). You can edit the include path and order by changing
# the proguardFiles directive in build.gradle.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# Add any project specific keep options here:

# Tesseract/leptonica are loaded through JNI, so their native entry points are
# not visible to ProGuard's static analysis. minifyEnabled is currently false;
# if it is enabled, keep the JNI-facing classes.
#-keep class com.googlecode.tesseract.android.** { *; }
#-keep class com.googlecode.leptonica.android.** { *; }
