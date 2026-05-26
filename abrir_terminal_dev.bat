@echo off
TITLE ARI ONE - DEVELOPER TERMINAL
COLOR 0A
cd /d "%~dp0"

echo ==========================================================
echo          ARIONE - NEXUS DEVELOPMENT TERMINAL
echo ==========================================================
echo.

if exist .venv\Scripts\activate.bat (
    echo [🚀] Ativando Ambiente Virtual (.venv)...
    call otao expoatr.bat
    echo [✅] Ambiente Ativado! Pronto para o trabalho.
) else (
    echo [⚠️] Ambiente Virtual nao encontrado.
    echo [ℹ️] Execute 'python -m venv .venv' para criar um.
)

echo.
echo ----------------------------------------------------------
cmd /k
