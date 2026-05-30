Passo a Passo - Deploy Manual:

1. Finalizar Desenvolvimento

No AriOne, verificar se há versões em DEV
Se houver, publicar a versão (mudar status para "publicada")
Documentar changelog e arquivos modificados
2. Commitar no Git (AriOneDEV)

bash
cd c:\AriOneDEV
git add .
git commit -m "vX.X.X: Descrição da versão"
git push origin develop
3. Merge para Main

bash
git checkout main
git pull origin main
git merge develop
git push origin main
4. Deploy no Render

Acessar https://dashboard.render.com/web/services/suitearione
Clicar em "Manual Deploy"
Selecionar branch main
Clicar em "Deploy Now"
Acompanhar nos logs
5. Verificação

Acessar https://suitearione.onrender.com
Testar funcionalidades críticas
Verificar logs no Render se houver erro
Checklist Rápido:

Versões publicadas no AriOne?
Commit feito no develop?
Merge para main?
Push para GitHub?
Deploy no Render iniciado?
Aplicação funcionando?
Esse processo garante que só código versionado e testado vai para produção.