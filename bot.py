import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

user_tickets = {}

class TicketView(discord.ui.View):
    @discord.ui.button(label="👁️ Open Ticket", style=discord.ButtonStyle.blurple, custom_id="open_ticket_button")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        guild = interaction.guild

        if user_id in user_tickets and guild.get_channel(user_tickets[user_id]):
            await interaction.response.send_message("❌ You already have an open ticket!", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites,
            topic=f"Ticket for {interaction.user.name}"
        )

        user_tickets[user_id] = ticket_channel.id
        await ticket_channel.send(f"{interaction.user.mention}, welcome! Use `/close` when you're done.")
        await interaction.response.send_message(f"✅ Ticket opened: {ticket_channel.mention}", ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

@tree.command(name="openpanel", description="Send the ticket panel")
@app_commands.describe(channel="The channel to send the panel to")
async def openpanel(interaction: discord.Interaction, channel: discord.TextChannel):
    embed = discord.Embed(
        title="What's this about?",
        description="**Open A Ticket To Buy!**\n\n```How Do I open a ticket?\nTo open a ticket, just click the button below!```",
        color=discord.Color.magenta()
    )
    await channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ Ticket panel sent.", ephemeral=True)

@tree.command(name="close", description="Close the ticket (remove user access)")
async def close(interaction: discord.Interaction):
    channel = interaction.channel
    if not channel.name.startswith("ticket-"):
        await interaction.response.send_message("❌ This is not a ticket channel.", ephemeral=True)
        return

    await channel.set_permissions(interaction.user, view_channel=False)
    await interaction.response.send_message("🔒 Ticket closed. Use `/open` to reopen it.")

@tree.command(name="open", description="Reopen the ticket")
async def open(interaction: discord.Interaction):
    channel = interaction.channel
    if not channel.name.startswith("ticket-"):
        await interaction.response.send_message("❌ This is not a ticket channel.", ephemeral=True)
        return

    await channel.set_permissions(interaction.user, view_channel=True, send_messages=True, read_message_history=True)
    await interaction.response.send_message("🔓 Ticket reopened.")

@tree.command(name="delete", description="Delete the ticket channel")
async def delete(interaction: discord.Interaction):
    channel = interaction.channel
    if not channel.name.startswith("ticket-"):
        await interaction.response.send_message("❌ This is not a ticket channel.", ephemeral=True)
        return

    for user_id, chan_id in list(user_tickets.items()):
        if chan_id == channel.id:
            del user_tickets[user_id]
            break

    await interaction.response.send_message("🗑️ Deleting this ticket...", ephemeral=True)
    await channel.delete()

@tree.command(name="pay", description="Show payment instructions")
async def pay(interaction: discord.Interaction):
    embed = discord.Embed(
        title="How To Pay",
        description=":CashApp~1: `Cashapp: $MacAndCheeseFr`\n:pay_btc: :eth: `Crypto: Tell Me Which You are paying with.`",
        color=discord.Color.magenta()
    )
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("TOKEN"))
