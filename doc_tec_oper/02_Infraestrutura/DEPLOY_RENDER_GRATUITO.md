# Deploy Gratuito no Render

## Visão Geral

Este guia detalha o deploy do AriOne ERP no Render com plano gratuito.

## Por que Render?

**Vantagens do Plano Gratuito:**
- **Web Service:** 750 horas/mês (suficiente para testes)
- **PostgreSQL:** 90 dias grátis, depois $7/mês
- **Deploy automático** via GitHub
- **SSL automático** (HTTPS)
- **Domínio gratuito:** `.onrender.com`
- **Fácil de usar:** Interface intuitiva

**Limitações:**
- Web service "sleep" após 15 minutos de inatividade
- Primeira requisição pode levar 30-60 segundos (cold start)
- PostgreSQL gratuito por 90 dias
- Sem domínio customizado no plano gratuito

## Pré-requisitos

1. **Conta no GitHub** (gratuita)
2. **Conta no Render** (gratuita)
3. **Código no GitHub** (repositório público ou privado)

## Passo a Passo

### 1. Preparar o Repositório

#### 1.1. Criar arquivo `render.yaml`
Este arquivo configura automaticamente o deploy no Render.

```yaml
services:
  - type: web
    name: arione-erp
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app.app:create_app() --bind 0.0.0.0:$PORT
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PYTHONUNBUFFERED
        value: 1

databases:
  - name: arione-db
    databaseName: arione
    user: arione
```

#### 1.2. Atualizar `requirements.txt`
Certifique-se que tem:
```
Flask
SQLAlchemy
Flask-SQLAlchemy
Flask-Login
python-dotenv
psycopg2-binary
gunicorn
```

#### 1.3. Atualizar `app/app.py` para usar variável de ambiente
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Usa DATABASE_URL do Render ou SQLite local
database_url = os.getenv('DATABASE_URL', 'sqlite:///instance/arione.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://')

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
```

#### 1.4. Commit e push no GitHub
```bash
git add .
git commit -m "Preparando para deploy no Render"
git push origin main
```

### 2. Criar Conta no Render

1. Acesse: https://render.com
2. Clique em "Sign Up"
3. Use GitHub para autenticar
4. Verifique o email

### 3. Criar Web Service

1. No dashboard, clique em "New +"
2. Selecione "Web Service"
3. Conecte seu repositório GitHub
4. Selecione o repositório do AriOne
5. Configure:
   - **Name:** `arione-erp`
   - **Region:** Oregon (mais próximo do Brasil)
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app.app:create_app() --bind 0.0.0.0:$PORT`
6. Clique em "Create Web Service"

### 4. Criar Banco de Dados PostgreSQL

1. No dashboard, clique em "New +"
2. Selecione "PostgreSQL"
3. Configure:
   - **Name:** `arione-db`
   - **Database:** `arione`
   - **User:** `arione`
4. Clique em "Create Database"

### 5. Conectar Web Service ao Banco

1. Vá para o Web Service criado
2. Clique em "Environment"
3. Adicione variável de ambiente:
   - **Key:** `DATABASE_URL`
   - **Value:** (copie do PostgreSQL dashboard, "Internal Database URL")
4. Clique em "Save Changes"
5. O serviço reiniciará automaticamente

### 6. Acessar a Aplicação

1. Aguarde o deploy terminar (5-10 minutos)
2. O Render fornecerá uma URL: `https://arione-erp.onrender.com`
3. Acesse a URL no navegador

## Migração de Dados

### Opção 1: Começar do zero (recomendado para testes)
O banco PostgreSQL será criado vazio. Você pode:
- Cadastrar dados manualmente
- Importar via script de migração

### Opção 2: Migrar do SQLite
Se você tem dados no SQLite local:

1. Exporte do SQLite:
```bash
python scripts/manutencao/migrate_to_postgres.py
```

2. Configure a variável `DATABASE_URL` no Render com seu PostgreSQL local temporariamente
3. Execute o script de migração
4. Volte para o PostgreSQL do Render

## Variáveis de Ambiente Adicionais

No Render, adicione estas variáveis:

```
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=postgresql://user:pass@host:port/db
```

## Limitações e Soluções

### Cold Start (Sleep)
**Problema:** O serviço "dorme" após 15 minutos de inatividade. Primeira requisição leva 30-60s.

**Soluções:**
- **Ping automático:** Use um serviço como UptimeRobot para pingar a cada 5 minutos
- **Upgrade:** Plano pago ($7/mês) remove o sleep

### PostgreSQL 90 dias
**Problema:** PostgreSQL gratuito por 90 dias.

**Soluções:**
- **Backup:** Exporte dados antes dos 90 dias
- **Upgrade:** Plano PostgreSQL pago ($7/mês)
- **Alternativa:** Use Neon (PostgreSQL serverless com free tier generoso)

### Domínio Customizado
**Problema:** Sem domínio customizado no plano gratuito.

**Solução:**
- Use o domínio `.onrender.com`
- Upgrade para plano pago ($7/mês) para domínio customizado

## Monitoramento

### Logs
1. No dashboard do Render
2. Clique no Web Service
3. Clique em "Logs"
4. Veja logs em tempo real

### Métricas
1. No dashboard do Render
2. Clique no Web Service
3. Clique em "Metrics"
4. Veja CPU, memória, rede

## Backup Automático

Render faz backup automático do PostgreSQL, mas você pode configurar backup manual:

```python
# No seu código, adicione endpoint de backup
@app.route('/admin/backup')
def backup():
    # Script de backup
    return "Backup realizado"
```

## Troubleshooting

### Deploy falha
- Verifique os logs no Render
- Certifique-se que `requirements.txt` está correto
- Verifique que `startCommand` está correto

### Erro de conexão com banco
- Verifique que `DATABASE_URL` está configurada
- Verifique que o PostgreSQL está rodando
- Teste a conexão localmente

### Aplicação não inicia
- Verifique que `gunicorn` está instalado
- Verifique que o comando de start está correto
- Veja os logs de erro

## Alternativa: Neon + Render

Se quiser PostgreSQL gratuito por mais tempo:

1. **Neon** (PostgreSQL serverless):
   - Free tier generoso
   - Escalável
   - URL: https://neon.tech

2. **Render** (apenas web service):
   - Use Neon como banco externo
   - Configure `DATABASE_URL` do Neon no Render

## Próximos Passos

1. ✅ Preparar repositório
2. ✅ Criar conta no Render
3. ✅ Deploy web service
4. ✅ Criar PostgreSQL
5. ✅ Conectar banco
6. ✅ Testar aplicação
7. ✅ Configurar ping automático (UptimeRobot)
8. ✅ Monitorar logs

## Custo

**Plano Gratuito:**
- Web Service: $0 (750 horas/mês)
- PostgreSQL: $0 (90 dias, depois $7/mês)
- **Total:** $0 (primeiros 90 dias)

**Após 90 dias:**
- Web Service: $0
- PostgreSQL: $7/mês
- **Total:** $7/mês

## Suporte

- **Documentação Render:** https://render.com/docs
- **Comunidade:** https://community.render.com
- **Suporte:** support@render.com
