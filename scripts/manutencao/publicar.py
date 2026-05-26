import os
import subprocess
import time
import sys
import json
import re

def update_status(step, percent=0, message="", status="running"):
    """Salva o progresso em um arquivo JSON para o Flask ler"""
    data = {
        "step": step,
        "percent": percent,
        "message": message,
        "status": status,
        "updated_at": time.time()
    }
    try:
        # Garante que a pasta instance existe
        if not os.path.exists("instance"): os.makedirs("instance")
        with open("instance/deploy_status.json", "w") as f:
            json.dump(data, f)
    except: pass

def encerrar_processos_destino(diretorio_destino):
    update_status("cleaning", 5, "Limpando processos na pasta de destino...")
    origem_blindada = r"C:\AriOneDEV".lower()
    destino_exato = r"C:\AriOne".lower()
    
    try:
        # Pega o PID atual e o PID do pai (Flask) para proteção total
        meu_pid = str(os.getpid())
        pai_pid = ""
        try:
            import psutil
            pai_pid = str(os.getppid())
        except: pass

        # Pega todos os processos python com seus caminhos
        cmd = 'wmic process where "name=\'python.exe\'" get ExecutablePath,ProcessId'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='replace')
        
        for line in output.splitlines():
            line = line.strip()
            if not line or "ExecutablePath" in line: continue
            
            # Divide a linha para pegar o caminho e o PID
            parts = line.rsplit(None, 1)
            if len(parts) < 2: continue
            path, pid = parts[0].lower(), parts[1]

            # 🛡️ PROTEÇÃO SUPREMA: Nunca mata a si mesmo ou ao pai (Flask)
            if pid == meu_pid or pid == pai_pid:
                continue

            # 🛡️ REGRA DE OURO: Só mata se estiver EXATAMENTE na pasta de destino
            if path.startswith(destino_exato + "\\") and origem_blindada not in path:
                # Se o PID for o que estamos usando agora, ignoramos (camada extra)
                if pid == meu_pid: continue
                # Log de segurança (opcional)
                with open("instance/kill_log.txt", "a") as log:
                    log.write(f"[{time.ctime()}] Encerrando PROD: {path} (PID: {pid})\n")
                
                subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                time.sleep(0.5)
            else:
                # Log de proteção do DEV
                if origem_blindada in path:
                    pass # Protegido!
    except Exception as e:
        with open("instance/kill_log.txt", "a") as log:
            log.write(f"[{time.ctime()}] Erro na limpeza: {str(e)}\n")

def publicar():
    origem = r"C:\AriOneDEV"
    destino = r"C:\AriOne"
    
    update_status("initializing", 10, "Preparando motor de sincronia...")
    encerrar_processos_destino(destino)
    
    if not os.path.exists(destino): os.makedirs(destino)

    # Configuração do ROBOCOPY
    pastas_ignoradas = [".git", ".venv", "venv", "__pycache__", ".vscode", "Bacukps", ".local", "brain", "instance"]
    arquivos_ignorados = ["*.rar", "*.pyc", ".env.backup", "*.log"]

    comando = ["robocopy", origem, destino, "/MIR", "/FFT", "/Z", "/MT:32", "/R:3", "/W:5", "/NP", "/NDL"]

    if pastas_ignoradas:
        comando.append("/XD")
        comando.extend(pastas_ignoradas)
    if arquivos_ignorados:
        comando.append("/XF")
        comando.extend(arquivos_ignorados)

    update_status("copying", 15, "Iniciando Robocopy...")
    
    try:
        # Executa capturando a saída em tempo real
        processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
        
        # Prepara arquivo de log
        log_path = "instance/sync_report.log"
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write(f"=== RELATÓRIO DE SINCRONIZAÇÃO ARIONE - {time.ctime()} ===\n")
            log_file.write(f"ORIGEM: {origem}\nDESTINO: {destino}\n\n")

            for line in iter(processo.stdout.readline, ""):
                log_file.write(line)
                # Tenta encontrar o percentual na linha (Padrão Robocopy: "  10.5%")
                match = re.search(r"(\d+)%", line)
                if match:
                    perc = int(match.group(1))
                    real_perc = 15 + int(perc * 0.8)
                    update_status("copying", real_perc, f"Copiando arquivos: {perc}%")
        
        processo.wait()
        
        if processo.returncode < 8:
            update_status("finished", 100, "Sincronização realizada com sucesso!", "success")
            time.sleep(5) # Mantém o status 100% por um tempo
            update_status("idle", 0, "", "idle")
        else:
            update_status("error", 0, f"Erro no Robocopy (Cod: {processo.returncode})", "error")
            
    except Exception as e:
        update_status("error", 0, str(e), "error")

if __name__ == "__main__":
    publicar()
