# PAA - Pilar da Informação (Audit Hub)
## Especificação: Cabeçalho Mestre "Padrão Ouro" AriOne

Este documento registra a estrutura oficial e obrigatória para todos os cabeçalhos de formulários do sistema AriOneDEV.

### 1. Identificação e Navegação (Esquerda)
- **Ícone de Retorno (<)**: Primeiro elemento, permite voltar à tela anterior ou fechar o modal.
- **Ícone do Módulo**: Em destaque com fundo translúcido (glassmorphism).
- **Título**: Fonte robusta (900), sombra leve.
- **Subtítulo**: Caminho de navegação (Breadcrumb) em caixa alta.
- **Pill de Status**: Identificador dinâmico de estado (Novo, Editando, etc.).

### 2. Ações Operacionais (Centro-Direita - Grupo Glass)
Apenas as ferramentas de busca e visualização ficam visíveis para manter o foco:
- **Ícone Pesquisa Rápida**: Aciona `toggleSearchZone()`.
- **Ícone Filtro**: Aciona `toggleFilterZone()`.
- **Ícone Ver Lista**: Aciona `showOnlyList()`.

### 3. Menu de Extensões (Dropdown "...")
Agrupa ações de saída e integração:
- **Importar XML/CSV**
- **Exportar Dados**
- **Enviar por E-mail**
- **Enviar por WhatsApp**
- **Imprimir Documento**

### 4. Comandos de Saída (Extrema Direita)
- **Ícone Novo (+)**: Reseta o formulário para uma nova inclusão.
- **Ícone Clonar (Cópia)**: Duplica o registro atual para agilizar novos cadastros.
- **Ícone Salvar (Disquete)**: Botão de ação principal em destaque (cor de tema).
- **Ícone Fechar (X)**: Botão de fechamento rápido.

### 5. Regras de Implementação
- O cabeçalho deve ser sempre `sticky` (fixo no topo).
- Deve herdar a `cor_tema` do módulo correspondente.
- Deve utilizar as funções globais do `arione-utils.js` por padrão.
