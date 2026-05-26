# REGRAS DE ESTABILIDADE MASTER - ARIONE DEV

Este arquivo define as estruturas, funções e campos que já foram VALIDADOS e não devem sofrer retrabalho ou alteração estrutural sem solicitação explícita.

## 1. ESTRUTURA DE ROTAS E BLUEPRINTS
- O prefixo do Blueprint de cadastros é `/cadastros`. Nunca remover.
- Rotas de JSON como `/cadastros/catalogos/grades/<id>/json` são vitais.

## 2. INTERFACE E ABAS (UI/UX)
- A estrutura de abas em `form_produto_abas.html` deve manter os IDs e `data-tab` originais (`estoque`, `composicao`, `precos`, etc).
- A visibilidade da aba de Composição é controlada pela função `toggleComposicaoTab(visible)`.

## 3. MOTOR JAVASCRIPT (produto_engine.js)
- **Funções Intocáveis**:
    - `calcMargens()`: Validada e funcional.
    - `initAutoSave()`: Validada e funcional.
    - `renderCoresChips()` / `renderAtributosChips()`: Validados.
- **Campos de Matriz**:
    - Os nomes dos inputs (`mat_sku_`, `mat_estoque_`, `mat_preco_`, `mat_override_`) são a base da persistência e não devem ser alterados.

## 4. CAMPOS DO BANCO DE DADOS (MODELS)
- `referencia`, `estoque_atual`, `estoque_minimo`, `preco_varejo`, `preco_custo` são campos padrão ouro.

---
*Assinado: Antigravity Master Agent*
