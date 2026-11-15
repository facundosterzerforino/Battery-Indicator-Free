# BatteryBot 10.0.1-beta1 built from source for Android 2.3 (Motorola XT550)

Branch `xt550-gingerbread` starts at upstream commit `0d8fa8d`
("Release 10.0.1-beta1", 2016-08-17), the last BatteryBot release whose
minSdkVersion supports Android 2.3. App code is unchanged; this branch only
adds an offline build script, because the original Gradle 2.1 / Jack setup no
longer builds.

## Code review (before building)

- 17 Java files, 3,454 lines, reviewed for network use, command execution,
  root, trackers, ads, dynamic code loading and device identifiers: none found.
- Only permission: `RECEIVE_BOOT_COMPLETED` (start the status-bar icon at boot).
  No INTERNET permission, so it cannot send data anywhere.
- It lists installed packages only to find its own icon-set plugins, on the device.
- The "upgrade" button opens a Play Store link; on a phone without Play Store it
  shows "can't launch Market".

## Build inputs

- support-v4 24.1.1 AAR from Google's Maven (Apache 2.0), SHA-1
  `57c006a017aa2cbe3d32511e5ac28ee76cf9f51b` (checked by `build.py`).
- `android.jar` from Google's `platform-24_r02.zip` (SHA-1
  `8912da3d4bfe7a9f28f0e5ce92d3a8dc96342aee`), compile time only.
- JDK 17, Android build-tools 30.0.3 (aapt, R8/D8, zipalign, apksigner).

```
python build.py --jdk JDK --build-tools BUILD_TOOLS --android-jar android-24/android.jar   --support-aar support-v4-24.1.1.aar --keystore /outside/key.jks --storepass-file /outside/pass
```

## Measured on the XT550 (Android 2.3.6)

Background service (status-bar percentage): about 3.0 MB PSS (median of 3).
Main screen, only while open: about 6.5 MB.

License: GPL-3.0 (see LICENSE).
