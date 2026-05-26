# Scripts AriOne

Este diretório contém scripts utilitários e de manutenção do sistema AriOne.

## Estrutura

```
scripts/
├── api/              # Scripts relacionados a APIs externas
├── diagnostico/      # Scripts de diagnóstico do sistema
├── manutencao/       # Scripts de manutenção e correções
├── sync/             # Scripts de sincronização de dados
├── teste/            # Scripts de teste
└── tray_manager.py   # Gerenciador de tray do sistema
```

## Descrição das Subpastas

### api/
Scripts relacionados a integrações com APIs externas:
- `api_routes.py` - Rotas API para integração com sistemas externos

### diagnostico/
Scripts para diagnóstico e análise do sistema:
- `diagnostico_dados.py` - Diagnóstico de dados
- `diagnostico_params.py` - Diagnóstico de parâmetros

### manutencao/
Scripts de manutenção e correções do banco de dados:
- `add_campos_empresa.py` - Adiciona campos de empresa
- `check_cols.py` - Verifica colunas do banco
- `delete_colors.py` - Remove cores duplicadas
- `fix_comercial_db.py` - Corrige banco comercial
- `fix_pix_column.py` - Corrige coluna PIX
- `fix_schema.py` - Corrige schema do banco
- `fix_versoes_db.py` - Corrige versões do banco
- `init_db.py` - Inicializa banco de dados
- `publicar.py` - Script de publicação
- `scratch_db_fix.py` - Correções rápidas do banco

### sync/
Scripts de sincronização de dados:
- `sync_db.py` - Sincroniza banco de dados
- `sync_finance.py` - Sincroniza dados financeiros

### teste/
Scripts de teste do sistema:
- `test_operacoes.py` - Testa operações do sistema

## Arquivos na Raiz (Devem ficar lá)

Os seguintes arquivos .py devem permanecer na raiz do projeto:

- **gunicorn.conf.py** - Configuração do Gunicorn para produção
- **main.py** - Script principal de inicialização
- **run.py** - Script de inicialização para desenvolvimento

## Como Usar

### Executar script de manutenção
```bash
python scripts/manutencao/init_db.py
```

### Executar diagnóstico
```bash
python scripts/diagnostico/diagnostico_dados.py
```

### Executar sincronização
```bash
python scripts/sync/sync_db.py
```

## Cuidados

- **Sempre faça backup** antes de executar scripts de manutenção
- **Teste em ambiente de desenvolvimento** antes de produção
- **Leia o código** antes de executar scripts desconhecidos
- **Verifique os imports** após mover arquivos
