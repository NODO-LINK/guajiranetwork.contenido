#!/usr/bin/env bash
# Compila el APK sin Gradle, con las herramientas del Android SDK del runner de GitHub.
set -euo pipefail
cd "$(dirname "$0")"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
BT=$(ls -d "$SDK"/build-tools/* | sort -V | tail -1)
PLAT=$(ls -d "$SDK"/platforms/android-* | sort -V | tail -1)
JAR="$PLAT/android.jar"
VC="${VERSION_CODE:-1}"
echo "build-tools: $BT"; echo "plataforma: $PLAT"; java -version 2>&1 | head -1

rm -rf build && mkdir -p build/gen build/obj build/dex
"$BT/aapt2" compile --dir res -o build/res.zip
"$BT/aapt2" link -o build/base.apk -I "$JAR" --manifest AndroidManifest.xml build/res.zip \
  --java build/gen --min-sdk-version 24 --target-sdk-version 34 \
  --version-code "$VC" --version-name "1.$VC" --auto-add-overlay
javac -source 8 -target 8 -bootclasspath "$JAR" -classpath "$JAR" -encoding UTF-8 -nowarn -d build/obj $(find src build/gen -name '*.java')
"$BT/d8" --release --lib "$JAR" --min-api 24 --output build/dex $(find build/obj -name '*.class')
cp build/base.apk build/sin-firmar.apk
(cd build/dex && zip -q ../sin-firmar.apk classes.dex)
"$BT/zipalign" -f -p 4 build/sin-firmar.apk build/alineado.apk

PASS="${KEYSTORE_PASS:-guajira2107}"
if [ -n "${KEYSTORE_B64:-}" ]; then
  echo "$KEYSTORE_B64" | base64 -d > build/gn.jks
else
  keytool -genkeypair -keystore build/gn.jks -storepass "$PASS" -keypass "$PASS" -alias gn \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -dname "CN=Guajira Network, O=GUAJIRA NETWORK 2107 C.A., L=San Rafael de El Mojan, C=VE"
fi
"$BT/apksigner" sign --ks build/gn.jks --ks-pass "pass:$PASS" --ks-key-alias gn --out build/GuajiraNetwork.apk build/alineado.apk
"$BT/apksigner" verify --print-certs build/GuajiraNetwork.apk | head -3
ls -la build/GuajiraNetwork.apk
