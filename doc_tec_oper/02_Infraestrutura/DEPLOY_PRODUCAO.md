# Deploy em Produção - AriOne ERP

Este guia explica como configurar o AriOne para rodar 24/7 em um servidor com acesso externo.

---

## 📋 Pré-requisitos

- Python 3.8+
- Virtualenv instalado
- Banco de dados configurado
- Porta 5000 liberada no firewall

---

## 🪟 Windows (Serviço do Windows)

### Opção 1: Usando NSSM (Recomendado)

1. **Baixe e instale NSSM:**
   - Acesse: https://nssm.cc/download
   - Extraia e adicione ao PATH do sistema

2. **Execute o script de instalação:**
   ```cmd
   cd c:\AriONEDEV
   install_windows_service.bat
   ```

3. **Comandos úteis:**
   ```cmd
   nssm start AriOneERP          # Iniciar
   nssm stop AriOneERP           # Parar
   nssm restart AriOneERP        # Reiniciar
   nssm remove AriOneERP confirm # Remover
   ```

### Opção 2: Usando Waitress (Simplificado)

1. **Instale Waitress:**
   ```cmd
   venv\Scripts\pip install waitress
   ```

2. **Crie o arquivo `run_prod.py`:**
   ```python
   from waitress import serve
   from app.app import create_app

   app = create_app()
   serve(app, host='0.0.0.0', port=5000, threads=4)
   ```

3. **Execute:**
   ```cmd
   venv\Scripts\python run_prod.py
   ```

---

## 🐧 Linux (Systemd + Gunicorn)

### Instalação

1. **Instale Gunicorn:**
   ```bash
   venv/bin/pip install gunicorn
   ```

2. **Copie o arquivo de serviço:**
   ```bash
   sudo cp arione.service /etc/systemd/system/
   ```

3. **Edite o arquivo de serviço:**
   ```bash
   sudo nano /etc/systemd/system/arione.service
   ```
   
   Altere os caminhos:
   - `WorkingDirectory=/caminho/para/AriONEDEV`
   - `ExecStart=/caminho/para/AriONEDEV/venv/bin/gunicorn ...`

4. **Ative e inicie o serviço:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable arione
   sudo systemctl start arione
   ```

5. **Verifique o status:**
   ```bash
   sudo systemctl status arione
   ```

### Comandos úteis

```bash
sudo systemctl start arione      # Iniciar
sudo systemctl stop arione       # Parar
sudo systemctl restart arione     # Reiniciar
sudo systemctl status arione      # Status
sudo journalctl -u arione -f      # Ver logs em tempo real
```

---

## 🔧 Configuração de Rede

### Acesso Externo

1. **Configure o firewall para liberar a porta 5000:**

   **Windows:**
   ```cmd
   netsh advfirewall firewall add rule name="AriOne" dir=in action=allow protocol=TCP localport=5000
   ```

   **Linux (UFW):**
   ```bash
   sudo ufw allow 5000/tcp
   ```

2. **Configure o roteador (Port Forwarding):**
   - Redirecione a porta 5000 para o IP interno do servidor
   - Use uma porta externa diferente (ex: 8080) por segurança

3. **Configure HTTPS (Recomendado):**
   - Use Nginx ou Apache como proxy reverso
   - Instale certificado SSL com Let's Encrypt

---

## 📊 Monitoramento

### Verificar se o serviço está rodando

**Windows:**
```cmd
sc query AriOneERP
```

**Linux:**
```bash
sudo systemctl status arione
```

### Logs

**Windows:**
- Logs em: `c:\AriONEDEV\logs\arione_stdout.log`
- Erros em: `c:\AriONEDEV\logs\arione_stderr.log`

**Linux:**
```bash
sudo journalctl -u arione -f
```

---

## 🔒 Segurança

1. **Use HTTPS em produção:**
   - Configure Nginx/Apache com SSL
   - Use Let's Encrypt para certificados gratuitos

2. **Configure variáveis de ambiente:**
   ```bash
   export SECRET_KEY="sua-chave-secreta-aqui"
   export DATABASE_URL="sqlite:///arione_prod.db"
   ```

3. **Limite o acesso por IP:**
   - Configure o firewall para aceitar apenas IPs confiáveis
   - Use VPN para acesso administrativo

4. **Backups automáticos:**
   - Configure agendamento de backups no sistema
   - Use a aba Sistema/Armazenamento/Agendamento

---

## 🚀 Inicialização Manual (Testes)

### Desenvolvimento
```bash
python run.py
```

### Produção (Gunicorn)
```bash
gunicorn --config gunicorn.conf.py app.app:create_app()
```

### Produção (Waitress - Windows)
```bash
venv\Scripts\python run_prod.py
```

---

## 📝 Solução de Problemas

### Serviço não inicia

1. Verifique os logs
2. Verifique se a porta 5000 está em uso
3. Verifique permissões de arquivo
4. Teste manualmente antes de instalar como serviço

### Erro de permissão (Linux)

```bash
sudo chown -R www-data:www-data /caminho/para/AriONEDEV
```

### Porta já em uso

**Windows:**
```cmd
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Linux:**
```bash
sudo lsof -i :5000
sudo kill -9 <PID>
```

---

## 📞 Suporte

Para mais informações, consulte a documentação em `Doc_DEV/`.
