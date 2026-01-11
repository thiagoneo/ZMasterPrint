#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
APP_NAME="ZMasterPrint"
PKG_NAME="zmasterprint"
APP_VERSION="$(
  PYTHONPATH="$PROJECT_ROOT" \
  python3 -c "import zmasterprint.__version__ as v; print(v.VERSION)"
)"
ARCHITECTURE=$(dpkg --print-architecture)
PKG_DIR="${SCRIPT_DIR}/${PKG_NAME}.deb-build"
PKG_FILE="${PKG_NAME}_${APP_VERSION}_${ARCHITECTURE}.deb"
REQUIRED_PACKAGES="python3 python3-dev python3-venv python3-pip build-essential"
MISSING_PACKAGES=""

# Check system dependencies
for pkg in $REQUIRED_PACKAGES; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        MISSING_PACKAGES="$MISSING_PACKAGES $pkg"
    fi
done

if [ -n "$MISSING_PACKAGES" ]; then
    echo "Installing missing packages: $MISSING_PACKAGES"
    sudo apt-get update
    sudo apt-get install -y "$MISSING_PACKAGES"
fi

# Prepare Python environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r "${PROJECT_ROOT}/requirements.txt"
pip install pyinstaller

python3 "${PROJECT_ROOT}/scripts/generate_ui.py"

# Build the application using PyInstaller
rm -rfv "${SCRIPT_DIR}/dist ${SCRIPT_DIR}/build"

pyinstaller \
  --name "${PKG_NAME}" \
  --onedir \
  --noconfirm \
  --clean \
  --strip \
  --distpath "${SCRIPT_DIR}/dist" \
  --workpath "${SCRIPT_DIR}/build" \
  --add-data "${PROJECT_ROOT}/zmasterprint/generated/about_reqs.html:generated" \
  "${PROJECT_ROOT}/zmasterprint/main.py"

deactivate

# Prepare the package directory structure
rm -rfv "${PKG_DIR}"
mkdir -pv "${PKG_DIR}/DEBIAN"

mkdir -pv "${PKG_DIR}/opt/${PKG_NAME}"
cp -rv "${SCRIPT_DIR}/dist/${PKG_NAME}"/* "${PKG_DIR}/opt/${PKG_NAME}/"
mkdir -pv "${PKG_DIR}/opt/${PKG_NAME}/icons"
cp -v "${PROJECT_ROOT}/zmasterprint/icons/zmasterprint.svg" "${PKG_DIR}/opt/${PKG_NAME}/icons/"
chmod 755 "${PKG_DIR}/opt/${PKG_NAME}/${PKG_NAME}"

mkdir -pv "${PKG_DIR}/usr/bin"
ln -sfv "/opt/${PKG_NAME}/${PKG_NAME}" "${PKG_DIR}/usr/bin/${PKG_NAME}"
mkdir -pv "${PKG_DIR}/usr/share/icons/hicolor/scalable/apps/"
ln -sfv "/opt/${PKG_NAME}/icons/zmasterprint.svg" "${PKG_DIR}/usr/share/icons/hicolor/scalable/apps/zmasterprint.svg"

mkdir -pv "${PKG_DIR}/usr/share/applications"
cat <<EOF > "${PKG_DIR}/usr/share/applications/${PKG_NAME}.desktop"
[Desktop Entry]
Name=ZMasterPrint
Name[pt_BR]=Editor de etiquetas
Comment=Edite e etiquetas com facilidade
Exec=/usr/bin/zmasterprint
Icon=/opt/${PKG_NAME}/icons/zmasterprint.svg
Terminal=false
Type=Application
Categories=Utility;
StartupWMClass=zmasterprint
EOF

mkdir -pv "${PKG_DIR}/usr/share/doc/${PKG_NAME}"
cp -v "${PROJECT_ROOT}/LICENSE" "${PKG_DIR}/usr/share/doc/${PKG_NAME}/LICENSE"

cat <<EOF > "${PKG_DIR}/DEBIAN/control"
Package: ${PKG_NAME}
Version: ${APP_VERSION}
Section: utils
Priority: optional
Architecture: ${ARCHITECTURE}
Installed-Size: $(du -sk ${PKG_DIR}/opt ${PKG_DIR}/usr | awk '{sum += $1} END {print sum}')
Depends: libc6 (>= $(getconf GNU_LIBC_VERSION | awk '{print $2}')), cups-client
Maintainer: ZMasterPrint Developers <sousathiago@protonmail.com>
Description: Uma ferramenta simples e pr�tica para gerar e imprimir etiquetas em impressoras Zebra usando c�digo ZPL.
EOF

# Build the Debian package
rm -fv "${SCRIPT_DIR}/${PKG_FILE}"
dpkg-deb --build --root-owner-group "${PKG_DIR}" "${SCRIPT_DIR}/${PKG_FILE}"
echo "Debian package created at ${SCRIPT_DIR}/${PKG_FILE}"
