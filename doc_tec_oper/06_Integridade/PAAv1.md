# =============================================================================
# Arquivo  : PAA.md
# Caminho  : Doc_DEV/Integridade/PAA.md
# Função   : Protocolo de Auditoria AriOne (HCM GOLDEN STANDARD)
# Versão   : 1.0 (Audit Ready)
# =============================================================================

> [!IMPORTANT]
> **MANUAL DO AUDITOR (INSTRUÇÃO AO AGENTE):**
> Ao receber a instrução "Agente, audite o formulário [X]", você deve:
> 1. Ler os itens de 1 a 9 deste protocolo.
> 2. Analisar o código-fonte do formulário [X] (HTML, JS e Backend).
> 3. Gerar um relatório apontando:
>    - ✅ **Conformidade**: O que está seguindo o padrão.
>    - ⚠️ **Vulnerabilidades**: O que está fora do padrão ou em risco.
>    - 🚀 **Sugestão de Correção**: O código exato para ajustar o item.

1. CAMADA DE VALIDAÇÃO (O "ANTES"):

Esta é a primeira linha de defesa do sistema. Antes de qualquer tentativa de salvar, o AriOne
valida os dados diretamente no frontend (JavaScript) e, em seguida, no backend (Flask/Python).

A. VALIDAÇÃO NO FRONTEND (Antes de enviar):
   - Implementação: Lógica JavaScript ativada no evento `blur` (ao sair do campo) e no clique do botão "Salvar".
   - Feedback: A função `arioneToast('mensagem', 'warning')` exibe alertas visuais sem interromper o fluxo.
   - Campos com erro recebem destaque visual em vermelho e uma mensagem contextual abaixo do input.

B. REGRAS DE VALIDAÇÃO OBRIGATÓRIAS (Em todos os módulos):
   - Campos obrigatórios: Não podem ser enviados em branco (ex: Nome, SKU, CNPJ/CPF).
   - Unicidade (Real-Time): SKU, CPF/CNPJ e Código Interno devem ser únicos. A verificação **deve** ocorrer via AJAX no evento `blur` chamando o endpoint `/check-duplicate`, sinalizando erro antes mesmo do salvamento.
   - Nomes e Descrições (MAIÚSCULAS): Conversão automática para caixa alta para garantir integridade em buscas e padrão profissional.
   - CPF: 11 dígitos numéricos. CNPJ: 14 dígitos. Ambos validados com máscara e dígito verificador.
   - CEP: 8 dígitos numéricos (máscara `00000-000`). Ao sair do campo (`blur`), dispara consulta
     automática à API ViaCEP e preenche Logradouro, Bairro, Cidade e UF automaticamente.
     Se o CEP for inválido ou não encontrado, exibe `arioneToast` de aviso e bloqueia o salvamento,
     pois um CEP errado compromete diretamente a Nota Fiscal, o Romaneio e a entrega.
   - BANCOS: Jamais campo de texto livre. O campo banco deve ser sempre vinculado à
     tabela oficial de bancos do Banco Central (código COMPE/ISPB).
     Regras obrigatórias:
       * O usuário seleciona o banco via `<select>` ou `<datalist>` com busca por nome ou código.
       * O sistema preenche automaticamente o nome oficial do banco ao selecionar o código.
       * Código inválido ou não encontrado na tabela = bloqueio do salvamento + `arioneToast`.
       * Impacto: Um banco incorreto invalida TED, boleto, chave PIX e dados de cobrança.
     Esta regra aplica-se a: Cadastro de Clientes, Fornecedores, Funcionários (salário),
     Contas Bancárias da Empresa e qualquer formulário com dados financeiros.

C. VALIDAÇÃO NO BACKEND (Segunda barreira):
   - O Flask valida novamente os dados recebidos via `request.form` ou `request.json`.
   - Em caso de erro, retorna `{"ok": false, "msg": "..."}` e o frontend exibe via `arioneToast`.

