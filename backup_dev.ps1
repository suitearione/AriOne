param($origem, $zip)

$excluir = @('backups','venv','.venv','env','node_modules','__pycache__','.git','.github','.idea','.vscode','.pytest_cache','.mypy_cache','dist','build','uploads','media','arquivos','relatorios','storage')
$extExcluir = @('*.db','*.sqlite','*.sqlite3','*.db3','*.log','*.tmp','*.temp','*.bak','*.pyc','*.pyo','*.pyd','*.md','*.rst','*.key','*.pem','*.p12','*.pfx','.env','deploy_arione.bat')

$arquivos = Get-ChildItem -Path $origem -Recurse -File | Where-Object {
    $rel = $_.FullName.Substring($origem.Length + 1)
    $partes = $rel -split '\\'
    $emPastaExcluida = $false
    foreach ($p in $partes[0..($partes.Length-2)]) {
        if ($excluir -contains $p) { $emPastaExcluida = $true; break }
    }
    $extExcluida = $false
    foreach ($e in $extExcluir) {
        if ($_.Name -like $e) { $extExcluida = $true; break }
    }
    -not $emPastaExcluida -and -not $extExcluida
}

if ($arquivos) {
    Compress-Archive -Path $arquivos.FullName -DestinationPath $zip -Force -CompressionLevel Optimal
    Write-Host "OK"
} else {
    Write-Error "Nenhum arquivo encontrado para backup!"
    exit 1
}
