@echo off
setlocal enabledelayedexpansion

SET "ORIGEM=C:\AriOneDEV"
SET "DESTINO=C:\AriOne"
SET "HASH_DEV=%TEMP%\hash_arione_dev.txt"
SET "HASH_PROD=%DESTINO%\.hash_prod"
SET "LOG=%DESTINO%\deploy.log"
SET "BACKUP_DEV=%ORIGEM%\backups"
SET "BACKUP_PROD=%DESTINO%\backups"
SET "MAX_BACKUPS_DEV=2"
SET "MAX_BACKUPS_PROD=3"
SET "PS_BACKUP_DEV=%ORIGEM%\backup_dev.ps1"

:: ================================================
:: Captura data e hora
:: ================================================
for /f "tokens=1-3 delims=/" %%a in ("%date%") do (
    SET "DIA=%%a"
    SET "MES=%%b"
    SET "ANO=%%c"
)
for /f "tokens=1-3 delims=:." %%a in ("%time%") do (
    SET "HORA=%%a"
    SET "MIN=%%b"
    SET "SEG=%%c"
)
SET "HORA=!HORA: =0!"
SET "DATAHORA=!DIA!/!MES!/!ANO! !HORA!:!MIN!:!SEG!"
SET "DATATAG=!DIA!-!MES!-!ANO!_!HORA!-!MIN!"

:: ================================================
:: Cria pastas de backup se nao existirem
:: ================================================
if not exist "%BACKUP_DEV%" mkdir "%BACKUP_DEV%"
if not exist "%BACKUP_PROD%" mkdir "%BACKUP_PROD%"

echo ==================================================
echo  DEPLOY ARIONE - !DATAHORA!
echo ==================================================

:: ================================================
:: PASSO 1 - Para o AriOne (libera o banco)
:: ================================================
echo.
echo [1/6] Parando o AriOne em producao...
taskkill /F /IM python.exe /T >nul 2>&1
if !errorlevel! equ 0 (
    echo       OK - AriOne parado com sucesso.
    echo [!DATAHORA!] AriOne parado para deploy. >> "%LOG%"
) else (
    echo       AVISO - Nenhum processo Python encontrado. Continuando...
    echo [!DATAHORA!] AVISO - Nenhum processo Python ativo encontrado. >> "%LOG%"
)
:: Aguarda 3 segundos para garantir que o banco foi liberado
timeout /t 3 /nobreak >nul

:: ================================================
:: PASSO 2 - ZIP da origem AriOneDEV (so codigo fonte)
:: ================================================
echo.
echo [2/6] Gerando backup de AriOneDEV...
SET "ZIP_DEV=%BACKUP_DEV%\AriOneDEV_backup_%DATATAG%.zip"

powershell -ExecutionPolicy Bypass -File "%PS_BACKUP_DEV%" -origem "%ORIGEM%" -zip "%ZIP_DEV%"

if exist "%ZIP_DEV%" (
    echo       OK - AriOneDEV_backup_%DATATAG%.zip
    echo [!DATAHORA!] BACKUP DEV gerado: %ZIP_DEV% >> "%LOG%"
) else (
    echo.
    echo ==================================================
    echo  ABORTADO - Falha ao gerar backup do AriOneDEV!
    echo  Nenhum arquivo foi alterado em producao.
    echo  Verifique permissoes da pasta: %BACKUP_DEV%
    echo ==================================================
    echo [!DATAHORA!] ERRO - Falha no backup DEV. Deploy abortado. >> "%LOG%"
    echo -------------------------------------------------- >> "%LOG%"
    goto :SUBIR
)

:: Mantem apenas os 2 backups mais recentes no DEV
SET "COUNT=0"
for /f "delims=" %%f in ('dir /b /o-d "%BACKUP_DEV%\AriOneDEV_backup_*.zip" 2^>nul') do (
    SET /a COUNT+=1
    if !COUNT! GTR %MAX_BACKUPS_DEV% (
        echo       Removendo backup antigo DEV: %%f
        echo [!DATAHORA!] BACKUP DEV REMOVIDO: %%f >> "%LOG%"
        del "%BACKUP_DEV%\%%f"
    )
)

:: ================================================
:: PASSO 3 - ZIP da producao AriOne (completo + banco)
:: ================================================
echo.
echo [3/6] Gerando backup de AriOne...
SET "ZIP_PROD=%BACKUP_PROD%\AriOne_backup_%DATATAG%.zip"

powershell -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%DESTINO%\*' -DestinationPath '%ZIP_PROD%' -Force -CompressionLevel Optimal"

