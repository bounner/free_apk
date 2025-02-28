[app]
title = OrangeApp
package.name = orangeapp
package.domain = org.orange
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3, kivy, sqlite3
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE;maxSdkVersion=28
android.api = 31
android.minapi = 21
android.sdk = 20
android.ndk = 23b
android.archs = arm64-v8a, armeabi-v7a
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1