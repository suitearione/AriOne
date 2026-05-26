# =============================================================================
# Script de Inicialização AriOne - Desenvolvimento e Produção
# =============================================================================

import os
import sys

# Adiciona o diretório raiz ao PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import create_app

# Cria a aplicação
app = create_app()

if __name__ == '__main__':
    # Modo Desenvolvimento (Flask dev server)
    # Use este apenas para desenvolvimento local
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