if exist "%ZIP_PROD%" (
    echo       OK - AriOne_backup_%DATATAG%.zip
    echo [!DATAHORA!] BACKUP PROD gerado: %ZIP_PROD% >> "%LOG%"
) else (
    echo.
    echo ==================================================
    echo  ABORTADO - Falha ao gerar backup do AriOne!
    echo  Nenhum arquivo foi alterado em producao.
    echo  Verifique permissoes da pasta: %BACKUP_PROD%
    echo ==================================================
    echo [!DATAHORA!] ERRO - Falha no backup PROD. Deploy abortado. >> "%LOG%"
    echo -------------------------------------------------- >> "%LOG%"
    goto :SUBIR
)

:: Mantem apenas os 3 backups mais recentes na PROD
SET "COUNT=0"
for /f "delims=" %%f in ('dir /b /o-d "%BACKUP_PROD%\AriOne_backup_*.zip" 2^>nul') do (
    SET /a COUNT+=1
    if !COUNT! GTR %MAX_BACKUPS_PROD% (
        echo       Removendo backup antigo PROD: %%f
        echo [!DATAHORA!] BACKUP PROD REMOVIDO: %%f >> "%LOG%"
        del "%BACKUP_PROD%\%%f"
    )
)

:: ================================================
:: PASSO 4 - Verifica hash (houve mudanca?)
:: ================================================
echo.
echo [4/6] Calculando integridade do codigo...

powershell -ExecutionPolicy Bypass -Command "Get-ChildItem '%ORIGEM%' -Recurse -Filter *.py | Get-FileHash | Select-Object -ExpandProperty Hash | Out-File '%HASH_DEV%' -Encoding utf8"

if exist "%HASH_PROD%" (
    fc "%HASH_DEV%" "%HASH_PROD%" >nul 2>&1
    if !errorlevel! equ 0 (
        echo       Nenhuma alteracao detectada. Deploy nao necessario.
        echo [!DATAHORA!] SEM ALTERACAO - Deploy nao necessario. >> "%LOG%"
        echo -------------------------------------------------- >> "%LOG%"
        del "%HASH_DEV%"
        goto :SUBIR
    )
)

:: ================================================
:: PASSO 5 - Deploy
:: ================================================
echo.
echo [5/6] Alteracao detectada! Iniciando Deploy...
echo [!DATAHORA!] INICIANDO Deploy de "%ORIGEM%" para "%DESTINO%" >> "%LOG%"

robocopy "%ORIGEM%" "%DESTINO%" /E /MIR ^
  /XD venv .venv env node_modules __pycache__ .idea .vscode .git .github ^
      .pytest_cache .mypy_cache dist build ^
      uploads backups media arquivos relatorios storage ^
  /XF .env .env.* config.ini secrets.json credentials.json ^
      *.db *.sqlite *.sqlite3 *.db3 ^
      *.log *.log.* *.tmp *.temp *.bak ^
      *.pyc *.pyo *.pyd ^
      *.md *.rst *.txt ^
      *.key *.pem *.p12 *.pfx ^
      *.DS_Store Thumbs.db desktop.ini ^
      deploy_arione.bat backup_dev.ps1 ^
      .hash_prod deploy.log

if !errorlevel! GTR 7 (
    echo.
    echo ==================================================
    echo  ERRO no Deploy! Verifique o log: %LOG%
    echo ==================================================
    echo [!DATAHORA!] ERRO - Deploy falhou. Errorlevel: !errorlevel! >> "%LOG%"
    echo -------------------------------------------------- >> "%LOG%"
    del "%HASH_DEV%"
    goto :SUBIR
)

copy "%HASH_DEV%" "%HASH_PROD%" >nul
del "%HASH_DEV%"

echo.
echo ==================================================
echo  Deploy realizado com sucesso!
echo ==================================================
echo [!DATAHORA!] SUCESSO - Deploy concluido sem erros. >> "%LOG%"
echo -------------------------------------------------- >> "%LOG%"

:: ================================================
:: PASSO 6 - Sobe o AriOne novamente
:: ================================================
:SUBIR
echo.
echo [6/6] Iniciando AriOne em producao...
start "AriOne" /D "%DESTINO%" cmd /k "python main.py"
echo       OK - AriOne iniciado em nova janela.
echo [!DATAHORA!] AriOne iniciado apos deploy. >> "%LOG%"

echo.
echo ==================================================
echo  Concluido! AriOne esta rodando em producao.
echo ==================================================

:FIM
pause
