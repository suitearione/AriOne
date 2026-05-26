# =============================================================================
# Arquivo  : PAA-UI.md
# Caminho  : templates/sistema/cards/developer/PAA-UI.md
# Função   : Protocolo de Interface AriOne (UI/UX Standards)
# Versão   : 2.0
# Data     : 2026-05-01
# =============================================================================

> [!IMPORTANT]
> **ESCOPO DESTE DOCUMENTO:**
> Este protocolo define EXCLUSIVAMENTE os padrões de interface, experiência do usuário,
> validação no frontend e componentes visuais do AriOne. Para padrões de dados e backend,
> consulte PAA-DATA. Para segurança e deploy, consulte PAA-OPS.

---

## ÍNDICE

1. [Camada de Validação Frontend](#1-camada-de-validação-frontend)
2. [Sistema de Navegação Contextual](#2-sistema-de-navegação-contextual)
3. [Design System - Cabeçalho Mestre](#3-design-system---cabeçalho-mestre)
4. [Matriz de Produtos e Variantes](#4-matriz-de-produtos-e-variantes)
5. [Arquitetura de Sub-Abas](#5-arquitetura-de-sub-abas)
6. [Acessibilidade (WCAG 2.1)](#6-acessibilidade-wcag-21)
7. [Responsividade e Mobile-First](#7-responsividade-e-mobile-first)

---

## 1. CAMADA DE VALIDAÇÃO FRONTEND

### 1.1 PRINCÍPIOS FUNDAMENTAIS

A validação frontend é a **primeira linha de defesa** do sistema, mas NUNCA a única.
Seu objetivo é fornecer feedback imediato ao usuário, melhorando a UX e reduzindo
requisições desnecessárias ao servidor.

**Regra de Ouro:** Toda validação frontend DEVE ter uma validação equivalente no backend
(vide PAA-DATA para detalhes).

---

### 1.2 EVENTOS DE VALIDAÇÃO

#### A. Validação em Tempo Real (Event: `blur`)

Dispara quando o usuário **sai** de um campo. Ideal para:
- Verificação de unicidade (SKU, CPF/CNPJ, Email)
- Formatação automática (CEP, telefone)
- Consultas a APIs externas (ViaCEP)

#### B. Validação Pré-Submit (Event: `submit` ou click em "Salvar")

Valida TODOS os campos obrigatórios antes de enviar ao servidor.

---

### 1.3 REGRAS DE VALIDAÇÃO OBRIGATÓRIAS

#### A. Campos de Texto

| Campo | Regra | Implementação |
|-------|-------|---------------|
| **Nome / Razão Social** | Title Case (primeira letra maiúscula) | `toTitleCase()` no `blur` |
| **Descrição de Produto** | Livre (preservar formatação original) | Sem transformação |
| **Email** | Minúsculas + Regex RFC 5322 | `toLowerCase()` + validação |
| **SKU / Código Interno** | UPPERCASE + Alfanumérico | `toUpperCase()` + `/^[A-Z0-9-_]+$/` |

---

### 1.4 MÁSCARAS DE ENTRADA

**Biblioteca recomendada:** IMask.js ou Vanilla Masker. Uso obrigatório para CPF, CNPJ, Telefone, CEP e Preços (R$).

---

### 1.5 FEEDBACK VISUAL DE VALIDAÇÃO

#### A. Estados de Campo
- `.input-success`: Borda verde + checkmark.
- `.input-error`: Borda vermelha + fundo de alerta.
- `.input-loading`: Spinner de processamento.

---

### 1.6 TOAST NOTIFICATIONS (arioneToast)

Função unificada para feedback ao usuário (`success`, `warning`, `error`, `info`).

---

### 1.7 PREVENÇÃO DE SUBMISSÃO DUPLICADA

Ao clicar em "Salvar", o botão deve ser desabilitado e exibir um spinner até a resposta do servidor.

---

### 1.8 DIRTY STATE (ALERTA DE SAÍDA)

Monitorar alterações e avisar o usuário se ele tentar fechar a tela com dados não salvos.

---

## 2. SISTEMA DE NAVEGAÇÃO CONTEXTUAL

### 2.1 ARQUITETURA DE COMPONENTES

Baseado nos **3 Pilares da Produtividade**:
1. **Info Tooltip** - Orientação (i).
2. **Field Lookup** - Seleção (Autocomplete).
3. **Quick Actions** - Atalhos (Lupa e Plus).

---

## 3. DESIGN SYSTEM - CABEÇALHO MESTRE

### 3.1 ANATOMIA DO HEADER COMPONENT
- Breadcrumbs para localização.
- Toolbar com botões icon-only.
- Dropdown "..." para ações secundárias (Clonar, WhatsApp, PDF).
- Herança Cromática dinâmica do card de origem.

---

## 4. MATRIZ DE PRODUTOS E VARIANTES

### 4.1 GERAÇÃO AUTOMÁTICA DE SKU
Padrão: `[REFERENCIA]-[COR]-[TAMANHO]`.

### 4.2 GALERIA DE FOTOS POR COR
Vínculo obrigatório entre as imagens e a variação de cor selecionada.

---

## 5. ARQUITETURA DE SUB-ABAS

### 5.1 ESTRUTURA VERTICAL
- Topo: Cabeçalho Mestre.
- Centro: Dados Principais e Itens.
- Rodapé: Navegação por Sub-Abas (Financeiro, Fiscal, Logística).

---

## 6. ACESSIBILIDADE (WCAG 2.1)

- Contraste mínimo de 4.5:1.
- Navegação completa por teclado.
- Uso de ARIA labels para botões icon-only.
- Focus visible obrigatório.

---

## 7. RESPONSIVIDADE E MOBILE-FIRST

- Touch Targets de no mínimo 44x44px.
- Tabelas responsivas (Modo Card em mobile).
- Breakpoints: 640px (Tablet), 1024px (Desktop).

---
**FIM DO PAA-UI v2.0**
