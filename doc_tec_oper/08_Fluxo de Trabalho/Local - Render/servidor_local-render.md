Fluxo de trabalho: Local → Render

[Seu PC - AriOneDEV]  →  [GitHub]  →  [Render - Produção]
      Edita código         Push          Deploy automático

Como funciona:
Você edita localmente no seu PC (aqui no VS Code)
Commit + Push para o GitHub:
git add .
git commit -m "descrição da alteração"
git push origin main
Render detecta automaticamente o push e faz o deploy (2-5 min)
Site atualizado em https://suitearione.onrender.com/

Resumo rápido:
Ação	Onde
Desenvolver/testar	Seu PC (localhost)
Versionar código	Git (commit)
Enviar para produção	git push origin main
Deploy	Render faz sozinho

Importante:
NÃO se edita no servidor — o Render é read-only, ele reconstrói tudo a cada push
Tudo passa pelo Git — é seu histórico e backup
Cada push = novo deploy — então teste localmente antes de subir
Seu fluxo diário:
Abre o VS Code → faz alterações
Testa local (se quiser)
git add . → git commit -m "..." → git push origin main
Espera 2-5 min → site atualizado
É exatamente o que fizemos ontem — cada fix que eu fazia, commitava e pushava, e o Render deployava automaticamente.