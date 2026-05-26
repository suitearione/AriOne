# ============================================================ 
# 🟪 ARIONEDEV – UTILITÁRIO DE LOGO DA EMPRESA                 
# 📂 Local: /AriOneDev/utils/empresa_logo.py                   
# 🔧 Função: Fornecer URL da logo global da empresa            
# ============================================================ 

import os
from flask import current_app, url_for

def get_logo_empresa():
    """
    Retorna a URL da logo da empresa, se existir.
    Se não existir, retorna a logo padrão.
    """

    caminho_arquivo = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "logo_empresa",
        "logo_empresa.png"
    )

    # Se o arquivo existe → retorna ele
    if os.path.exists(caminho_arquivo):
        return url_for("static", filename="uploads/logo_empresa/logo_empresa.png")

    # Se não → usa logo padrão
    return url_for("static", filename="img/logo_padrao_empresa.png")
