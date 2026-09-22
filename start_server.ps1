# ==============================================================================
# ARI ONE - SISTEMA DE GESTÃO INTEGRADA
# SCRIPT DE INICIALIZAÇÃO DO SERVIDOR
# ==============================================================================

Clear-Host
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         ARI ONE - NEXUS DEVELOPMENT ENVIRONMENT         " -ForegroundColor White -BackgroundColor Blue
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[🚀] Iniciando o Ambiente Virtual (.venv)..." -ForegroundColor Yellow

# Executa o Python do ambiente virtual direto, sem precisar ativar script de terceiros
& ".\.venv\Scripts\python.exe" tray_manager.py

Write-Host ""
Write-Host "----------------------------------------------------------" -ForegroundColor Cyan