# Sistema de Tickets para Discord

Este projeto implementa um sistema de gerenciamento de tickets para servidores do Discord usando a biblioteca `nextcord`. O sistema permite que os usuários criem tickets de suporte e os administradores possam gerenciá-los eficientemente.

## Funcionalidades

- **Configuração do sistema de tickets**: Administradores podem configurar o sistema de tickets, definindo canais, categorias e funções.
- **Criação de tickets**: Usuários podem criar tickets com categorias específicas.
- **Gerenciamento de tickets**: Administradores podem atender e fechar tickets, além de coletar avaliações dos usuários após o fechamento.

## Pré-requisitos

Antes de começar, você precisa ter o seguinte instalado:

- Python 3.7 ou superior
- MySQL Server
- A biblioteca `nextcord` e outras dependências especificadas no arquivo `requirements.txt`

## Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/LucasDesignerF/python-ticket-bot.git
   cd python-ticket-bot
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure o arquivo `.env` com as seguintes variáveis:

   ```plaintext
   DISCORD_TOKEN=seu_token_aqui
   DB_HOST=localhost
   DB_USER=seu_usuario_db
   DB_PASSWORD=sua_senha_db
   DB_NAME=seu_nome_db
   ```

4. Crie as tabelas no banco de dados:

   ```sql
   CREATE TABLE tickets_config (
       server_id VARCHAR(255) PRIMARY KEY,
       ticket_channel_id VARCHAR(255),
       admin_role_id VARCHAR(255),
       category_id VARCHAR(255),
       review_channel_id VARCHAR(255),
       background_image_url TEXT
   );

   CREATE TABLE servidores (
       server_id VARCHAR(255) PRIMARY KEY,
       activation_key VARCHAR(255)
   );
   ```

## Uso

1. Inicie o bot:

   ```bash
   python bot.py
   ```

2. Utilize os comandos disponíveis:
   - `/configurar_ticket`: Configura o sistema de tickets no servidor.
   - `/criar_ticket`: Permite que os usuários criem tickets.

## Estrutura do Projeto

- `bot.py`: Arquivo principal que inicia o bot.
- `cogs/`: Diretório contendo os Cogs que gerenciam funcionalidades específicas.
  - `ticket_cog.py`: Implementa a lógica do sistema de tickets.
  - `activation.py`: Gerencia a ativação do bot no servidor.
- `db_mysql.py`: Função para conectar ao banco de dados MySQL.
- `requirements.txt`: Lista de dependências do projeto.

## Logs

Os logs de atividades e erros são registrados usando o módulo `logging`. Os logs podem ser visualizados no console onde o bot está sendo executado.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir um issue ou um pull request.

## Licença

Este projeto é licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.
