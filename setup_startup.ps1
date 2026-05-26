$WshShell = New-Object -ComObject WScript.Shell
$StartupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$ShortcutPath = Join-Path $StartupPath "AriOneServer.lnk"

$PythonPath = "C:\AriOneDEV\.venv\Scripts\pythonw.exe"
$ScriptPath = "C:\AriOneDEV\tray_manager.py"
$WorkDir = "C:\AriOneDEV"

if (Test-Path $ShortcutPath) {
    Remove-Item $ShortcutPath
}

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonPath
$Shortcut.Arguments = "`"$ScriptPath`""
$Shortcut.WorkingDirectory = $WorkDir
$Shortcut.IconLocation = "$WorkDir\static\favicon.ico" # Tenta usar o favicon se existir
$Shortcut.Description = "Servidor AriOne (Segundo Plano)"
$Shortcut.Save()

Write-Host "✅ Atalho de Inicialização criado com sucesso em: $ShortcutPath"
Write-Host "O AriOne agora iniciará automaticamente com o Windows em segundo plano (na bandeja)."
