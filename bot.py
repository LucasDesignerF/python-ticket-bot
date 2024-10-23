import nextcord
from nextcord.ext import commands
import os
import mysql.connector
from dotenv import load_dotenv
from db_mysql import get_db_connection

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Ativa todas as intents
intents = nextcord.Intents.all()

# Criação do bot com intents e prefixo (para uso futuro)
bot = commands.Bot(command_prefix="!", intents=intents)

# Carrega os Cogs dinamicamente da pasta cogs
if __name__ == '__main__':
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

# Evento que inicia o bot
@bot.event
async def on_ready():
    # Conectar ao banco de dados
    try:
        connection = get_db_connection()
        if connection.is_connected():
            print("Conexão ao MySQL bem-sucedida!")
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")

    # Exibe o nome e ID do bot
    print(f'Bot conectado como {bot.user}')

    # Lista todos os comandos slash disponíveis
    print("Comandos Slash Disponíveis:")
    app_commands = bot.get_application_commands()  # Correção: removido o await
    for cmd in app_commands:
        print(f"- /{cmd.name}: {cmd.description}")

    # Lista os servidores onde o bot está presente
    print("Servidores em que o bot está presente:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")

bot.run(os.getenv('DISCORD_TOKEN'))