D. PADRÕES DE FORMATAÇÃO E UX (Aparência e Digitação):
   - **Nomes e Descrições (MAIÚSCULAS)**: Campos de Nome, Razão Social e Descrição de Produto devem ser convertidos automaticamente para MAIÚSCULAS no evento `input` ou `blur`. Isso garante integridade em buscas SQL e padronização em relatórios/etiquetas.
   - **E-mail (minúsculas)**: Todo campo de e-mail deve ser forçado para minúsculas.
   - **Auto-Select de Números**: Campos de Preço e Quantidade devem selecionar todo o texto ao receberem foco (`this.select()`), facilitando a substituição rápida.
   - **Máscaras Dinâmicas**: CPF, CNPJ, Telefone e CEP devem possuir máscaras de entrada que se aplicam enquanto o usuário digita.

E. VANTAGEM DO PADRÃO DUAL:
   - O frontend garante uma UX fluida e dados visualmente limpos.
   - O backend garante que nenhum dado inválido persiste mesmo se o JS for burlado.


2. Padrão de NAVEGAÇÃO CONTEXTUAL AriOne

Este padrão garante a gestão rápida e leve de dados sem quebra de fluxo operacional. Baseia-se nos **3 Pilares da Produtividade**, implementados via macros Jinja2 no arquivo `macros/componentes.html`.

Os 3 PILARES:

A. PILAR DA INFORMAÇÃO (O "O QUE É?"):
   - Função: Orientar o usuário sobre a regra de negócio do campo.
   - Implementação: `{{ comp.info_icon("Sua mensagem aqui") }}`.
   - Comportamento: Exibe um ícone (i) que, ao passar o mouse, revela um tooltip descritivo.

B. PILAR DA CONSULTA / ESCOLHA (O "ESCOLHA"):
   - Função: Seleção rápida e inteligente de registros existentes.
   - Implementação: Uso de `<select>` para listas fixas ou `<datalist>` para buscas dinâmicas.
   - Atalho: **ALT + ↓ (Seta para baixo)** ou **F4** (em campos específicos) para abrir a lista.

C. PILAR DA NAVEGAÇÃO / ATALHO (O "VÁ PARA"):
   - Função: Ponte direta para o formulário mestre ou criação de novos registros.
   - Implementação:
     * **Mestre (Lupa)**: `{{ comp.master_icon("modulo") }}` — Atalho: **SHIFT + F4**.
     * **Novo (+)**: `{{ comp.plus_icon("modulo") }}` — Atalho: **SHIFT + F2**.
   - Regras de Execução:
     1. **Isolamento (Iframe/Modal)**: Atalhos devem abrir o destino em Modal ou Iframe para nunca perder o progresso do formulário de origem.
     2. **Foco e Seleção Automática**: Ao retornar de um cadastro novo (Pilar Plus), o sistema deve selecionar automaticamente o registro criado no campo de origem e aplicar um breve "highlight" visual.
     3. **Retorno Seguro**: Se o usuário sair sem salvar no destino, o foco deve retornar exatamente ao campo que disparou a navegação.



3. CAMADA DE SCHEMA (O "BANCO"):

Esta é a fundação estrutural do sistema via SQLAlchemy. Um banco bem modelado impede a corrupção de dados e garante a longevidade do sistema.

A. PADRÕES DE NOMENCLATURA E ESTRUTURA:
   - Tabelas: `prefixo_nome_tabela` (ex: `cat_produtos`, `ope_vendas`).
   - Colunas: Sempre em `snake_case`. Chaves Estrangeiras: `tabela_referencia_id`.
   - **Campos HCM Obrigatórios**: `id`, `data_criacao`, `data_atualizacao`, `status` e `empresa_id` (Multi-tenancy).

B. INTEGRIDADE E SEGURANÇA HISTÓRICA:
   - **Soft Delete (Exclusão Lógica)**: É proibido deletar registros físicos (`hard delete`) em tabelas operacionais. Use a coluna `status` ('Ativo', 'Inativo', 'Excluido') para preservar o histórico de auditoria e relatórios fiscais.
   - **Moeda e Precisão**: Valores financeiros **devem** usar `Numeric(15,2)`. O uso de `Float` é proibido para evitar erros de arredondamento.
   - **Default Values**: Campos de texto não-obrigatórios devem usar `default=''` e `nullable=False` para evitar erros de `NoneType` no Python.

