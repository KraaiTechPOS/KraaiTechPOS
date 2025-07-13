[app]
title = PyPOS
package.name = pypos
package.domain = org.example
source.dir = .
source.include_exts = py,json
version = 1.0
entrypoint = main.py
orientation = portrait
fullscreen = 1
android.hide_statusbar = 1
android.permissions = INTERNET
requirements = python3,kivy
android.package_format = apk
android.minapi = 21
android.api = 31
android.ndk = 23b
android.ndk_api = 21
android.ndk_use_legacy_toolchain = False
log_level = 2
android.copy_libs = 1

[buildozer]
requirement_install_overrides = --break-system-packages
log_level = 2
warn_on_root = 1