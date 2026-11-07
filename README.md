# HTV — Android APK build

This repository contains a GitHub Actions workflow for building the HTV Android app as a universal APK.

## Build

1. Open the **Actions** tab.
2. Select **Build universal Android APK**.
3. Press **Run workflow**.
4. When the run finishes, open it and download the `HTV-universal-APK` artifact.

The workflow checks out the public source repository `HTWMedia/HTV`, installs Flutter dependencies, and runs `flutter build apk --release`.

**Note:** The application source itself has not been mirrored into this repository yet; the workflow builds directly from the upstream repository.
