import subprocess
import threading
import os
import sys
import webbrowser
import signal
try:
    from PIL import Image
    import pystray
    from pystray import MenuItem as item
except ImportError:
    print("Dependências faltando. Instalando pystray e Pillow...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pystray", "Pillow"])
    from PIL import Image
    import pystray
    from pystray import MenuItem as item

# --- Configurações ---
from dotenv import load_dotenv
load_dotenv()

APP_NAME = "AriOne DEV"
SERVER_CMD = [sys.executable, "main.py"]
PORT = os.getenv("FLASK_PORT", "8081")
USE_HTTPS = os.getenv("USE_HTTPS", "False").lower() == "true"
PROTOCOL = "https" if USE_HTTPS else "http"
URL = f"{PROTOCOL}://localhost:{PORT}"
ICON_PATH = "arione_tray_icon.png" # Usaremos a imagem gerada

class AriOneTray:
    def __init__(self):
        self.process = None
        self.icon = None
        self.running = True

    def start_server(self):
        """Inicia o processo do servidor Flask"""
        if self.process:
            self.stop_server()
        
        # Inicia o main.py em um novo processo
        self.process = subprocess.Popen(
            SERVER_CMD, 
            cwd=os.path.dirname(os.path.abspath(__file__)),
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        print(f"Servidor iniciado com PID: {self.process.pid}")

    def stop_server(self):
        """Finaliza o processo do servidor"""
        if self.process:
            if os.name == 'nt':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
            else:
                self.process.terminate()
            self.process = None

    def open_system(self, icon, item):
        webbrowser.open(URL)

    def restart_server(self, icon, item):
        self.start_server()
        icon.notify("Servidor Reiniciado", "O sistema AriOne foi reiniciado com sucesso.")

    def on_quit(self, icon, item):
        self.running = False
        self.stop_server()
        icon.stop()

    def run(self):
        # Tenta carregar o ícone premium gerado
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_icon = os.path.join(script_dir, "tray_icon.png")
        remote_icon = r"C:\Users\Arisvan\.gemini\antigravity\brain\9623803a-6bf8-479f-b92d-407c00596b46\media__1777336900143.png"

        if os.path.exists(local_icon):
            image = Image.open(local_icon)
        elif os.path.exists(remote_icon):
            image = Image.open(remote_icon)
        else:
            # Fallback elegante (Ciano Vibrante para DEV)
            image = Image.new('RGB', (64, 64), color=(0, 255, 255)) 

        # Menu de contexto
        menu = pystray.Menu(
            item('🌐 Abrir Sistema', self.open_system),
            item('🔄 Reiniciar Servidor', self.restart_server),
            pystray.Menu.SEPARATOR,
            item('❌ Sair', self.on_quit)
        )

        self.icon = pystray.Icon("AriOne", image, APP_NAME, menu)
        
        # Inicia o servidor em uma thread separada para não bloquear a GUI do ícone
        self.start_server()
        
        # Roda o ícone (isso bloqueia a thread principal)
        self.icon.run()

if __name__ == "__main__":
    tray = AriOneTray()
    tray.run()
