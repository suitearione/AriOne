# 02 - Visão Geral do Sistema

## Arquitetura do AriOne ERP

### Stack Tecnológica

**Backend:**
- Python 3.8+
- Flask (Framework Web)
- SQLAlchemy (ORM)
- SQLite (Banco de Dados)

**Frontend:**
- HTML5 + Jinja2
- JavaScript (ES6+)
- CSS3 (Custom)
- Bootstrap (Componentes base)

**Utilitários:**
- Gunicorn (Servidor de produção)
- Waitress (Servidor Windows)
- NSSM (Gerenciador de serviços Windows)
- Systemd (Gerenciador de serviços Linux)

## Módulos do Sistema

### 1. Cadastros
- **Catálogos:** Produtos, serviços, insumos, matéria-prima
- **Pessoas:** Clientes, fornecedores, funcionários
- **Financeiro:** Contas, bancos, formas de pagamento
- **Fiscal:** NCM, CEST, CFOP, CST

### 2. Operações
- **Vendas:** Orçamentos, pedidos, entregas
- **Compras:** Requisições, pedidos, recebimento
- **Produção:** Ordens de produção, ficha técnica
- **Estoque:** Movimentações, inventário, locais

### 3. Financeiro
- **Contas a Pagar:** Lançamentos, baixas, parcelas
- **Contas a Receber:** Faturamento, recebimentos
- **Fluxo de Caixa:** Entradas, saídas, saldo
- **Conciliação:** Bancária, cartões

### 4. Fiscal
- **NFe:** Emissão, cancelamento, inutilização
- **NFCe:** Vendas no balcão
- **NFSe:** Serviços
- **Sped:** Escrituração fiscal

### 5. Sistema
- **Usuários:** Gestão de acessos
- **Parâmetros:** Configurações globais
- **Backups:** Snapshot e restauração
- **Integrações:** APIs externas

## Fluxo de Trabalho Típico

### Venda de Produto

1. **Cadastro Prévio:**
   - Produto cadastrado com preço e estoque
   - Cliente cadastrado
   - Condição de pagamento definida

2. **Orçamento:**
   - Seleção de produtos
   - Aplicação de descontos
   - Geração de PDF

3. **Pedido de Venda:**
   - Confirmação do orçamento
   - Reserva de estoque
   - Geração de NFe

4. **Expedição:**
   - Separação de produtos
   - Conferência
   - Entrega

5. **Financeiro:**
   - Faturamento
   - Baixa de estoque
   - Contas a receber

### Produção

1. **Ficha Técnica:**
   - Definição de composição
   - Cálculo de custos
   - Margens

2. **Ordem de Produção:**
   - Criação da OP
   - Reserva de insumos
   - Acompanhamento

3. **Consumo:**
   - Baixa de insumos
   - Registro de horas
   - Controle de qualidade

4. **Finalização:**
   - Entrada de produto acabado
   - Atualização de custos
   - Disponibilização no estoque

## Integrações

### APIs Externas
- **SEFAZ:** Emissão de NFes
- **Correios:** Cálculo de frete
- **Gateways:** Pagamento online
- **Bancos:** Conciliação bancária

### Sistemas Legados
- **ERP Antigo:** Migração de dados
- **Contabilidade:** Exportação SPED
- **RH:** Integração funcional

## Segurança

### Níveis de Acesso
- **Administrador:** Acesso total
- **Gerente:** Acesso ao módulo
- **Operador:** Acesso limitado
- **Visualizador:** Apenas consulta

### Auditoria
- Log de todas as ações
- Rastreamento de alterações
- Relatórios de auditoria

## Performance

### Otimizações
- Índices em tabelas principais
- Cache de consultas frequentes
- Lazy loading de relacionamentos
- Compressão de backups

### Escalabilidade
- Arquitetura modular
- Separação de concerns
- API para integrações
- Suporte a multi-empresa

## Manutenção

### Backups
- Automáticos (agendados)
- Manuais (on-demand)
- Retenção configurável
- Armazenamento local e cloud

### Atualizações
- Versionamento semântico
- Migrações de banco
- Compatibilidade backward
- Rollback automático

## Monitoramento

### Métricas
- Uso de CPU/Memória
- Tempo de resposta
- Erros por módulo
- Volume de transações

### Alertas
- Falhas de serviço
- Estoque baixo
- Contas vencidas
- Integrações falhando

## Suporte

### Documentação
- Manual do usuário
- Documentação técnica
- Guia de instalação
- FAQ

### Canais
- Sistema de tickets
- Chat em tempo real
- E-mail
- Telefone
