# Documentação Técnica Operacional - AriOne ERP

## Estrutura de Organização

A partir de agora, toda documentação técnica deve ser organizada nas subpastas a seguir.

## 📁 Estrutura de Diretórios

```
doc_tec_oper/
├── README.md                           # Este arquivo
├── 01_Integridade_Estrutural.md        # Padrões de código e estrutura
├── 02_Visao_Geral.md                   # Visão geral do sistema
├── 03_Fluxo_Financeiro.md              # Fluxo financeiro completo
├── 04_Regras_Fiscal.md                 # Regras fiscais brasileiras
├── 05_Integracoes_API.md               # Documentação de APIs
├── 06_Fluxo_Operacional.md             # Fluxos operacionais
│
├── 01_Desenvolvimento/                 # Documentação de desenvolvimento
│   ├── ESTABILIDADE_MASTER.md
│   ├── estrutura.md
│   └── regras_desenvolvimento.md
│
├── 02_Infraestrutura/                  # Infraestrutura e deploy
│   └── DEPLOY_PRODUCAO.md
│
├── 03_Design/                          # Design e identidade visual
│   ├── padrao_logo.md
│   └── sistema_cores.md
│
├── 04_Versoes/                         # Registro de versões
│   ├── V1.02.03.md
│   ├── v1.04.01.md
│   ├── v1.04.02.md
│   └── v1.04.03.md
│
├── 05_Mapeamentos/                     # Mapeamentos de dados
│   ├── Empresa.md
│   ├── Forempresa.md
│   ├── Investidores.md
│   └── Socios.md
│
├── 06_Integridade/                     # Padrões de integridade
│   ├── AriOne_Genesis.md
│   ├── PAA-DATA.md
│   ├── PAA-OPS.md
│   ├── PAAv1.md
│   ├── PAAv2.md
│   ├── cabecalho_mestre.md
│   ├── paa.md
│   └── padrao_ouro_arione.md
│
└── 07_UI_UX/                           # Interface e experiência do usuário
    └── PAA-UI.md
```

## 📋 Descrição das Subpastas

### 01_Desenvolvimento
Documentação relacionada ao desenvolvimento do sistema:
- Regras de desenvolvimento
- Estrutura de código
- Padrões de estabilidade

### 02_Infraestrutura
Documentação de infraestrutura e deploy:
- Configuração de servidores
- Deploy em produção
- Scripts de instalação

### 03_Design
Documentação de design e identidade visual:
- Padrão de logo
- Sistema de cores
- Diretrizes visuais

### 04_Versoes
Registro de versões do sistema:
- Changelog de versões
- Novidades por versão
- Correções e melhorias

### 05_Mapeamentos
Mapeamentos de dados e entidades:
- Estrutura de tabelas
- Relacionamentos
- Modelos de dados

### 06_Integridade
Padrões de integridade do sistema:
- PAA (Padrão AriOne)
- Cabeçalho mestre
- Regras de dados

### 07_UI_UX
Documentação de interface e experiência do usuário:
- Padrões de UI
- Componentes
- Diretrizes de UX

## 📝 Convenções de Nomenclatura

### Arquivos Principais (Raiz)
- Prefixo numérico: `01_Nome.md`, `02_Nome.md`
- Nome em snake_case
- Descrição clara e concisa

### Arquivos em Subpastas
- Nome em snake_case
- Sem prefixo numérico (exceto versões)
- Nome descritivo do conteúdo

## 🚀 Como Adicionar Nova Documentação

1. **Identifique a categoria correta** (subpasta apropriada)
2. **Crie o arquivo** com nome descritivo em snake_case
3. **Adicione conteúdo** seguindo os padrões existentes
4. **Atualize este README** se criar nova subpasta

## ⚠️ Regras

- **OBRIGATÓRIO:** Todo arquivo .md deve estar em `doc_tec_oper/`
- **OBRIGATÓRIO:** Usar subpasta apropriada
- **OBRIGATÓRIO:** Nomenclatura snake_case
- **RECOMENDADO:** Atualizar este README ao adicionar arquivos
- **PROIBIDO:** Criar arquivos .md fora de `doc_tec_oper/`

## 📞 Suporte

Para dúvidas sobre organização de documentação, consulte o documento `01_Integridade_Estrutural.md`.
