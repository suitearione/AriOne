# 05 - Integrações API

## Visão Geral

Este documento descreve as integrações de API do sistema AriOne ERP, incluindo endpoints internos e externos.

## Arquitetura de Integração

### Padrão REST
- **Protocolo:** HTTP/HTTPS
- **Formato:** JSON
- **Autenticação:** Bearer Token / API Key
- **Versionamento:** /api/v1/

### Padrão de Resposta
```json
{
  "success": true/false,
  "data": {},
  "message": "Descrição",
  "error": "Detalhes do erro (se houver)",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## APIs Internas

### Autenticação

#### Login
- **Endpoint:** POST /api/v1/auth/login
- **Request:**
  ```json
  {
    "email": "usuario@empresa.com",
    "password": "senha"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "token": "jwt_token",
      "user": {
        "id": 1,
        "nome": "Usuário",
        "email": "usuario@empresa.com"
      }
    }
  }
  ```

#### Logout
- **Endpoint:** POST /api/v1/auth/logout
- **Headers:** Authorization: Bearer {token}
- **Response:**
  ```json
  {
    "success": true,
    "message": "Logout realizado com sucesso"
  }
  ```

### Produtos

#### Listar Produtos
- **Endpoint:** GET /api/v1/produtos
- **Query Params:** page, limit, busca, categoria
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "produtos": [],
      "total": 100,
      "page": 1,
      "pages": 10
    }
  }
  ```

#### Criar Produto
- **Endpoint:** POST /api/v1/produtos
- **Request:**
  ```json
  {
    "descricao": "Produto Exemplo",
    "preco_varejo": 100.00,
    "estoque_atual": 50,
    "categoria_id": 1
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "id": 123,
      "descricao": "Produto Exemplo",
      "preco_varejo": 100.00,
      "estoque_atual": 50
    }
  }
  ```

#### Atualizar Produto
- **Endpoint:** PUT /api/v1/produtos/{id}
- **Request:** (mesmo que criar)
- **Response:** (mesmo que criar)

#### Deletar Produto
- **Endpoint:** DELETE /api/v1/produtos/{id}
- **Response:**
  ```json
  {
    "success": true,
    "message": "Produto deletado com sucesso"
  }
  ```

### Vendas

#### Criar Pedido
- **Endpoint:** POST /api/v1/vendas/pedidos
- **Request:**
  ```json
  {
    "cliente_id": 1,
    "itens": [
      {
        "produto_id": 123,
        "quantidade": 2,
        "preco_unitario": 100.00
      }
    ],
    "forma_pagamento_id": 1,
    "observacao": "Observação"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "pedido_id": 456,
      "total": 200.00,
      "status": "CONFIRMADO"
    }
  }
  ```

#### Consultar Pedido
- **Endpoint:** GET /api/v1/vendas/pedidos/{id}
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "id": 456,
      "cliente": {},
      "itens": [],
      "total": 200.00,
      "status": "CONFIRMADO"
    }
  }
  ```

### Estoque

#### Movimentação
- **Endpoint:** POST /api/v1/estoque/movimentacao
- **Request:**
  ```json
  {
    "produto_id": 123,
    "quantidade": 10,
    "tipo": "ENTRADA",
    "local_id": 1,
    "documento_origem": "NF-123"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "movimentacao_id": 789,
      "saldo_atual": 60
    }
  }
  ```

#### Consultar Saldo
- **Endpoint:** GET /api/v1/estoque/saldo/{produto_id}
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "produto_id": 123,
      "saldo_fisico": 50,
      "saldo_disponivel": 45,
      "saldo_reservado": 5
    }
  }
  ```

### Financeiro

#### Criar Conta a Pagar
- **Endpoint:** POST /api/v1/financeiro/contas-pagar
- **Request:**
  ```json
  {
    "fornecedor_id": 1,
    "valor": 1000.00,
    "vencimento": "2024-01-31",
    "categoria_id": 1
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "conta_id": 321,
      "valor": 1000.00,
      "vencimento": "2024-01-31",
      "status": "PENDENTE"
    }
  }
  ```

#### Baixar Conta
- **Endpoint:** POST /api/v1/financeiro/contas-pagar/{id}/baixar
- **Request:**
  ```json
  {
    "data_pagamento": "2024-01-31",
    "valor_pago": 1000.00,
    "forma_pagamento_id": 1
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Conta baixada com sucesso"
  }
  ```

## APIs Externas

### SEFAZ (Nota Fiscal Eletrônica)

#### Status Serviço
- **Endpoint:** GET /api/v1/nfe/status
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "status": "VERDE",
      "motivo": "Autorizado"
    }
  }
  ```

#### Enviar NFe
- **Endpoint:** POST /api/v1/nfe/enviar
- **Request:**
  ```json
  {
    "pedido_id": 456,
    "tipo": "SAIDA",
    "natureza": "VENDA"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "chave_acesso": "431404...",
      "protocolo": "431400000...",
      "status": "AUTORIZADO"
    }
  }
  ```

#### Consultar NFe
- **Endpoint:** GET /api/v1/nfe/consultar/{chave}
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "chave_acesso": "431404...",
      "status": "AUTORIZADO",
      "protocolo": "431400000...",
      "xml": "base64_encoded_xml"
    }
  }
  ```

#### Cancelar NFe
- **Endpoint:** POST /api/v1/nfe/cancelar
- **Request:**
  ```json
  {
    "chave_acesso": "431404...",
    "motivo": "Erro na emissão",
    "protocolo": "431400000..."
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "protocolo_cancelamento": "431400000...",
      "status": "CANCELADO"
    }
  }
  ```

### Correios (Cálculo de Frete)

