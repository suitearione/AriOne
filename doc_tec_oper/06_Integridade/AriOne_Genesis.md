# =============================================================================
# Projeto: AriOne System Architecture
# Documento: Seeding de Homologação: AriOne_Genesis
# Função: Planejamento de Povoamento de Dados para Testes (Standard Luxure)
# Data: 06/05/2026
# =============================================================================

# SEEDING de HOMOLOGAÇÃO

Este documento estabelece o protocolo de povoamento inicial do banco de dados AriOne. O objetivo é garantir que o sistema contenha dados de teste realistas em todos os módulos, respeitando as restrições de integridade e dependências estruturais.

---

## 🧬 Árvore Genealógica de Dependências

Para que o povoamento ocorra sem erros de chave estrangeira, a execução deve seguir rigorosamente a ordem abaixo:

### **Nível 0: Alicerces (Independência Total)**
> [!NOTE]
> Estes dados são a "gramática" do sistema. Sem eles, nada faz sentido.

- [ ] **Status de Workflow**: Definição de cores e ícones para cada etapa (Vendas, Compras, Produção).
- [ ] **Unidades de Medida**: UN, KG, MT, PC, CX.
- [ ] **Marcas**: Cadastro básico de fabricantes e grifes.
- [ ] **Cores e Tamanhos**: Paleta cromática e grades dimensionais.
- [ ] **Grades de Modelo**: Estruturação de grades P/M/G ou Numéricas.

### **Nível 1: Estrutura Organizacional**
- [ ] **Empresa (Matriz)**: Cadastro da entidade principal (AriOne Matriz).
- [ ] **Setores**: Definição de Almoxarifado, Comercial, Produção, Financeiro.
- [ ] **Cargos**: Definição de Vendedores, Costureiras, Administradores.

### **Nível 2: Pessoas e Entidades (Atores)**
- [ ] **Funcionários**: Cadastro de 3 colaboradores de teste (Vínculo com Cargo/Setor).
- [ ] **Clientes**: Cadastro de 3 clientes (PF/PJ) com dados de entrega e faturamento.
- [ ] **Fornecedores**: Cadastro de 3 fornecedores de insumos e matérias-primas.
- [ ] **Transportadoras**: Cadastro de 3 operadoras logísticas.

### **Nível 3: O Catálogo (Hardware e Software)**
- [ ] **Categorias e Subcategorias**: Hierarquia de tipos de produtos.
- [ ] **Insumos / Matéria-Prima**: Cadastro de tecidos, botões, aviamentos (Vínculo com Fornecedor).
- [ ] **Produtos (Base)**: Cadastro mestre de 3 produtos (Simples, Com Grade, Composto).

### **Nível 4: Engenharia e Preço**
- [ ] **Variações de Produto (SKUs)**: Geração de combinações de Cor x Tamanho.
- [ ] **Tabelas de Preços**: Configuração de Varejo e Atacado para os produtos de teste.
- [ ] **Fichas Técnicas**: Definição do consumo de insumos por produto.

### **Nível 5: Fluxo Vivo (Transacional)**
- [ ] **Orçamentos**: Geração de orçamentos de teste para validar o seletor de cores.
- [ ] **Ordens de Produção**: Geração de OPs de teste para validar a integração com estoque.

---

## 💎 Padrão de Cadastro "AriOne_Genesis"

Para cada formulário, utilizaremos o seguinte padrão de dados:

1.  **Nomenclatura**: 
    - `[Nome] 1 - Testes`
    - `[Nome] 2 - Testes`
    - `[Nome] 3 - Testes`
2.  **Integridade**: Preenchimento de **100% dos campos** (Endereço completo, Contatos, Fotos, Dados Fiscais).
3.  **Estética**: Uso de imagens de alta qualidade (via AI) para fotos de produtos e funcionários.

---

> [!IMPORTANT]
> Este planejamento serve como o "Caminho Crítico" para o script de automação de seeding. Qualquer nova tabela criada deve ser inserida na posição correta desta árvore.
