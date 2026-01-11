import subprocess
from pathlib import Path
import re
import html
from importlib.metadata import version as pkg_version, PackageNotFoundError

# Caminhos base
SRC = Path(__file__).resolve().parent.parent / "zmasterprint"
GENERATED = SRC / "generated"
REQUIREMENTS = Path(__file__).resolve().parent.parent / "requirements.txt"
REQUIREMENTS_HTML = GENERATED / "about_reqs.html"

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

RE_REQUIREMENT = re.compile(
    r"""
    ^
    \s*
    (?P<name>[a-zA-Z0-9_.-]+)
    \s*
    (?:
        (?P<op>==|>=|<=|~=|!=|>|<)
        \s*
        (?P<version>[^\s;]+)
    )?
    """,
    re.VERBOSE,
)

def generate_html(
    font_family: str = "Segoe UI",
    font_size_pt: int = 10,
):
    template = f"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN"
"http://www.w3.org/TR/REC-html40/strict.dtd">
<html>
<head>
<meta name="qrichtext" content="1" />
<style type="text/css">
p, li {{ white-space: pre-wrap; }}
</style>
</head>
<body style=" font-family:'{font_family}'; font-size:{font_size_pt}pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;
-qt-block-indent:0; text-indent:0px;">
<span style=" font-weight:600; background-color:transparent;">
Bibliotecas utilizadas:
</span>
</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;
-qt-block-indent:0; text-indent:0px;">
python_libs_html
</p>
</body>
</html>
"""
    return template

def get_installed_version(pkg_name: str) -> str:
    try:
        return pkg_version(pkg_name)
    except PackageNotFoundError:
        return None

def generate_libraries_html(requirements):
    lines = []

    for name, _ in requirements:
        installed_version = get_installed_version(name)

        if installed_version is None:
            continue

        safe_name = html.escape(name)
        safe_version = html.escape(installed_version)

        pypi_url = f"https://pypi.org/project/{safe_name}/"

        lines.append(
            f'<p style="margin:0;">'
            f'<b>'
            f'<a href="{pypi_url}" style="color:#0850bd; text-decoration:underline;">'
            f'{safe_name}'
            f'</a>'
            f'</b> {safe_version}'
            f'</p>'
        )

    return "\n".join(lines)

def write_html_file(output_file: str, template: str):
    output_file = Path(output_file)
    output_file.write_text(template, encoding="utf-8")

template = generate_html()
parsed_requirements = []

for line in REQUIREMENTS.read_text().splitlines():
    line = line.strip()

    if not line or line.startswith("#"):
        continue

    match = RE_REQUIREMENT.match(line)
    if not match:
        continue

    name = match.group("name")
    version = match.group("version") or ""

    parsed_requirements.append((name, version))

libs_html = generate_libraries_html(parsed_requirements)
template = template.replace("python_libs_html", libs_html)
write_html_file(REQUIREMENTS_HTML, template)

print("Todos os arquivos gerados com sucesso.")