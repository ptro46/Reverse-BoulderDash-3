#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
cargo build --release --locked
app="$PWD/build/Boulder Dash III.app"
mkdir -p "$app/Contents/MacOS" "$app/Contents/Resources"
cp target/release/boulder-dash-iii "$app/Contents/MacOS/boulder-dash-iii.new"
mv -f "$app/Contents/MacOS/boulder-dash-iii.new" "$app/Contents/MacOS/boulder-dash-iii"
cat > "$app/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>boulder-dash-iii</string>
<key>CFBundleIdentifier</key><string>fr.ptro.boulderdash3.rust</string>
<key>CFBundleName</key><string>Boulder Dash III</string>
<key>CFBundleDisplayName</key><string>Boulder Dash III</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>0.1.0</string>
<key>CFBundleVersion</key><string>1</string>
<key>LSMinimumSystemVersion</key><string>11.0</string>
<key>NSHighResolutionCapable</key><true/>
<key>NSSupportsAutomaticGraphicsSwitching</key><true/>
<key>CFBundleIconFile</key><string>BoulderDashIII.icns</string>
</dict></plist>
PLIST
if [ -f assets/BoulderDashIII.icns ]; then cp assets/BoulderDashIII.icns "$app/Contents/Resources/"; fi
codesign --force --deep --sign - "$app"
codesign --verify --deep --strict "$app"
printf '%s\n' "$app"
