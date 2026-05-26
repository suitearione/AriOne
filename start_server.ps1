# ==============================================================================
# ARI ONE - SISTEMA DE GESTÃO INTEGRADA
# SCRIPT DE INICIALIZAÇÃO DO SERVIDOR
# ==============================================================================

Clear-Host
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         ARI ONE - NEXUS DEVELOPMENT ENVIRONMENT         " -ForegroundColor White -BackgroundColor Blue
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Definindo Caminhos
$VENV_PATH = ".\.venv\Scripts\Activate.ps1"

if (Test-Path $VENV_PATH) {
    Write-Host "[🚀] Ativando Ambiente Virtual (.venv)..." -ForegroundColor Yellow
    . $VENV_PATH
    Write-Host "[✅] Ambiente Ativado com Sucesso!" -ForegroundColor Green
} else {
    Write-Host "[⚠️] Ambiente Virtual não encontrado em $VENV_PATH" -ForegroundColor Red
    Write-Host "[ℹ️] Tentando executar com o Python global..." -ForegroundColor Gray
}

Write-Host "[🔥] Iniciando Gerenciador AriOne na Bandeja de Sistema..." -ForegroundColor Cyan
Write-Host "[💡] O servidor rodará em segundo plano." -ForegroundColor Gray
Write-Host ""
Write-Host "----------------------------------------------------------" -ForegroundColor Cyan

# Executando o servidor via Gerenciador de Bandeja
python tray_manager.py
