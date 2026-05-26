@echo off
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VENV_PYTHON_DIR=C:\AriOneDEV\.venv\Scripts"
set "PYTHON_EXE=%VENV_PYTHON_DIR%\AriOneServer.exe"
set "SCRIPT_PY=C:\AriOneDEV\tray_manager.py"
set "SHORTCUT_NAME=AriOneDEV.lnk"

echo Preparando executavel personalizado AriOne...
if not exist "%VENV_PYTHON_DIR%\AriOneServer.exe" (
    copy "%VENV_PYTHON_DIR%\pythonw.exe" "%VENV_PYTHON_DIR%\AriOneServer.exe" >nul
)

echo Criando atalho de inicializacao automatica para o AriOne...

powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_DIR%\%SHORTCUT_NAME%'); $Shortcut.TargetPath = '%PYTHON_EXE%'; $Shortcut.Arguments = '\"%SCRIPT_PY%\"'; $Shortcut.WorkingDirectory = 'C:\AriOneDEV'; $Shortcut.Save()"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Sucesso! O AriOne agora aparecera como "AriOneServer" na inicializacao.
    echo O servidor ficara oculto na bandeja proximo ao relogio.
) else (
    echo.
    echo Ocorreu um erro ao criar o atalho.
)
pause
