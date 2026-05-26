# Manual de Fluxos Operacionais - AriOne

Este documento define a lógica de interdependência entre os módulos de Produção, Compras, Vendas e Logística.

## 1. Fluxo de Produção (Oficinas e Interno)
O ciclo de produção deve garantir a rastreabilidade desde a matéria-prima até o produto acabado.

### 1.1. Envio para Oficinas (Costura/Pintura)
* **Gatilho:** Abertura de uma Ordem de Produção (OP).
* **Processo:**
    1. Registro da saída de Insumos/Matéria-Prima no módulo de Estoque.
    2. Geração de guia de remessa para a oficina (parceiro/fornecedor).
    3. Status da OP: "Em Produção - Oficina".
* **Retorno:**
    1. Entrada da mercadoria finalizada.
    2. Baixa na remessa da oficina.
    3. Atualização do custo final (Insumo + Mão de obra externa).

### 1.2. Produção Interna
* **Gatilho:** Abertura de OP para produção própria.
* **Processo:**
    1. Reserva de insumos no estoque (não baixa definitiva).
    2. Acompanhamento por etapas (Corte, Costura, Acabamento).
    3. Baixa definitiva de insumos ao finalizar.
    4. Entrada de produto acabado.
* **Custo:** Cálculo baseado na composição + horas de mão de obra.

## 2. Fluxo de Compras
* **Integração:**
    * Ao finalizar um pedido de compra, o sistema deve verificar o nível de estoque mínimo.
    * Integração direta com o **Financeiro (Contas a Pagar)** ao confirmar o recebimento da nota fiscal.
* **Etapas:**
    1. Requisição de compra (manual ou automática por estoque mínimo).
    2. Cotação com fornecedores.
    3. Pedido de compra.
    4. Recebimento da nota fiscal.
    5. Entrada no estoque.
    6. Geração de conta a pagar.

## 3. Fluxo de Vendas (Comercial, Financeiro e Logística)
O ciclo de vendas deve ser unificado para evitar duplicidade de dados.

### 3.1. Pipeline de Venda
* **Comercial:** Cadastro do Orçamento -> Conversão em Pedido -> Vinculação do Cliente.
* **Financeiro:** O pedido gera automaticamente uma previsão no **Contas a Receber**.
* **Logística (Expedição):**
    * Verificação de disponibilidade em Estoque (Mapa/Estocagem).
    * Geração de etiqueta de envio (Integração Correios/Transportadoras).
    * Atualização de status: "Aguardando Coleta" -> "Em Trânsito".

### 3.2. Venda Balcão (NFCe)
* **Processo:**
    1. Seleção de produtos.
    2. Pagamento imediato.
    3. Emissão de NFCe.
    4. Baixa de estoque.
    5. Entrada no caixa.

### 3.3. Venda E-commerce
* **Processo:**
    1. Pedido via API.
    2. Verificação de estoque.
    3. Reserva de estoque.
    4. Pagamento (gateway).
    5. Geração de pedido no sistema.
    6. Expedição.

## 4. Matriz de Integração (Cross-Module)
| Módulo | Dependência | Ação Automática |
| :--- | :--- | :--- |
| Produção | Estoque | Baixa de Insumos |
| Vendas | Financeiro | Geração de Contas a Receber |
| Compras | Financeiro | Geração de Contas a Pagar |
| Expedição | Vendas | Atualização de Rastreio |
| Estoque | Compras | Entrada de Mercadorias |
| Estoque | Vendas | Baixa de Mercadorias |
| Financeiro | Vendas | Recebimento de Contas |
| Financeiro | Compras | Pagamento de Contas |

## 5. Regras de Negócio

### 5.1. Bloqueios
* **Estoque Insuficiente:** Bloqueia venda se não houver estoque disponível.
* **Cliente Inadimplente:** Bloqueia novas vendas.
* **Fornecedor Inadimplente:** Bloqueia novas compras.
* **Limite de Crédito:** Bloqueia venda acima do limite.

### 5.2. Reservas
* **Orçamento:** Não reserva estoque.
* **Pedido:** Reserva estoque (configurável).
* **Produção:** Reserva insumos.
* **Expedição:** Baixa definitiva.

### 5.3. Cancelamentos
* **Orçamento:** Sem impacto financeiro/estoque.
* **Pedido:** Libera reserva de estoque, cancela contas a receber.
* **Produção:** Libera insumos, cancela OP.
* **Expedição:** Retorna ao estoque, atualiza rastreio.

## 6. Notificações Automáticas

### 6.1. Estoque
* **Estoque Mínimo:** Alerta para compras.
* **Estoque Zerado:** Alerta crítico.
* **Estoque Negativo:** Bloqueio de vendas.

### 6.2. Financeiro
* **Vencimento Próximo:** Alerta 3 dias antes.
* **Vencido:** Alerta diário.
* **Pagamento:** Confirmação ao cliente.

### 6.3. Vendas
* **Novo Pedido:** Notificação ao time comercial.
* **Conversão:** Alerta ao gerente.
* **Cancelamento:** Justificativa obrigatória.

### 6.4. Produção
* **OP Criada:** Notificação ao PCP.
* **Envio Oficina:** Alerta ao logística.
* **Retorno Oficina:** Notificação ao estoque.

## 7. Rastreabilidade

### 7.1. Produto
* **Lote:** Rastreio por lote de produção.
* **Série:** Rastreio por número de série.
* **Validade:** Rastreio por data de validade.

### 7.2. Operação
* **Usuário:** Quem realizou a ação.
* **Data/Hora:** Quando foi realizada.
* **IP:** De onde foi realizada.
* **Motivo:** Justificativa quando necessário.

## 8. Performance

### 8.1. Otimizações
* **Índices:** Em campos frequentemente consultados.
* **Cache:** De consultas frequentes.
* **Async:** Processamento em background.
* **Batch:** Operações em lote.

### 8.2. Monitoramento
* **Tempo de Resposta:** Por endpoint.
* **Erros:** Taxa de erro por módulo.
* **Volume:** Transações por período.
* **Recursos:** CPU, memória, disco.

---
*Este documento é a base para o desenvolvimento das rotas em `blueprints/operacoes.py`.*
