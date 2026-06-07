@echo off
TITLE ARI ONE - SERVIDOR
COLOR 0B
CLS

echo ==========================================================
echo          ARI ONE - NEXUS DEVELOPMENT ENVIRONMENT         
echo ==========================================================
echo.

set VENV_PATH=.\.venv\Scripts\activate.bat

if exist %VENV_PATH% (
    echo [🚀] Ativando Ambiente Virtual (.venv)...
    call %VENV_PATH%
    echo [✅] Ambiente Ativado!
) else (
    echo [⚠️] Ambiente Virtual nao encontrado.
)

echo [🔥] Iniciando Gerenciador AriOne na Bandeja de Sistema...
echo [💡] O servidor rodara em segundo plano.
echo.
echo ----------------------------------------------------------

python tray_manager.py

pause
