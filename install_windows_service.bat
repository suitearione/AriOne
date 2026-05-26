@echo off
REM =============================================================================
REM Script para Instalar AriOne como Serviço do Windows usando NSSM
REM Pré-requisito: Baixe e instale NSSM de https://nssm.cc/download
REM =============================================================================

echo Instalando AriOne como Servico do Windows...
echo.

REM Verifica se NSSM está instalado
where nssm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: NSSM nao encontrado.
    echo Por favor, baixe e instale NSSM de https://nssm.cc/download
    echo Adicione o NSSM ao PATH do sistema.
    pause
    exit /b 1
)

REM Obtém o caminho completo do diretório atual
set "ARIONE_PATH=%~dp0"
set "ARIONE_PATH=%ARIONE_PATH:~0,-1%"

REM Caminho do Python virtualenv
set "PYTHON_PATH=%ARIONE_PATH%\venv\Scripts\python.exe"

REM Caminho do script run.py
set "RUN_SCRIPT=%ARIONE_PATH%\run.py"

REM Nome do serviço
set "SERVICE_NAME=AriOneERP"

echo Caminho do AriOne: %ARIONE_PATH%
echo Caminho do Python: %PYTHON_PATH%
echo Script: %RUN_SCRIPT%
echo.

REM Remove serviço existente se houver
echo Removendo servico existente (se houver)...
nssm stop %SERVICE_NAME% >nul 2>&1
nssm remove %SERVICE_NAME% confirm >nul 2>&1

REM Instala o serviço
echo Instalando novo servico...
nssm install %SERVICE_NAME% "%PYTHON_PATH%" "%RUN_SCRIPT%"

REM Configura o serviço
nssm set %SERVICE_NAME% AppDirectory "%ARIONE_PATH%"
nssm set %SERVICE_NAME% DisplayName "AriOne ERP System"
nssm set %SERVICE_NAME% Description "Sistema ERP AriOne - Sistema de Gestao Empresarial"
nssm set %SERVICE_NAME% Start SERVICE_AUTO_START
nssm set %SERVICE_NAME% AppEnvironmentExtra "FLASK_ENV=production" "FLASK_DEBUG=0"

REM Configura logs
nssm set %SERVICE_NAME% AppStdout "%ARIONE_PATH%\logs\arione_stdout.log"
nssm set %SERVICE_NAME% AppStderr "%ARIONE_PATH%\logs\arione_stderr.log"
nssm set %SERVICE_NAME% AppRotateFiles 1
nssm set %SERVICE_NAME% AppRotateBytes 10485760

REM Configura recuperação em caso de falha
nssm set %SERVICE_NAME% AppRestartDelay 10000
nssm set %SERVICE_NAME% AppThrottle 1500
nssm set %SERVICE_NAME% AppExit Default Restart
nssm set %SERVICE_NAME% AppRestart Default Restart

echo.
echo Servico instalado com sucesso!
echo.
echo Comandos uteis:
echo   Iniciar:   nssm start %SERVICE_NAME%
echo   Parar:     nssm stop %SERVICE_NAME%
echo   Reiniciar: nssm restart %SERVICE_NAME%
echo   Remover:   nssm remove %SERVICE_NAME% confirm
echo   Status:    sc query %SERVICE_NAME%
echo.
echo Iniciando o servico...
nssm start %SERVICE_NAME%

if %ERRORLEVEL% EQU 0 (
    echo Servico iniciado com sucesso!
    echo AriOne esta rodando em http://0.0.0.0:5000
) else (
    echo Erro ao iniciar servico. Verifique os logs em %ARIONE_PATH%\logs\
)

pause