C. PERFORMANCE E ESCALABILIDADE:
   - **Indexação**: Colunas de busca frequente (`nome`, `sku`, `cpf_cnpj`) e todas as **Chaves Estrangeiras (FKs)** devem possuir `index=True` no SQLAlchemy.
   - **Migrations (Alembic)**: Toda e qualquer alteração na estrutura do banco deve ser feita via scripts de migração. Alterações manuais via SQL direto no banco são proibidas.

D. AUDITORIA AUTOMATIZADA:
   - O script `Doc_DEV/Integridade/auditoria_hcm.py` deve validar se as novas tabelas seguem este protocolo antes do deploy.



4. CAMADA DE TESTES DE PERSISTÊNCIA (CICLO DE VIDA DO DADO):

Este protocolo valida o sucesso da gravação física no banco de dados e a integridade da leitura posterior. É o teste do "Ciclo Completo" (End-to-End).

A. O PROTOCOLO "SAVE & VERIFY":
   1. **Input**: Preencher o formulário com dados de teste.
   2. **Save**: Disparar a função de salvamento (AJAX).
   3. **Verify (Frontend)**: O sistema deve exibir `arioneToast` de sucesso e atualizar a "Lista de Recentes" ou o Grid Principal.
   4. **Verify (Banco)**: Consultar o registro via SQL ou Terminal para garantir que todos os campos (incluindo campos ocultos como `empresa_id`) foram gravados corretamente.

B. REGRAS DE OURO DA PERSISTÊNCIA:
   - **Atomicidade (Tudo ou Nada)**: Em cadastros mestre-detalhe (ex: Pedidos + Itens), a gravação deve ser atômica. Se um item falhar, o pedido inteiro deve sofrer rollback. Jamais permitir pedidos sem itens no banco.
   - **Prevenção de Duplicidade (UI)**: Ao clicar em "Salvar", o botão deve ser desabilitado imediatamente e exibir um spinner de loading, impedindo cliques múltiplos.
   - **Dirty State (Alerta de Saída)**: O formulário deve monitorar alterações. Se o usuário tentar fechar a tela com dados modificados e não salvos, o sistema deve pedir confirmação.
   - **Controle de Concorrência**: O sistema deve validar (via timestamp ou token) se o registro foi alterado por outro usuário entre o momento da abertura e o salvamento. Em caso de conflito, deve bloquear o "Save" e sugerir o "Refresh" dos dados para evitar perda de trabalho.

C. INTEGRIDADE DE CÁLCULOS:
   - Em formulários operacionais, o valor total gravado no banco deve ser revalidado pelo backend (soma dos itens + frete - descontos). O sistema não deve confiar apenas no valor calculado pelo HTML/JS.

---

5. 🏷️ PADRÃO DE CABEÇALHO MÓDULO (PADRÃO HCM ARI-ONE):

Para especificações detalhadas de implementação do cabeçalho mestre (incluindo especificações visuais, funções JavaScript e exemplos de código), consulte: **docs/padronizacao_cabecalho_mestre.md**

Este documento contém:
- Especificações visuais e de design (cores, gradientes, tipografia)
- Arquitetura de ações e dropdown
- Padronização de largura (tamanhos do cabeçalho)
- 12 funções JavaScript padrão com exemplos de código
- Configuração do macro `cabecalho_mestre_arione`
- Checklist de padronização

6. 💎 PADRÃO DE CATÁLOGO & MATRIZ (EVOLUÇÃO OURO):

Este item define a inteligência por trás do Configurador de Produtos e da Matriz de Variantes.

A. GERAÇÃO INTELIGENTE DE SKU (IDENTIDADE):
   - **Padrão Obrigatório**: Se a geração automática estiver ativa, o SKU deve seguir rigorosamente o formato `[REFERÊNCIA]-[COR]-[TAMANHO]` (ex: `MOD-123-AZ-P`).
   - **Unicidade**: O sistema deve impedir o salvamento de SKUs duplicados, validando a combinação Cor+Tamanho antes da persistência.

