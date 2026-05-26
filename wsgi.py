# =============================================================================
# WSGI Entry Point for AriOne ERP
# =============================================================================
# Este arquivo é o ponto de entrada para o Gunicorn em produção
# Ele chama a factory create_app() e expõe o objeto app WSGI

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