#### Calcular Frete
- **Endpoint:** POST /api/v1/frete/calcular
- **Request:**
  ```json
  {
    "cep_origem": "80000000",
    "cep_destino": "01310000",
    "peso": 1.5,
    "valor_declarado": 100.00,
    "servico": "SEDEX"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "valor": 25.50,
      "prazo": 3,
      "servico": "SEDEX"
    }
  }
  ```

### Gateways de Pagamento

#### Criar Transação
- **Endpoint:** POST /api/v1/pagamento/transacao
- **Request:**
  ```json
  {
    "pedido_id": 456,
    "valor": 200.00,
    "metodo": "CREDITO",
    "parcelas": 3,
    "cartao": {
      "numero": "4111111111111111",
      "validade": "12/25",
      "cvv": "123",
      "titular": "NOME TITULAR"
    }
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "transacao_id": "tran_123",
      "status": "APROVADO",
      "nsu": "123456"
    }
  }
  ```

#### Consultar Transação
- **Endpoint:** GET /api/v1/pagamento/transacao/{id}
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "transacao_id": "tran_123",
      "status": "APROVADO",
      "valor": 200.00,
      "data_aprovacao": "2024-01-01T00:00:00Z"
    }
  }
  ```

### Bancos (Conciliação)

#### Importar Extrato
- **Endpoint:** POST /api/v1/banco/extrato
- **Request:**
  ```json
  {
    "banco_id": 1,
    "arquivo": "base64_encoded_ofx",
    "formato": "OFX"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "importados": 50,
      "conciliados": 45,
      "divergentes": 5
    }
  }
  ```

#### Conciliar Lançamento
- **Endpoint:** POST /api/v1/banco/conciliar
- **Request:**
  ```json
  {
    "extrato_id": 123,
    "lancamento_id": 456
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Lançamento conciliado com sucesso"
  }
  ```

## Webhooks

### Configuração
- **Endpoint:** POST /api/v1/webhooks/configurar
- **Request:**
  ```json
  {
    "evento": "PEDIDO_CRIADO",
    "url": "https://seu-sistema.com/webhook",
    "headers": {
      "Authorization": "Bearer seu_token"
    }
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "webhook_id": 789,
      "evento": "PEDIDO_CRIADO",
      "url": "https://seu-sistema.com/webhook"
    }
  }
  ```

### Eventos Disponíveis
- `PEDIDO_CRIADO` - Novo pedido criado
- `PEDIDO_CONFIRMADO` - Pedido confirmado
- `PEDIDO_CANCELADO` - Pedido cancelado
- `CONTA_PAGAR_CRIADA` - Nova conta a pagar
- `CONTA_PAGAR_BAIXADA` - Conta baixada
- `CONTA_RECEBER_CRIADA` - Nova conta a receber
- `CONTA_RECEBER_RECEBIDA` - Conta recebida
- `ESTOQUE_BAIXO` - Estoque abaixo do mínimo
- `NFE_AUTORIZADA` - NFe autorizada
- `NFE_CANCELADA` - NFe cancelada

## Segurança

### Autenticação
- **Bearer Token:** JWT com expiração
- **API Key:** Chave estática para integrações
- **OAuth 2.0:** Para integrações complexas

### Rate Limiting
- **Padrão:** 100 requisições/minuto
- **Premium:** 1000 requisições/minuto
- **Excedido:** HTTP 429

### IP Whitelist
- **Configuração:** Por API Key
- **Validação:** A cada requisição
- **Bloqueio:** Automático

### Criptografia
- **HTTPS:** Obrigatório em produção
- **Dados Sensíveis:** Criptografados
- **Logs:** Sem dados sensíveis

## Erros

### Códigos de Erro
- `400` - Bad Request (parâmetros inválidos)
- `401` - Unauthorized (não autenticado)
- `403` - Forbidden (sem permissão)
- `404` - Not Found (recurso não existe)
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error (erro interno)
- `503` - Service Unavailable (manutenção)

### Formato de Erro
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Parâmetros inválidos",
    "details": [
      {
        "field": "email",
        "message": "Email inválido"
      }
    ]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Testes

### Ambiente de Testes
- **URL:** https://teste.arione.com/api/v1
- **Autenticação:** Token de teste
- **Dados:** Base de dados de teste

### Collection Postman
- **Disponível:** Em /docs/api/
- **Atualização:** Mensal
- **Variáveis:** Ambiente configurável

## Documentação

### Swagger/OpenAPI
- **URL:** /api/docs
- **Formato:** OpenAPI 3.0
- **Atualização:** Automática

### Exemplos
- **Linguagens:** Python, JavaScript, PHP
- **SDKs:** Disponíveis sob solicitação
- **Suporte:** Via ticket

## Monitoramento

### Logs
- **Acesso:** Todos os endpoints
- **Erro:** Detalhado
- **Performance:** Tempo de resposta
- **Retenção:** 30 dias

### Métricas
- **Requisições:** Por endpoint
- **Erros:** Por tipo
- **Latência:** P50, P95, P99
- **Uptime:** 99.9%

### Alertas
- **Erro:** Taxa > 5%
- **Latência:** P95 > 1s
- **Disponibilidade:** < 99%
- **Segurança:** Tentativas inválidas

## Suporte

### Canais
- **Email:** api@arione.com
- **Slack:** #api-support
- **Ticket:** Via sistema

### SLA
- **Crítico:** 1 hora
- **Alto:** 4 horas
- **Médio:** 8 horas
- **Baixo:** 24 horas

### Changelog
- **Versão:** Semântica
- **Atualização:** Semanal
- **Notificação:** Email
- **Deprecação:** 30 dias de aviso