B. PRECIFICAÇÃO E ATRIBUTOS (FLEXIBILIDADE):
   - **Herança de Preço**: Por padrão, as variantes herdam o preço do produto pai.
   - **Preço por Variação**: Se o parâmetro `PRECO_VARIAVEL` estiver ativo, a matriz deve permitir a edição individual de preços (ex: Tamanhos Especiais com valor diferenciado).
   - **Matriz de Atributos**: Atributos extras (ex: Mangas, Tecidos) devem ser selecionados via Pilar de Escolha (Item 2) diretamente na grade.

C. INTEGRIDADE VISUAL (AFINIDADE COR x FOTO):
   - **Vínculo por Cor**: As fotos da galeria devem ser associadas a uma Cor específica do catálogo.
   - **Fallback Inteligente**: Ao alternar cores na interface, o sistema deve exibir as fotos correspondentes. Caso não existam fotos para a cor selecionada, deve-se exibir a foto principal do produto.

D. TERMINOLOGIA OPERACIONAL:
   - O termo técnico "Grade" deve ser substituído na interface pelo termo amigável "**Tamanhos**" ou "**Variações**", conforme o contexto do parceiro.



7. 🏗️ ENGENHARIA DE PRODUTO RELACIONAL (PADRÃO 3 NÍVEIS):

O sistema utiliza uma estrutura relacional PLM (Product Lifecycle Management) para garantir precisão técnica e financeira.

A. ESTRUTURA DE DADOS (3 NÍVEIS):
   - **Nível 1 (Produto_Pai)**: Cadastro mestre (Identidade).
   - **Nível 2 (SKU_Filho)**: Cada variante de Cor/Tamanho é um registro único com estoque próprio.
   - **Nível 3 (Composicao_Item)**: Materiais e Insumos vinculados individualmente a cada SKU_Filho.

B. PROTOCOLO DE REPLICAÇÃO COM INDEPENDÊNCIA:
   - **Botão Replicar**: Ferramenta de produtividade para copiar a lista de materiais de uma variante para as demais.
   - **Ajuste Fino (Campo Livre)**: A replicação não bloqueia os registros. Após a cópia, todos os campos de consumo e quantidade devem permanecer **livres para edição individual**, permitindo que tamanhos diferentes tenham consumos diferentes.

C. CÁLCULO DE CUSTO AUTOMÁTICO:
   - O sistema deve somar o custo unitário de todos os itens do Nível 3 para gerar o **Custo de Engenharia** da variante em tempo real.
   - Este custo serve de base para a validação da margem de lucro no módulo operacional.

D. MATRIZ DE AJUSTE EM MASSA:
   - Interface em grade (Itens x Tamanhos) para edição rápida de consumo, garantindo que o usuário visualize a engenharia de toda a grade em uma única tela.


8. 🛡️ LÓGICA DE CLONAGEM MESTRE (SMART CLONE):

A função de clonagem permite a criação rápida de novos itens baseados em registros existentes, garantindo a integridade e evitando duplicidades acidentais.

A. COMPORTAMENTO TÉCNICO E SEGURANÇA:
   - **Reset de Identidade**: O sistema deve limpar o `ID` e tratar a ação como um novo `INSERT`.
   - **Status Inicial (Segurança)**: Todo registro clonado deve nascer com `status='Inativo'`. Isso obriga o usuário a revisar os dados antes de liberar o item para venda/operação.
   - **Limpeza de Dados Sensíveis (Zero-Out)**: Campos de "Estoque Atual", "Custo Médio" e "Data de Última Compra" devem ser zerados, pois são exclusivos do registro original.

B. UX E IDENTIFICAÇÃO:
   - **Prefixo de Cópia**: O campo "Descrição" ou "Nome" deve receber automaticamente o prefixo `CÓPIA - ` para facilitar a identificação visual imediata e evitar que o usuário passe despercebido.
   - **Preservação de Inteligência**: A clonagem de um Produto Pai deve levar consigo toda a sua **Engenharia/Composição (Item 7)**.

