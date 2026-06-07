@echo off
setlocal enabledelayedexpansion

SET "ORIGEM=C:\AriOneDEV"
SET "DESTINO=C:\AriOne"
SET "HASH_DEV=%ORIGEM%\.hash_dev"
SET "HASH_PROD=%DESTINO%\.hash_prod"

:: Calcula um HASH dos arquivos .py para verificar mudancas
echo Calculando integridade do codigo...
dir /s /b "%ORIGEM%\*.py" | certutil -hashfile - > "%HASH_DEV%"

:: Compara o hash atual com o da ultima execucao
if exist "%HASH_PROD%" (
    fc "%HASH_DEV%" "%HASH_PROD%" >nul
    if !errorlevel! equ 0 (
        echo ==================================================
        echo Nenhuma alteracao detectada no codigo.
        echo Deploy nao necessario.
        echo ==================================================
        del "%HASH_DEV%"
        goto :FIM
    )
)

echo Alteracao detectada! Iniciando Deploy...
robocopy "%ORIGEM%" "%DESTINO%" /E /MIR /XD venv .git __pycache__ .idea /XF .env *.db *.log *.pyc .hash_prod
copy "%HASH_DEV%" "%HASH_PROD%" >nul
del "%HASH_DEV%"

echo ==================================================
echo Deploy realizado com sucesso!
echo ==================================================

:FIM
pause