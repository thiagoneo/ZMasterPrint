import subprocess
from pathlib import Path

# Caminhos base
SRC = Path(__file__).resolve().parent.parent / "zmasterprint"
GENERATED = SRC / "generated"

# Certifica que a pasta generated existe
GENERATED.mkdir(exist_ok=True)

# Mapeamento .ui → .py
UI_FILES = {
    SRC / "ui/mainwindow.ui": GENERATED / "ui_mainwindow.py",
    SRC / "ui/settingsdialog.ui": GENERATED / "ui_settingsdialog.py",
    SRC / "ui/cadprodutodlg.ui": GENERATED / "ui_cadprodutodlg.py",
    SRC / "ui/aboutdlg.ui": GENERATED / "ui_aboutdlg.py",
}

# Mapeamento .qrc → _rc.py
QRC_FILES = {
    SRC / "resources/resources.qrc": GENERATED / "resources_rc.py",
    SRC / "resources/about.qrc": GENERATED / "about_rc.py",
}

# Função simples para rodar comandos
def run(cmd):
    print("▶", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)

# Geração
for ui_in, py_out in UI_FILES.items():
    run(["pyuic5", "--from-imports", str(ui_in), "-o", str(py_out)])

for qrc_in, py_out in QRC_FILES.items():
    run(["pyrcc5", str(qrc_in), "-o", str(py_out)])

print("Todos os arquivos gerados com sucesso.")