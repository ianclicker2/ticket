import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = False

bot = commands.Bot(command_prefix="!", intents=intents)
ticket_channels = {}  # Keeps track of active tickets by user ID

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="👁️ Open Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket"))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="openpanel", description="Send the ticket panel to a channel")
@app_commands.describe(channel="The channel to send the panel to")
async def openpanel(interaction: discord.Interaction, channel: discord.TextChannel):
    embed = discord.Embed(title="Support Ticket Panel", description="Click the button to open a ticket.", color=0xFF69B4)
    await channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Ticket panel sent!", ephemeral=True)

@bot.tree.command(name="pay", description="Show payment instructions")
async def pay(interaction: discord.Interaction):
    embed = discord.Embed(title="How to Pay", color=0xFF69B4)
    embed.description = ":CashApp~1: `Cashapp: $MacAndCheeseFr`\n:pay_btc: :eth: `Crypto: Tell Me Which You are paying with.`"
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="close", description="Close the ticket")
async def close(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.user, view_channel=False)
    await interaction.response.send_message("Ticket closed.")

@bot.tree.command(name="open", description="Reopen the ticket")
async def open(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.user, view_channel=True)
    await interaction.response.send_message("Ticket reopened.")

@bot.tree.command(name="delete", description="Delete the ticket channel")
async def delete(interaction: discord.Interaction):
    await interaction.channel.delete()

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data["custom_id"] == "open_ticket":
            user_id = interaction.user.id

            if user_id in ticket_channels:
                await interaction.response.send_message("You already have an open ticket!", ephemeral=True)
                return

            guild = interaction.guild
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }
            ticket_channel = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
            ticket_channels[user_id] = ticket_channel.id

            await ticket_channel.send(f"{interaction.user.mention}, thank you for opening a ticket. Staff will be with you shortly.")
            await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

    await bot.process_application_commands(interaction)

bot.run(os.getenv("TOKEN"))