C. LÓGICA DE FOCO DINÂMICO:
   - **Prioridade de Identidade**: Após o disparo do Clone, o sistema deve aplicar o foco (`focus()`) automaticamente:
     1. No campo **SKU**, caso a geração seja manual.
     2. No campo **Referência / Nome**, caso o SKU seja gerado automaticamente (Item 6).
   - **Objetivo**: Garantir que a primeira ação do usuário seja definir a nova identidade do registro.

9. 💎 ARQUITETURA DE INTERFACE POR SUB-ABAS (MODERNA):

Este padrão substitui o layout lateral antigo, focando em uma interface limpa onde a complexidade é organizada em níveis de profundidade.

A. ESTRUTURA VERTICAL (FLUXO OPERACIONAL):
   1. **Topo (Torre de Comando)**: Uso obrigatório do `cabecalho_mestre_arione` com cor de herança.
   2. **Centro (Dados Mestres)**: Campos principais (Cliente/Data) e a Grade de Itens (Foco Total).
   3. **Rodapé (Sub-Navegação)**: Uso do sistema de abas para dados secundários (Financeiro, Logística, Fiscal, Observações, Anexos).

B. INTELIGÊNCIA DE NAVEGAÇÃO:
   - **Troca Instantânea (Zero Reload)**: A alternância entre abas deve ser feita via CSS/JS, garantindo que o usuário não sinta atraso no fluxo.
   - **Badges de Conteúdo**: Abas que possuem dados gravados (ex: uma Observação ou um arquivo em Anexos) devem exibir um indicador visual (badge/ponto) para informar o usuário sem necessidade de clique.
   - **Auto-Foco em Erros**: Se houver um erro de validação em um campo de uma aba inativa, o sistema deve alternar automaticamente para essa aba ao tentar salvar, destacando o erro.
   - **Responsividade (Mobile)**: Em telas pequenas, o menu de sub-abas deve colapsar para um **Dropdown de Navegação** ou uma **Barra com Scroll Horizontal**, mantendo a facilidade de toque.

C. TOTAIS E AÇÕES:
   - Os totais financeiros devem ser exibidos em uma barra discreta e elegante (Fixed ou Sticky), preferencialmente integrada ao topo ou rodapé, sem reduzir o espaço lateral dos campos de dados.



---
10. 🔄 PADRÃO DE OPERAÇÃO COMERCIAL DINÂMICA (PERFIS & BUSCA):

Este padrão estabelece a inteligência de segmentação de parceiros e a precisão técnica na busca de itens, garantindo que o sistema se adapte a diferentes modelos de negócio (B2C e B2B).

A. IDENTIFICAÇÃO DE PARCEIROS (PERFIL DE VENDA):
   - **Segmentação Obrigatória**: Formulários de Vendas/Pedidos devem possuir um seletor de "Perfil" (CONSUMIDOR / REVENDA) posicionado antes da identificação do cliente.
   - **Alternância de Datalist**: A escolha do perfil deve disparar a troca dinâmica da fonte de dados (`list` do input), garantindo que um revendedor não seja buscado na base de clientes comuns e vice-versa.
   - **Reset de Contexto**: Ao alternar o perfil, os campos de Identificação e Tipo (PF/PJ) devem ser limpos automaticamente para evitar vínculos incorretos.

B. IDENTIFICAÇÃO DE ATENDIMENTO (TIPO VENDEDOR):
   - **Hibridismo (Humano/Robô)**: Registro obrigatório da origem do atendimento.
   - **Lógica de Interface**:
     * **Humano**: Exibe `<select>` vinculado à tabela de Funcionários.
     * **Robô (IA)**: Oculta a lista de funcionários e exibe placeholder de status da IA ("Em desenvolvimento..."), preparando o campo para automações futuras.

C. BUSCA INTELIGENTE DE ITENS (HÍBRIDA & GRADE):
   - **Dual Search (Nome/SKU)**: O campo de busca de itens deve permitir a localização tanto pelo Nome (ordem alfabética) quanto pelo SKU (sequência exata).
   - **Prioridade de Variação (SKU_Filho)**: O sistema deve priorizar a busca por SKUs de variações (Nível 2). Se o código digitado corresponder a uma variação de grade (cor/tamanho), a descrição deve ser carregada com os atributos correspondentes.
   - **Fallback SKU Base**: Caso o código não corresponda a uma variação, o sistema deve buscar pelo SKU Base/Referência (Nível 1).

