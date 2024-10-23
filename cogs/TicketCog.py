import nextcord
from nextcord.ext import commands
from nextcord.ui import Select, View, Button
from db_mysql import get_db_connection
import logging
import asyncio
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO)

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='configurar_ticket', description='Configura o sistema de tickets.')
    @commands.has_permissions(administrator=True)
    async def configurar_ticket(self, interaction: nextcord.Interaction, 
                                 ticket_channel: nextcord.TextChannel = None, 
                                 admin_role: nextcord.Role = None, 
                                 category: nextcord.CategoryChannel = None, 
                                 review_channel: nextcord.TextChannel = None, 
                                 background_image_url: str = None): 
        
        if not all([ticket_channel, admin_role, category, review_channel, background_image_url]):
            await interaction.response.send_message("Por favor, forneça todos os parâmetros necessários.")
            return

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(""" 
                INSERT INTO tickets_config (server_id, ticket_channel_id, admin_role_id, category_id, review_channel_id, background_image_url) 
                VALUES (%s, %s, %s, %s, %s, %s) 
                ON DUPLICATE KEY UPDATE 
                    ticket_channel_id = %s, admin_role_id = %s, category_id = %s, review_channel_id = %s, background_image_url = %s
            """, (str(interaction.guild.id), str(ticket_channel.id), str(admin_role.id), 
                  str(category.id), str(review_channel.id), background_image_url, 
                  str(ticket_channel.id), str(admin_role.id), 
                  str(category.id), str(review_channel.id), background_image_url))
            connection.commit()
            await interaction.response.send_message("Sistema de tickets configurado com sucesso!")
        except Exception as e:
            logging.error(f"Erro ao salvar configurações: {e}")
            await interaction.response.send_message("Houve um erro ao salvar as configurações.")
        finally:
            cursor.close()
            connection.close()

    async def create_ticket_interface(self, ticket_channel, config):
        embed_info = nextcord.Embed(
            title="🎟️ Informações do Ticket",
            description="Selecione uma categoria para o seu ticket.",
            color=nextcord.Color.blue()
        )

        if config['background_image_url']:
            embed_info.set_image(url=config['background_image_url'])

        select = Select(
            placeholder="Selecione uma categoria...",
            options=[
                nextcord.SelectOption(label="🛠️ Suporte Técnico", value="suporte_tecnico", description="Assistência técnica."),
                nextcord.SelectOption(label="💰 Suporte Financeiro", value="suporte_financeiro", description="Ajuda financeira."),
                nextcord.SelectOption(label="🛒 Área de Compras", value="area_compras", description="Questões de compras."),
                nextcord.SelectOption(label="🗨️ Outros Assuntos", value="outros_assuntos", description="Outras dúvidas.")
            ]
        )

        # Criando a view sem timeout
        view = View(timeout=None)
        view.add_item(select)
        await ticket_channel.send(embed=embed_info, view=view)

        async def select_callback(interaction):
            await self.create_ticket(interaction, select.values[0], config)

        select.callback = select_callback

    async def create_ticket(self, interaction, selected_category, config):
        category = self.bot.get_channel(int(config['category_id']))
        
        overwrites = {
            interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            interaction.user: nextcord.PermissionOverwrite(read_messages=True)
        }
        ticket_channel = await category.create_text_channel(f'ticket-{interaction.user.name}', overwrites=overwrites)

        embed_ticket = nextcord.Embed(
            title="🎟️ Novo Ticket",
            description=f"Seu ticket foi criado com sucesso na categoria **{selected_category}**.",
            color=nextcord.Color.blue()
        )
        await ticket_channel.send(embed=embed_ticket)

        close_button = Button(label="Fechar Ticket", style=nextcord.ButtonStyle.red)
        attend_button = Button(label="Atender Ticket", style=nextcord.ButtonStyle.green)

        async def close_ticket(interaction):
            await interaction.channel.send("Ticket fechado.")
            await interaction.user.send("Avalie o atendimento.")
            
            await interaction.user.send("Digite sua avaliação:")

            def check(message):
                return message.author == interaction.user and message.channel == interaction.user.dm_channel

            try:
                evaluation_message = await self.bot.wait_for('message', check=check, timeout=60)
                evaluation = evaluation_message.content

                attendant = interaction.user
                category_name = selected_category
                date_str = datetime.now().strftime("%d/%m/%Y %H:%M")

                review_channel = self.bot.get_channel(int(config['review_channel_id']))
                await review_channel.send(f"📝 **Avaliação do Ticket**\n"
                                          f"👤 **Membro**: {interaction.user.mention}\n"
                                          f"🧑‍⚕️ **Atendente**: {attendant.mention}\n"
                                          f"📂 **Categoria**: {category_name}\n"
                                          f"📅 **Data**: {date_str}\n"
                                          f"💬 **Avaliação**: {evaluation}")

                await interaction.user.send("Sua avaliação foi registrada.")
            except asyncio.TimeoutError:
                await interaction.user.send("Você não enviou sua avaliação a tempo.")
            
            await asyncio.sleep(5)
            await interaction.channel.delete()

        async def attend_ticket(interaction):
            if config['admin_role_id'] and interaction.user in interaction.guild.get_role(int(config['admin_role_id'])).members:
                await ticket_channel.send(f"{interaction.user.mention} está atendendo.")
            else:
                await interaction.response.send_message("Você não tem permissão.", ephemeral=True)

        close_button.callback = close_ticket
        attend_button.callback = attend_ticket

        view = View()
        view.add_item(close_button)
        view.add_item(attend_button)
        await ticket_channel.send("Use os botões abaixo para fechar ou atender o ticket:", view=view)

    @nextcord.slash_command(name='criar_ticket', description='Cria um ticket de atendimento.')
    async def criar_ticket(self, interaction: nextcord.Interaction):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tickets_config WHERE server_id = %s", (str(interaction.guild.id),))
        
        config = cursor.fetchone()
        cursor.fetchall()

        cursor.close()
        connection.close()

        if not config:
            await interaction.response.send_message("O sistema de tickets não está configurado.") 
            return

        ticket_channel = self.bot.get_channel(int(config['ticket_channel_id']))

        async for message in ticket_channel.history(limit=100):
            if message.embeds and message.embeds[0].title == "🎟️ Informações do Ticket":
                await self.create_ticket_interface(ticket_channel, config)
                return
        
        await self.create_ticket_interface(ticket_channel, config)

def setup(bot):
    bot.add_cog(TicketCog(bot))
