Fluxo ideal:
PC Local → branch dev (push) → Render DEV (testa online) → main (deploy produção)

Na prática:
Desenvolve no PC (aqui no VS Code)
Push para dev → Render deploya no ambiente DEV
Testa online no ambiente DEV (mesmo Linux, mesmo PostgreSQL)
Tudo OK? → Merge dev → main → Render deploya em produção
Para configurar isso:
Você precisa de 2 serviços no Render:

Serviço	Branch	URL	Banco
suitearione-dev	dev	suitearione-dev.onrender.com	arione-db-dev
suitearione	main	suitearione.onrender.com	arione-db

Vantagem:
✅ Testa no mesmo ambiente que produção (Linux + PostgreSQL + SSL)
✅ Se funcionar no DEV, vai funcionar no MAIN
✅ Produção nunca quebra