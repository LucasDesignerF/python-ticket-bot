import nextcord
from nextcord.ext import commands
from db_mysql import get_db_connection

class Activation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="ativar", description="Ativa o bot no servidor")
    async def ativar(self, interaction: nextcord.Interaction, key: str):
        guild_id = interaction.guild.id

        # Defere a interação para dar mais tempo ao bot para processar a requisição
        await interaction.response.defer()

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se a chave está correta para o servidor
        cursor.execute("SELECT * FROM servidores WHERE server_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result:
            if result['activation_key'] == key:
                # As chaves coincidem
                await interaction.followup.send("Key ativada com sucesso!")
            else:
                # As chaves não coincidem, enviar mensagem na DM
                await interaction.user.send("Chave inválida. Por favor, entre em contato com o criador do bot: https://discord.gg/z5SkRN495p")
                await interaction.followup.send("Chave inválida.")
        else:
            await interaction.followup.send("Servidor não encontrado no banco de dados.")

        # Fecha a conexão com o banco de dados
        cursor.close()
        connection.close()

def setup(bot):
    bot.add_cog(Activation(bot))
