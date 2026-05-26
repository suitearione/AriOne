# 04 - Regras Fiscais

## Visão Geral

Este documento define as regras fiscais do sistema AriOne ERP, conforme a legislação brasileira vigente.

## Classificação Fiscal

### NCM (Nomenclatura Comum do Mercosul)
- **Objetivo:** Classificação de produtos
- **Estrutura:** 8 dígitos + 2 dígitos de exceção
- **Uso:** Base para cálculo de impostos
- **Validação:** Tabela oficial da Receita Federal

### CEST (Código Especificador da Substituição Tributária)
- **Objetivo:** Identificação de produtos sujeitos a ICMS-ST
- **Estrutura:** 7 dígitos
- **Uso:** Cálculo de substituição tributária
- **Validação:** Tabela oficial da Receita Federal

### CFOP (Código Fiscal de Operações e Prestações)
- **Objetivo:** Classificação de operações fiscais
- **Estrutura:** 4 dígitos
- **Uso:** Determina natureza da operação
- **Categorias:**
  - 1.000 - Entradas
  - 2.000 - Saídas
  - 3.000 - Entradas/Saídas não estaduais
  - 5.000 - Saídas interestaduais
  - 6.000 - Entradas interestaduais

### CST (Código de Situação Tributária)
- **Objetivo:** Definição do regime tributário
- **Estrutura:** 3 dígitos
- **Uso:** Cálculo de ICMS, IPI, PIS, COFINS
- **Principais:**
  - 00 - Tributada integralmente
  - 10 - Tributada com redução de base
  - 20 - Com redução de base
  - 40 - Isenta
  - 41 - Não tributada
  - 50 - Suspensão
  - 51 - Diferimento
  - 60 - ICMS cobrado por substituição
  - 90 - Outras

## Regimes Tributários

### Simples Nacional
- **Alíquota:** Variável por faixa de faturamento
- **Cálculo:** DAS único
- **Vantagem:** Simplificação
- **Limitação:** Teto de faturamento

### Lucro Presumido
- **Alíquota:** Fixa por atividade
- **Cálculo:** Presunção de lucro
- **Vantagem:** Menor burocracia
- **Limitação:** Atividades específicas

### Lucro Real
- **Alíquota:** Sobre lucro efetivo
- **Cálculo:** Apuração real
- **Vantagem:** Precisão
- **Limitação:** Maior burocracia

## Impostos

### ICMS (Imposto sobre Circulação de Mercadorias e Serviços)
- **Base:** Valor da operação
- **Alíquota:** Variável por estado
- **Cálculo:** Valor × Alíquota
- **Substituição:** ICMS-ST
- **Crédito:** Entradas geram crédito

### IPI (Imposto sobre Produtos Industrializados)
- **Base:** Valor da operação
- **Alíquota:** Variável por NCM
- **Cálculo:** Valor × Alíquota
- **Crédito:** Entradas geram crédito
- **Isenção:** Produtos específicos

### PIS (Programa de Integração Social)
- **Base:** Faturamento total
- **Alíquota:** 0,65% (cumulativa) ou 1,65% (não-cumulativa)
- **Cálculo:** Valor × Alíquota
- **Crédito:** Apenas não-cumulativa

### COFINS (Contribuição para Financiamento da Seguridade Social)
- **Base:** Faturamento total
- **Alíquota:** 3% (cumulativa) ou 7,6% (não-cumulativa)
- **Cálculo:** Valor × Alíquota
- **Crédito:** Apenas não-cumulativa

### ISS (Imposto Sobre Serviços)
- **Base:** Valor do serviço
- **Alíquota:** Variável por município (2% a 5%)
- **Cálculo:** Valor × Alíquota
- **Retenção:** Conforme lei municipal

## Nota Fiscal Eletrônica (NFe)

### Emissão
- **Pré-requisitos:** Certificado digital, credenciamento SEFAZ
- **Validação:** Schema XML, assinatura digital
- **Envio:** Web service da SEFAZ
- **Protocolo:** Autorização de uso

### Cancelamento
- **Prazo:** Até 24 horas após autorização
- **Motivo:** Justificativa obrigatória
- **Processo:** Evento de cancelamento
- **Limite:** 7 dias após autorização

### Inutilização
- **Motivo:** Erro na numeração
- **Processo:** Solicitação à SEFAZ
- **Faixa:** Sequência de números
- **Validação:** Sem uso prévio

### Carta de Correção
- **Prazo:** Até 30 dias após autorização
- **Limites:** Não altera valores
- **Quantidade:** Múltiplas correções
- **Processo:** Evento de correção

## NFCe (Nota Fiscal do Consumidor Eletrônica)

