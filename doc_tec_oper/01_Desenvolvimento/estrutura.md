📖 Estrutura e Funções do Projeto AriOne v.1.05
Este guia descreve a função de cada diretório e arquivo principal para facilitar a manutenção do sistema.

Diretórios (Pastas)
routes/: O Cérebro. Contém a lógica de navegação e as regras de negócio. Cada arquivo .py decide o que exibir quando o usuário acessa uma URL (Ex: vendas.py, financeiro.py).

templates/: O Visual. Guarda os arquivos HTML. É o esqueleto das páginas que o usuário vê no navegador.
funcoes_das_pastas.txt
static/: A Estética. Armazena arquivos estáticos que não mudam, como folhas de estilo (CSS), scripts (JavaScript) e imagens de logomarca.

utils/: Ferramentas. Guarda funções de suporte que são reutilizadas em várias partes do sistema, como validadores de documentos ou formatadores de data.

Doc_DEV/: Documentação. Local para armazenar manuais, diagramas e este guia de funções.

Arquivos Principais (Raiz)
app.py: O Coração. Onde o Flask é configurado, as extensões são inicializadas e todos os Blueprints (rotas) são registrados.

main.py: A Chave de Ignição. O arquivo de entrada do sistema. É o que você executa no terminal para ligar o servidor.

models.py: A Estrutura de Dados. Define as tabelas do banco de dados (Usuários, Produtos, etc.) usando SQLAlchemy.

config.py: Configurações. Centraliza variáveis de ambiente, chaves secretas e caminhos do banco de dados.

arione_dev.db: A Memória. O arquivo SQLite real que contém todos os dados gravados no sistema.

requirements.txt: A Lista de Compras. Contém todas as bibliotecas Python necessárias para rodar o projeto.