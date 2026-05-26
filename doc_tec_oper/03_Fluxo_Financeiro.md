# 03 - Fluxo Financeiro

## Visão Geral

Este documento descreve o fluxo financeiro do sistema AriOne ERP, desde o orçamento até a conciliação bancária.

## Ciclo Financeiro

### 1. Orçamento
- **Objetivo:** Previsão de receitas
- **Status:** Pendente
- **Impacto:** Apenas informativo, não afeta estoque nem financeiro

### 2. Pedido de Venda
- **Objetivo:** Formalização da venda
- **Status:** Confirmado
- **Impacto:**
  - Reserva de estoque (se configurado)
  - Geração de contas a receber
  - Emissão de NFe (se configurado)

### 3. Faturamento
- **Objetivo:** Geração do título financeiro
- **Status:** Faturado
- **Impacto:**
  - Criação de contas a receber
  - Baixa definitiva de estoque
  - Atualização de comissões

### 4. Recebimento
- **Objetivo:** Liquidação do título
- **Status:** Recebido
- **Impacto:**
  - Entrada no caixa
  - Atualização de saldo
  - Conciliação bancária

## Contas a Pagar

### Criação
- **Origem:** Pedido de compra, nota fiscal, manual
- **Dados:** Fornecedor, valor, vencimento, categoria
- **Classificação:** Fixa, variável, parcelada

### Baixa
- **Formas:** Dinheiro, boleto, transferência, cartão
- **Juros/Multa:** Calculados automaticamente
- **Desconto:** Abatimento manual ou automático

### Controle
- **Vencidos:** Alertas automáticos
- **A vencer:** Relatório de previsão
- **Pagos:** Histórico de pagamentos

## Contas a Receber

### Criação
- **Origem:** Pedido de venda, nota fiscal, manual
- **Dados:** Cliente, valor, vencimento, condição
- **Classificação:** Vista, prazo, parcelado

### Recebimento
- **Formas:** Dinheiro, boleto, transferência, cartão
- **Juros/Multa:** Aplicados em atraso
- **Desconto:** Concedido no pagamento

### Controle
- **Em atraso:** Cobrança automática
- **A receber:** Previsão de fluxo
- **Recebidos:** Histórico de entradas

## Fluxo de Caixa

### Entradas
- Vendas à vista
- Recebimentos de contas
- Outras receitas

### Saídas
- Pagamentos de contas
- Compras à vista
- Outras despesas

### Saldo
- **Atual:** Disponível imediato
- **Previsto:** Considerando a vencer
- **Projetado:** Considerando previsões

## Conciliação Bancária

### Processo
1. Importação de extrato bancário (OFX, CSV)
2. Comparação com lançamentos do sistema
3. Identificação de divergências
4. Ajustes manuais se necessário
5. Confirmação da conciliação

### Divergências Comuns
- Lançamentos não importados
- Valores diferentes
- Datas divergentes
- Lançamentos duplicados

## Formas de Pagamento

### Dinheiro
- **Registro:** Manual
- **Conciliação:** Direta
- **Taxas:** Zero

### Boleto
- **Registro:** Automático via banco
- **Conciliação:** Via retorno
- **Taxas:** Tarifa bancária

### Cartão de Crédito
- **Registro:** Via adquirente
- **Conciliação:** Via arquivo
- **Taxas:** MDR + antecipação

### Cartão de Débito
- **Registro:** Via adquirente
- **Conciliação:** Via arquivo
- **Taxas:** Tarifa fixa

### PIX
- **Registro:** Automático via banco
- **Conciliação:** Via retorno
- **Taxas:** Zero ou tarifa fixa

## Centros de Custo

### Classificação
- Por departamento
- Por projeto
- Por atividade

### Alocação
- Manual direta
- Rateio automático
- Percentual fixo

### Relatórios
- Por centro
- Comparativo
- Evolução

## Impostos Financeiros

### ISS
- **Base:** Serviços
- **Alíquota:** Variável por município
- **Cálculo:** Sobre valor bruto

### ICMS
- **Base:** Produtos
- **Alíquota:** Variável por estado
- **Cálculo:** Sobre valor bruto

### IPI
- **Base:** Produtos industrializados
- **Alíquota:** Variável por NCM
- **Cálculo:** Sobre valor bruto

### PIS/COFINS
- **Base:** Faturamento total
- **Alíquota:** Cumulativa ou não-cumulativa
- **Cálculo:** Sobre valor bruto

## Relatórios Financeiros

### Fluxo de Caixa
- Diário, semanal, mensal
- Por categoria
- Por centro de custo

### DRE (Demonstrativo de Resultado)
- Receitas
- Despesas
- Lucro/Prejuízo

### Balancete
- Saldos de contas
- Movimentações
- Comparativo

### Inadimplência
- Clientes em atraso
- Valor total
- Idade da dívida

## Integrações

### Bancos
- Importação de extratos
- Conciliação automática
- Pagamento de fornecedores

### Adquirentes
- Importação de vendas
- Recebimento de cartões
- Antecipações

### Contabilidade
- Exportação SPED
- Balancete mensal
- Lançamentos contábeis

## Regras de Negócio

### Bloqueios
- Cliente inadimplente: Bloqueio de novas vendas
- Fornecedor inadimplente: Bloqueio de compras
- Estoque negativo: Bloqueio de vendas

### Limites
- Limite de crédito por cliente
- Limite de pagamento por fornecedor
- Limite de saque por usuário

### Autorizações
- Descontos acima de X%: Gerente
- Cancelamento após faturamento: Diretor
- Estorno após recebimento: Financeiro

## Auditoria

### Logs
- Todas as movimentações financeiras
- Usuário responsável
- Data e hora
- IP de origem

### Rastreamento
- Origem do lançamento
- Alterações realizadas
- Histórico completo

### Segurança
- Criptografia de dados sensíveis
- Controle de acesso
- Backup diário