D. PADRÃO VISUAL DE CÓDIGOS (SKU):
   - **Largura Técnica**: Colunas de Código/SKU em grids operacionais devem possuir largura mínima de **250px** para visualização completa de códigos compostos.
   - **Tipografia de Precisão**: Uso obrigatório de fonte monoespaçada (`Roboto Mono` ou similar) e peso `700` para garantir legibilidade técnica imediata.

11. 🛡️ ARQUITETURA VISUAL PADRÃO OURO (OPÇÃO 2):

Este item define a evolução estética do AriOneDEV para o nível "Quiet Luxury", priorizando a Unidade de Marca e a Autoridade de Plataforma.

A. ASSINATURA DE MARCA (O TOPO):
   - **Cabeçalho Global**: Todos os módulos do sistema devem utilizar o **Roxo AriOne (#7A255F)** como cor predominante no cabeçalho mestre.
   - **Objetivo**: Criar uma "âncora visual" de confiança. O usuário, independente do módulo, sente que está dentro da plataforma integrada AriOne.

B. IDENTIDADE DE MÓDULO (OS ACENTOS):
   - A cor específica de cada módulo deixa de dominar o cabeçalho e passa a atuar nos detalhes internos do formulário (Acentos Cromáticos).
   - **Barra de Conexão (Premium Accent Bar)**: Uma linha sólida de **6px** de altura, na cor do módulo, posicionada imediatamente abaixo do cabeçalho roxo, fundindo-o ao corpo do formulário.
   - **Títulos de Cards**: Ícones e bordas esquerdas (`border-left: 4px`) dos cards internos devem assumir a cor do módulo.
   - **Ações Primárias**: Botões de conclusão (ex: "Finalizar", "Salvar") podem utilizar a cor do módulo para guiar o foco do usuário.

C. PALETA DE CORES MUNDIAL (VIVACIDADE ARI-ONE):
   As cores seguem a vibração original que define a identidade de cada módulo:
   - **Operações**: Ciano Elétrico (#03A9F4)
   - **Financeiro**: Verde Limão (#00E676)
   - **Gestão**: Lilás Elétrico (#CE93D8)
   - **Fiscal**: Amarelo Alaranjado (#FFB74D)
   - **Cadastros**: Cinza Prata (#BDBDBD)
   - **Patrimônio**: Bronze Prateado (#BCAAA4)
   - **Digital**: Azul Digital (#42A5F5)
   - **Relatórios**: Azul Indigo (#82B1FF)
   - **Sistema**: Cinza Técnico (#90A4AE)

D. LAYOUT INTEGRADO (CONTINUIDADE):
   - **Fim do Card Flutuante**: A base do cabeçalho mestre deve ser **RETA** (`border-radius: 12px 12px 0 0`).
   - **Efeito Visual**: O cabeçalho deve parecer "descer" e se integrar fisicamente ao corpo do formulário, eliminando espaços vazios e transmitindo a robustez de uma plataforma industrial sólida.

12. 🏛️ PADRÃO DE ESTRUTURA "FORMULÁRIO MESTRE ARIONE":

Este padrão define a arquitetura definitiva de navegação e layout para os formulários principais do sistema, substituindo o uso de modais por uma experiência de "Página Plena" (Full-Page).

A. ARQUITETURA DE NAVEGAÇÃO E FLUXO:
   - **Navegação Direta (Full-Page)**: Operações principais de CRUD (Cadastro, Edição, Orçamentos, Pedidos) devem ser carregadas via navegação de página real (`window.location.href`), abandonando o uso de Modais/Iframes para fluxos primários.
   - **Soberania do Sidebar**: O menu lateral (Sidebar) deve permanecer sempre visível e funcional à esquerda. O formulário deve ocupar 100% da área útil restante à direita (`arione-main-wrapper`).
   - **DNA de Continuidade**: Ao clicar em uma ação no Grid (ex: "Novo"), o sistema deve transitar para o formulário mantendo a unidade visual da plataforma.

B. COMPORTAMENTO E ERGONOMIA (STICKY & SCROLL):
   - **Cabeçalho Mestre Sticky**: O uso do `cabecalho_mestre_arione` deve ser obrigatório dentro de um container com `position: sticky`. As ações (Salvar, Novo, Clonar) devem estar sempre visíveis no topo, independentemente da rolagem da página.
   - **Scroll Natural do Navegador**: O formulário deve fluir verticalmente de forma contínua. É proibido o uso de travas de altura (`100vh`) ou containers de `overflow` interno que criem "páginas dentro da página". O scroll deve ser o nativo do navegador.
   - **Acessibilidade de Ações**: Botões de ação rápida e totais financeiros devem ser preferencialmente fixados (Sticky) para evitar que o usuário perca o contexto ao rolar listas longas de itens.

C. ESTÉTICA "QUIET LUXURY" (ESPAÇAMENTO):
   - **Área de Respiro**: O formulário deve manter um padding constante (Padrão: `24px`) em relação às bordas do sistema, garantindo que o conteúdo nunca "cole" no sidebar ou no rodapé.
   - **Layout Panorâmico**: Colunas críticas (como Descrição e SKU) devem ter larguras generosas para evitar truncamento de nomes compostos e variações de grade.

D. ESPECIFICAÇÕES TÉCNICAS "ULTRA-SLIM" (MEDIDAS):
   - **Cabeçalho Mestre (Padding)**: `7px 25px` (Compactação de Precision).
   - **Ícone de Identificação**: Container de `32px x 32px` com `border-radius: 9px`. Ícone interno: `14px`.
   - **Tipografia**: Título Principal: `15px` / Subtítulo: `10.5px` (Upper-spacing).
   - **Barra de Acento (Accent Bar)**: Altura fixa de `4px` com `border-radius: 0 0 12px 12px`.
   - **Espaçamento Inferior**: `margin-bottom: 12px` (Distância entre cabeçalho e formulário).

E. REGRAS DE ANCORAGEM E IMOBILIDADE (FIM DA LAGARTIXA):
   - **Zero Padding de Página**: O formulário deve forçar `.arione-page { padding-top: 0 !important; }` para garantir que o cabeçalho "beije" o topo do sistema.
   - **Sticky Puro**: Uso de `position: sticky; top: 0; z-index: 2000; background: #f4f6f9;`.
   - **Imobilidade**: É obrigatório o uso de `transition: none !important;` no container sticky para evitar saltos ou micro-movimentos durante o scroll.
   - **Blindagem de Fundo**: O container deve ter fundo 100% sólido e opaco, cobrindo toda a largura útil para evitar vazamento de conteúdo por trás.

13. 💎 CONSTITUIÇÃO DO CORPO DE FORMULÁRIO "COMPACTO PREMIUM":

Este padrão define a densidade de informação e a estética de alta precisão para o corpo dos formulários AriOne, priorizando a visibilidade de dados e a elegância.

A. TIPOGRAFIA E DENSIDADE DE DADOS:
   - **Dados e Inputs**: Tamanho fixo de `12px`. Fornece nitidez técnica sem ocupar espaço excessivo.
   - **Rótulos (Labels)**: Tamanho de `10px`, Peso `700` (Bold), Uppercase. Devem atuar como guias discretos.
   - **Títulos de Cards/Seções**: Tamanho de `13px`, Peso `700`.
   - **Tabelas de Itens**: Cabeçalhos (`10px` Bold) / Dados (`12px`).

B. ARQUITETURA DE ESPAÇAMENTO (PRECISION GAPS):
   - **Gaps de Linha (Rows)**: `10px` de distância entre colunas e `10px` entre linhas.
   - **Paddings de Input**: `7px 12px`.
   - **Respiro de Card**: Padding interno de `15px 18px`.
   - **Distância entre Cards**: `margin-bottom: 12px`.

C. RESUMO FINANCEIRO (KPIs DE TOTAIS):
   - **Valores de KPI**: Tamanho de `15px`, Peso `800`.
   - **Valor Líquido Final (Destaque)**: Tamanho de `26px`, Peso `900`, Cor de Acento do Módulo.
   - **Estrutura de Rodapé**: Padding de `15px 24px` com gap de `24px` entre os blocos de totais.

D. REGRAS DE INTEGRIDADE VISUAL:
   - **Fim do Vazio**: Todos os campos devem ser alinhados para evitar espaços vazios desnecessários, usando o sistema de `flex` (`fp-flex-1`, `fp-flex-2`) para distribuir o peso visual de forma inteligente.

---
14. 🏦 GESTÃO FINANCEIRA E PATRIMONIAL (GOLDEN STANDARD):

O módulo financeiro do AriOne segue uma arquitetura que separa **Patrimônio** (O que a empresa É) de **Resultado** (O que a empresa GERA), garantindo uma visão real da saúde do negócio.

A. HIERARQUIA DO PLANO DE CONTAS (MÁSCARA X.X.XXX):
   - **Grupo 1 (ATIVO)**: Bens, direitos e disponibilidades.
   - **Grupo 2 (PASSIVO)**: Obrigações e capital próprio.
   - **Grupo 3 (RECEITAS)**: Entradas por vendas ou serviços.
   - **Grupo 4 (CUSTOS/DESPESAS)**: Saídas e ajustes de resultado.
   - **Regra de Unicidade**: Cada conta analítica deve ser única por empresa e seguir rigorosamente a máscara de 3 níveis.

B. AUTOMAÇÃO DE DEPRECIAÇÃO (INTELIGÊNCIA PATRIMONIAL):
   - **Regime de Competência**: O AriOne automatiza a despesa de depreciação mensal para evitar distorções no lucro (DRE) em meses de grandes aquisições.
   - **Fluxo de Automação**:
     1. O Ativo é cadastrado (Grupo 1.4) com Valor de Aquisição e Vida Útil.
     2. O motor gera um **Lançamento de Ajuste** (Débito em 4.2.050 e Crédito Redutor no Ativo).
     3. O valor contábil é recalculado em tempo real: `Vlr. Aquisição - Depr. Acumulada`.
   - **Proteção de Valor**: O sistema bloqueia depreciações que ultrapassem o **Valor Residual** definido para o bem.

C. CONCILIAÇÃO E LANÇAMENTOS:
   - Todo lançamento financeiro (Receita/Despesa) deve estar obrigatoriamente vinculado a uma **Conta Analítica** e, opcionalmente, a um **Centro de Custo**.
   - **Status de Liquidação**: Lançamentos podem nascer como `PENDENTE` (Provisão) ou `PAGO` (Liquidação imediata).

---
15. 💎 SELO DE ENGENHARIA ARIONE (ASSINATURA DE MARCA):

Como parte da evolução para o nível "Quiet Luxury", todo formulário ou módulo mestre deve portar a assinatura oficial do AriOne, funcionando como um selo de autenticidade e autoridade técnica.

A. POSICIONAMENTO E RESPIRO:
   - O selo deve ser posicionado sempre ao final do conteúdo principal da página.
   - **Padding Superior**: Uso obrigatório de `margin-top: 80px` para garantir que a assinatura não dispute atenção com os dados operacionais.
   - **Linha de Divisão**: Uma borda superior sutil (`1px solid rgba(0,0,0,0.06)`) deve separar o selo do restante do formulário.

B. ANATOMIA DA MACRO `selo_arione()`:
   - **Copyright**: Exibição do ano atual e o nome "AriOne Operational Suite".
   - **Tipografia**: Uso da fonte `Outfit` com `letter-spacing: 1.5px` e `uppercase`.
   - **Versão (Versioning)**: Exibição clara da versão do sistema (ex: `v1.05.03 DEV`), onde o sufixo de ambiente (DEV/PROD) deve possuir cor de destaque.

C. FILOSOFIA DE DESIGN:
   - O selo não é apenas um rodapé; é um elemento de confiança. Ele assegura ao usuário que o formulário que ele está preenchendo segue os padrões globais de integridade e segurança do ecossistema AriOne.

---
**FIM DO PROTOCOLO PAA (HCM GOLDEN STANDARD)**




