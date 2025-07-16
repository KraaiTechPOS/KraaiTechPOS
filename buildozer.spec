[app]
title = POS System
package.name = posapp
package.domain = org.kivy.pos
source.dir = .
source.include_exts = py,json
source.exclude_exts = spec
source.include_patterns = *.json,*.py
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 1
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
osx.kivy_version = 2.3.0

# Entry point of your app
source.main = main.py

# Icon (optional)
# icon.filename = %(source.dir)s/icon.png

# Presplash (optional)
# presplash.filename = %(source.dir)s/splash.png

# Android specific
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.arch = armeabi-v7a
android.enable_androidx = 1

# Build with modern features
android.gradle_dependencies = com.android.support:appcompat-v7:28.0.0
android.allow_backup = 1
android.logcat_filters = *:S python:D

# Avoid AndroidX conversion issues
android.use_androidx = 1
android.enable_androidx = 1

# Set this to 0 to avoid installing on build
# deploy = 0

# Uncomment to force build on every run
# force_build = 1

[buildozer]
log_level = 2
warn_on_root = 1
