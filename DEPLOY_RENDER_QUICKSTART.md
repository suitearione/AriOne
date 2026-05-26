# Deploy Gratuito no Render - Quick Start

## Passos Rápidos (10 minutos)

### 1. Preparar Repositório GitHub
```bash
git add .
git commit -m "Preparando para deploy no Render"
git push origin main
```

### 2. Criar Conta no Render
1. Acesse: https://render.com
2. Clique em "Sign Up with GitHub"
3. Verifique o email

### 3. Criar Web Service
1. No dashboard, clique em "New +"
2. Selecione "Web Service"
3. Conecte seu repositório GitHub
4. Selecione o repositório do AriOne
5. Render detectará automaticamente o `render.yaml`
6. Clique em "Create Web Service"

### 4. Criar Banco de Dados
1. No dashboard, clique em "New +"
2. Selecione "PostgreSQL"
3. Configure:
   - Name: `arione-db`
   - Database: `arione`
   - User: `arione`
4. Clique em "Create Database"

### 5. Conectar Banco ao Web Service
1. Vá para o Web Service criado
2. Clique em "Environment"
3. Adicione variável:
   - Key: `DATABASE_URL`
   - Value: (copie do PostgreSQL dashboard)
4. Clique em "Save Changes"

### 6. Acessar Aplicação
1. Aguarde o deploy (5-10 minutos)
2. Acesse: `https://arione-erp.onrender.com`

## Importante

### Cold Start (Sleep)
O serviço "dorme" após 15 minutos sem uso. Primeira requisição leva 30-60s.

**Solução:** Configure ping automático em https://uptimerobot.com (gratuito)

### PostgreSQL Gratuito
PostgreSQL é gratuito por 90 dias. Depois: $7/mês.

**Alternativa:** Use Neon (https://neon.tech) - PostgreSQL gratuito generoso

## Variáveis de Ambiente

No Render, adicione também:
```
SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=production
```

## Documentação Completa

Veja `doc_tec_oper/02_Infraestrutura/DEPLOY_RENDER_GRATUITO.md` para detalhes completos.

## Suporte

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
