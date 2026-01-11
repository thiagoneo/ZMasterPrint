@echo off
setlocal enabledelayedexpansion

REM === Caminhos base ===
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%\..\..
for %%I in ("%PROJECT_ROOT%") do set PROJECT_ROOT=%%~fI

set APP_NAME=ZMasterPrint
set PKG_NAME=zmasterprint

REM === Lê versão do app ===
for /f %%v in ('PYTHONPATH="%PROJECT_ROOT%" python -c "import zmasterprint.__version__ as v; print(v.VERSION)"') do (
REM for /f %%v in ('python -c "import zmasterprint.__version__ as v; print(v.VERSION)"') do (
    set APP_VERSION=%%v
)

echo Building %APP_NAME% version %APP_VERSION%

REM === Virtualenv ===
if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r "%PROJECT_ROOT%\requirements.txt"
pip install pyinstaller

REM === Geração de UI / recursos ===
python "%PROJECT_ROOT%\scripts\generate_ui.py"

REM === Limpa builds anteriores ===
rmdir /s /q "%SCRIPT_DIR%\dist" 2>nul
rmdir /s /q "%SCRIPT_DIR%\build" 2>nul

REM === Build PyInstaller ===
pyinstaller ^
  --name %PKG_NAME% ^
  --onedir ^
  --noconsole ^
  --noupx ^
  --clean ^
  --noconfirm ^
  --icon "%PROJECT_ROOT%\zmasterprint\icons\zmasterprint.ico" ^
  --distpath "%SCRIPT_DIR%\dist" ^
  --workpath "%SCRIPT_DIR%\build" ^
  --add-data "%PROJECT_ROOT%\zmasterprint\generated\about_reqs.html;generated" ^
  "%PROJECT_ROOT%\zmasterprint\main.py"

deactivate

echo.
echo Build concluído com sucesso!
echo Saída em:
echo %SCRIPT_DIR%\dist\%PKG_NAME%
pause
