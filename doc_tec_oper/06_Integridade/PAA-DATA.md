# =============================================================================
# Arquivo  : PAA-DATA.md
# Função   : Protocolo de Arquitetura e Integridade de Dados AriOne
# Versão   : 2.0
# Data     : 2026-05-01
# =============================================================================

> [!IMPORTANT]
> **ESCOPO DESTE DOCUMENTO:**
> Este protocolo define os padrões obrigatórios para modelagem de banco de dados,
> persistência via ORM (SQLAlchemy) e integridade de registros. Nenhuma alteração
> de schema deve ser feita sem conformidade com estas regras.

---

## O QUE É?

O **PAA-DATA** é o guardião da **Verdade e Integridade** da informação. Sua missão é garantir que cada dado armazenado no AriOne seja preciso, seguro e rastreável. Ele estabelece as fundações técnicas para que os cálculos financeiros e a persistência de registros sejam imunes a falhas e inconsistências.

---

## ÍNDICE

1. [Nomenclatura e Estrutura](#1-nomenclatura-e-estrutura)
2. [Tipagem e Precisão](#2-tipagem-e-precisão)
3. [Relacionamentos e Integridade](#3-relacionamentos-e-integridade)
4. [Colunas de Auditoria Obrigatórias](#4-colunas-de-auditoria-obrigatórias)
5. [Padrões de Persistência (ORM)](#5-padrões-de-persistência-orm)
6. [Otimização e Indexação](#6-otimização-e-indexação)

---

## 1. NOMENCLATURA E ESTRUTURA

### 1.1 Tabelas
- **Sempre no Plural**: `usuarios`, `produtos`, `pedidos_vendas`.
- **Snake Case**: Tudo em minúsculo, separado por underscore.
- **Prefixos de Módulo**: Opcional para módulos isolados (ex: `financeiro_contas`).

### 1.2 Colunas
- **ID Master**: Toda tabela DEVE ter uma Primary Key chamada exatamente `id`.
- **Foreign Keys**: Padrão `[tabela_no_singular]_id`. Ex: `cliente_id`, `produto_id`.

---

## 2. TIPAGEM E PRECISÃO

### 2.1 Campos Monetários (Financeiro)
- **NUNCA** usar Float para dinheiro.
- **Sempre usar Numeric(10, 2)** ou Decimal para garantir precisão centesimal.

### 2.2 Strings e Textos
- **Varchar(255)**: Para nomes, descrições curtas e SKUs.
- **Text**: Para observações, logs ou conteúdos extensos.
- **Booleans**: Usar tipo Boolean nativo (True/False).

---

## 3. RELACIONAMENTOS E INTEGRIDADE

### 3.1 Regras de Deleção (On Delete)
- **RESTRICT**: Padrão para entidades mestre (Não deletar cliente se houver pedidos).
- **CASCADE**: Para itens dependentes (Se deletar o Pedido, deleta os Itens do Pedido).

### 3.2 Unicidade (Unique Constraints)
- SKUs, CPFs e CNPJs devem ter a restrição `unique=True` no banco de dados para prevenir duplicidade técnica.

---

## 4. COLUNAS DE AUDITORIA OBRIGATÓRIAS

Toda tabela de movimento ou cadastro deve conter:
- `criado_em`: DateTime (default=datetime.now).
- `atualizado_em`: DateTime (onupdate=datetime.now).
- `usuario_id`: FK para rastrear quem criou/alterou o registro.

---

## 5. PADRÕES DE PERSISTÊNCIA (ORM)

### 5.1 O Uso da Sessão
- Toda operação de escrita deve estar dentro de um bloco `try/except`.
- **Flush vs Commit**: Usar `.flush()` quando precisar do ID gerado antes de finalizar a transação completa.

### 5.2 Carregamento de Dados (Fetch Strategy)
- Usar `joinedload` ou `subqueryload` para evitar o erro de N+1 consultas em grids e relatórios.

---

## 6. OTIMIZAÇÃO E INDEXAÇÃO

- **Índices**: Criar índices (`index=True`) para colunas usadas em filtros frequentes (ex: `status`, `data_pedido`, `codigo_referencia`).
- **Soft Delete**: Se a regra de negócio exigir, usar coluna `ativo` (Boolean) em vez de deletar fisicamente o registro.

---
**FIM DO PAA-DATA v2.0**
