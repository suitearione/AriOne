# =============================================================================
# Arquivo  : PAA-OPS.md
# Função   : Protocolo de Segurança, Deploy e Infraestrutura AriOne
# Versão   : 2.0
# Data     : 2026-05-01
# =============================================================================

> [!IMPORTANT]
> **ESCOPO DESTE DOCUMENTO:**
> Este protocolo define as diretrizes de sobrevivência do sistema AriOne.
> Cobre a segurança do servidor, a integridade dos segredos de ambiente
> e a estratégia de recuperação de desastres (Backup).

---

## O QUE É?

O **PAA-OPS** é o guardião da **Continuidade e Segurança** do negócio. Sua missão é garantir que o sistema AriOne esteja sempre online, protegido contra ameaças e preparado para recuperação imediata em caso de falhas. Ele define os protocolos de "combate" para deploy, backup e estabilidade de infraestrutura.

---

## ÍNDICE

1. [Segurança e Segredos de Ambiente](#1-segurança-e-segredos-de-ambiente)
2. [Ciclo de Vida do Código (Deploy)](#2-ciclo-de-vida-do-código-deploy)
3. [Estratégia de Backup e Recuperação](#3-estratégia-de-backup-e-recuperação)
4. [Monitoramento e Logs](#4-monitoramento-e-logs)
5. [Configuração de Rede e Portas](#5-configuração-de-rede-e-portas)

---

## 1. SEGURANÇA E SEGREDOS DE AMBIENTE

### 1.1 O Arquivo .env
- **PROIBIDO**: Versionar o arquivo `.env` no Git.
- **CONTEÚDO**: Deve conter chaves de API, senhas de banco e a `SECRET_KEY` do Flask.
- **PROTEÇÃO**: Apenas o administrador Master tem acesso físico ao `.env` no servidor.

### 1.2 Criptografia
- Todas as senhas de usuários devem ser armazenadas usando hash `scrypt` ou `pbkdf2:sha256`.

---

## 2. CICLO DE VIDA DO CÓDIGO (DEPLOY)

### 2.1 Fluxo de Publicação
1.  **Desenvolvimento**: Testes locais via `python run.py`.
2.  **Staging**: Teste em pasta paralela ou servidor de homologação.
3.  **Produção**: Atualização via script de publicação (ex: `publicar.py`) para evitar perda de arquivos.

### 2.2 Hotfixes
- Correções urgentes devem ser documentadas no log de versões antes do deploy.

---

## 3. ESTRATÉGIA DE BACKUP E RECUPERAÇÃO

### 3.1 Backup do Banco de Dados (`arione.db`)
- **Frequência**: Diária (mínimo).
- **Rotação**: Manter os últimos 7 backups diários e os últimos 4 semanais.
- **Localização**: Uma cópia local e uma cópia em nuvem (ou disco externo isolado).

---

## 4. MONITORAMENTO E LOGS

### 4.1 Log de Erros (Flask/Werkzeug)
- O arquivo `error.log` deve ser verificado semanalmente.
- Erros 500 devem ser tratados com prioridade máxima.

### 4.2 Uptime
- O processo do servidor deve ser gerenciado por um Windows Service ou similar para reiniciar automaticamente em caso de queda.

---

## 5. CONFIGURAÇÃO DE REDE E PORTAS

- **Porta Padrão**: 8081 (ou conforme configurado no ambiente).
- **Bind**: O servidor deve escutar em `0.0.0.0` para permitir acesso remoto, mas protegido por firewall de rede.

---
**FIM DO PAA-OPS v2.0**
