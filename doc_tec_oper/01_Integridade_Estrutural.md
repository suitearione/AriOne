# 01 - Integridade Estrutural

## Visão Geral

Este documento define as regras e padrões para manter a integridade estrutural do sistema AriOne ERP.

## Padrões de Código

### Python
- PEP 8 como guia de estilo
- Docstrings em todas as funções públicas
- Type hints onde aplicável
- Máximo de 100 caracteres por linha

### JavaScript
- ES6+ features
- Nomenclatura camelCase para variáveis e funções
- Nomenclatura PascalCase para classes
- Comentários JSDoc para funções complexas

### HTML/Jinja2
- Indentação consistente (4 espaços)
- Templates reutilizáveis via macros
- Separação clara entre lógica e apresentação

## Estrutura de Diretórios

```
AriONEDEV/
├── app/
│   ├── models/          # Modelos de dados
│   ├── routes/          # Rotas Flask
│   ├── utils/           # Utilitários e helpers
│   └── extensions.py    # Extensões Flask
├── templates/           # Templates Jinja2
│   ├── cadastros/
│   ├── operacoes/
│   └── sistema/
├── static/              # Arquivos estáticos
├── doc_tec_oper/        # Documentação técnica operacional
├── Doc_DEV/             # Documentação de desenvolvimento
└── instance/            # Dados da aplicação (banco, logs)
```

## Regras de Banco de Dados

### Nomenclatura de Tabelas
- Prefixo por módulo: `cat_` (catálogos), `op_` (operações), `fin_` (financeiro)
- Snake_case: `cat_produtos`, `op_vendas_pedidos`
- Plural para tabelas, singular para modelos

### Campos Obrigatórios
- `id` (Integer, Primary Key)
- `created_at` (DateTime, auto-gerado)
- `ativo` (Boolean, default True) para registros deletáveis

### Relacionamentos
- Foreign keys com `_id` sufixo: `produto_id`, `cliente_id`
- Backref com nome descritivo: `backref='itens'`

## Regras de API

### Endpoints
- RESTful onde aplicável
- Verbos HTTP corretos (GET, POST, PUT, DELETE)
- Respostas JSON padronizadas

### Formato de Resposta
```json
{
  "success": true/false,
  "data": {},
  "message": "Descrição",
  "error": "Detalhes do erro (se houver)"
}
```

## Validação de Dados

### Frontend
- Validação visual imediata
- Mensagens de erro claras
- Prevenção de envio de dados inválidos

### Backend
- Validação rigorosa antes de persistir
- Sanitização de inputs
- Tratamento de exceções

## Segurança

### Autenticação
- Flask-Login para sessões
- Hash de senhas com bcrypt
- Tokens para APIs externas

### Autorização
- Decoradores `@login_required`
- Verificação de permissões por módulo
- Logs de ações sensíveis

### Dados Sensíveis
- Nunca expor senhas em logs
- Criptografia de dados sensíveis
- Backup com criptografia

## Performance

### Otimizações
- Índices em campos frequentemente consultados
- Eager loading de relacionamentos
- Cache de consultas frequentes
- Lazy loading de imagens

### Monitoramento
- Logs de performance
- Alertas de erros
- Métricas de uso

## Manutenção

### Versionamento
- Git para controle de versão
- Branches por feature
- Pull requests para revisão

### Testes
- Testes unitários para funções críticas
- Testes de integração para fluxos principais
- Testes E2E para interfaces complexas

### Documentação
- Docstrings atualizadas
- Comentários em código complexo
- Documentação de uso para usuários finais

## Checklist de Integridade

Antes de commitar:
- [ ] Código segue PEP 8
- [ ] Docstrings completas
- [ ] Sem console.log ou print em produção
- [ ] Validações implementadas
- [ ] Logs apropriados
- [ ] Testes passando
- [ ] Documentação atualizada