### Diferenças para NFe
- **Ambiente:** Produção obrigatório
- **QRCODE:** Obrigatório
- **Contingência:** FS-DA ou offline
- **Impressão:** DANFE NFCe simplificado

### Emissão
- **Integração:** SAT ou ECF
- **Validação:** Em tempo real
- **Transmissão:** Imediata
- **Protocolo:** Autorização instantânea

### Contingência
- **FS-DA:** Formulário de segurança
- **Offline:** Emissão sem conexão
- **Prazo:** Transmissão em até 30 dias
- **Limite:** 50 notas por contingência

## NFSe (Nota Fiscal de Serviços Eletrônica)

### Padrões
- **Abrasf:** Padrão nacional
- **Ginfes:** Padrão municipal
- **DSF:** Padrão específico
- **ISSNet:** Padrão web service

### Emissão
- **Credenciamento:** Prefeitura municipal
- **Validação:** Schema específico
- **Envio:** Web service municipal
- **Protocolo:** Autorização de uso

### Cancelamento
- **Prazo:** Variável por município
- **Motivo:** Justificativa obrigatória
- **Processo:** Evento de cancelamento
- **Limite:** Conforme legislação local

## SPED (Sistema Público de Escrituração Digital)

### SPED Fiscal
- **Objetivo:** Escrituração fiscal
- **Periodicidade:** Mensal
- **Arquivos:** Registros 0000 a 9999
- **Validação:** PVA Receita Federal

### SPED Contábil
- **Objetivo:** Escrituração contábil
- **Periodicidade:** Mensal
- **Arquivos:** Plano de contas, lançamentos
- **Validação:** PVA Receita Federal

### SPED Pis/Cofins
- **Objetivo:** Escrituração de créditos
- **Periodicidade:** Mensal
- **Arquivos:** Registros A100 a D500
- **Validação:** PVA Receita Federal

### EFD-Reinf
- **Objetivo:** Escrituração de retenções
- **Periodicidade:** Mensal
- **Arquivos:** Eventos R-1000 a R-9000
- **Validação:** PVA Receita Federal

## Regras Específicas

### Substituição Tributária (ICMS-ST)
- **Cálculo:** (Valor + IPI + Frete + Outros) × (1 + MVA) × Alíquota Interna - Alíquota Interestadual
- **MVA:** Margem de Valor Agregado
- **Base:** Valor agregado
- **Crédito:** Não gera crédito

### Diferencial de Alíquota
- **Origem:** Interestadual para consumidor final
- **Cálculo:** (Alíquota Interna - Alíquota Interestadual) × Valor
- **FCP:** Fundo de Combate à Pobreza
- **Destaque:** Obrigatório na nota

### Frete
- **CIF:** Frete incluso no valor
- **FOB:** Frete à parte
- **Base:** ICMS sobre frete
- **Alíquota:** Mesma do produto

### Seguro
- **Inclusão:** No valor da nota
- **Base:** ICMS sobre seguro
- **Alíquota:** Mesma do produto
- **Obrigatório:** Para transporte interestadual

## Armazenamento Fiscal

### XML
- **Prazo:** 5 anos
- **Local:** Armazenamento seguro
- **Backup:** Redundante
- **Acesso:** Restrito

### PDF
- **Prazo:** 5 anos
- **Gerado:** Automaticamente
- **Assinatura:** Digital
- **Validade:** Legal

### Protocolos
- **Prazo:** 5 anos
- **Armazenamento:** Com XML
- **Validação:** Receita Federal
- **Consulta:** Chave de acesso

## Integrações

### SEFAZ
- **Homologação:** Ambiente de teste
- **Produção:** Ambiente real
- **Status:** Consulta em tempo real
- **Distribuição:** DTE

### Contabilidade
- **Exportação:** SPED
- **Importação:** Lançamentos
- **Conciliação:** Automática
- **Validação:** Contábil

### Receita Federal
- **Consulta:** CNPJ, NCM
- **Validação:** Certificados
- **Download:** XMLs
- **Status:** Situação cadastral

## Penalidades

### Multas
- **Atraso:** Multa por atraso
- **Erro:** Multa por erro
- **Omissão:** Multa por omissão
- **Sonegação:** Multa pesada + processo

### Juros
- **Cálculo:** SELIC acumulada
- **Período:** Do vencimento ao pagamento
- **Base:** Valor do imposto
- **Aplicação:** Automática

## Auditoria Fiscal

### Logs
- **Registro:** Todas as operações
- **Rastreamento:** Completo
- **Acesso:** Restrito
- **Backup:** Seguro

### Relatórios
- **Fiscais:** Por período
- **Por imposto:** Detalhado
- **Por estado:** Regional
- **Por produto:** Analítico

### Validação
- **Automática:** Antes do envio
- **Manual:** Após o envio
- **Revisão:** Periódica
- **Correção:** Imediata
