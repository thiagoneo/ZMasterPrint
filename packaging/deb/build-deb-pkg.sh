#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT=$(dirname $(dirname $SCRIPT_DIR))
APP_NAME="ZMasterPrint"
PKG_NAME="zmasterprint"
APP_VERSION=$(PYTHONPATH=${PROJECT_ROOT} python3 -c "import zmasterprint.__version__ as v; print(v.VERSION)")
ARCHITECTURE=$(dpkg --print-architecture)
PKG_DIR="${SCRIPT_DIR}/${PKG_NAME}_${APP_VERSION}_${ARCHITECTURE}"

# Check system dependencies
if ! command -v python3 &> /dev/null || \
   ! command -v python3 -m venv &> /dev/null || \
   ! command -v pip &> /dev/null || \
   ! command -v dpkg-deb &> /dev/null;
then
    echo "Installing required packages...";
    sudo apt-get update;
    sudo apt-get install -y python3 python3-venv python3-pip build-essential;
fi

# Prepare Python environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r ${PROJECT_ROOT}/requirements.txt
pip install pyinstaller

# Build the application using PyInstaller
pyinstaller --name ${PKG_NAME} --onedir --noconfirm --clean --strip \
    --distpath ${SCRIPT_DIR}/dist --workpath ${SCRIPT_DIR}/build \
    ${PROJECT_ROOT}/zmasterprint/main.py

deactivate

# Prepare the package directory structure
rm -rf ${PKG_DIR}
mkdir -p ${PKG_DIR}/DEBIAN
cat <<EOF > ${PKG_DIR}/DEBIAN/control
Package: ${PKG_NAME}
Version: ${APP_VERSION}
Section: utils
Priority: optional
Architecture: ${ARCHITECTURE}
Depends: libc6 (>= $(getconf GNU_LIBC_VERSION | awk '{print $2}')), cups-client
Maintainer: ZMasterPrint Developers <sousathiago@protonmail.com>
Description: Uma ferramenta simples e prática para gerar e imprimir etiquetas em impressoras Zebra usando código ZPL.
EOF

mkdir -p ${PKG_DIR}/opt/${PKG_NAME}
cp -r ${SCRIPT_DIR}/dist/${PKG_NAME}/* ${PKG_DIR}/opt/${PKG_NAME}/
chmod 755 ${PKG_DIR}/opt/${PKG_NAME}/${PKG_NAME}

mkdir -p ${PKG_DIR}/usr/bin
ln -sf /opt/${PKG_NAME}/${PKG_NAME} ${PKG_DIR}/usr/bin/${PKG_NAME}

mkdir -p ${PKG_DIR}/usr/share/applications
cat <<EOF > ${PKG_DIR}/usr/share/applications/${PKG_NAME}.desktop
[Desktop Entry]
Name=ZMasterPrint
Name[pt_BR]=Editor de etiquetas
Comment=Edite e etiquetas com facilidade
Exec=/usr/bin/zmasterprint
Icon=/opt/ZMasterPrint/icons/zmasterprint.svg
Terminal=false
Type=Application
Categories=Utility;
StartupWMClass=zmasterprint
EOF

# Build the Debian package
dpkg-deb --build --root-owner-group ${PKG_DIR}
echo "Debian package created at ${PKG_DIR}.deb"
