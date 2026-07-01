[app]
title = Modelo S
package.name = modelos
package.domain = org.modelos

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = modelo_s.py,main.py,fetch_data.py

version = 1.0.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True

log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
