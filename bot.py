import os
import discord
from discord.ext import commands
from discord import option
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_tickets = {}

class TicketView(discord.ui.View):
    @discord.ui.button(label="👁️ Open Ticket", style=discord.ButtonStyle.blurple, custom_id="open_ticket_button")
    async def open_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
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
    print(f"✅ Logged in as {bot.user}")

@bot.slash_command(name="openpanel", description="Send the ticket panel")
@option("channel", description="Where to send the panel", channel_types=[discord.ChannelType.text])
async def openpanel(ctx, channel: discord.TextChannel):
    embed = discord.Embed(
        title="What's this about?",
        description="**Open A Ticket To Buy!**\n\n```How Do I open a ticket?\nTo open a ticket, just click the button below!```",
        color=discord.Color.magenta()
    )
    await channel.send(embed=embed, view=TicketView())
    await ctx.respond("✅ Ticket panel sent.", ephemeral=True)

@bot.slash_command(name="close", description="Close the ticket (remove user access)")
async def close(ctx):
    channel = ctx.channel
    if not channel.name.startswith("ticket-"):
        await ctx.respond("❌ This is not a ticket channel.", ephemeral=True)
        return

    user = ctx.author
    await channel.set_permissions(user, view_channel=False)
    await ctx.respond("🔒 Ticket closed. Use `/open` to reopen it.", ephemeral=False)

@bot.slash_command(name="open", description="Reopen the ticket (restore user access)")
async def open(ctx):
    channel = ctx.channel
    if not channel.name.startswith("ticket-"):
        await ctx.respond("❌ This is not a ticket channel.", ephemeral=True)
        return

    user = ctx.author
    await channel.set_permissions(user, view_channel=True, send_messages=True, read_message_history=True)
    await ctx.respond("🔓 Ticket reopened.", ephemeral=False)

@bot.slash_command(name="delete", description="Delete the ticket channel")
async def delete(ctx):
    channel = ctx.channel
    if not channel.name.startswith("ticket-"):
        await ctx.respond("❌ This is not a ticket channel.", ephemeral=True)
        return

    for user_id, chan_id in list(user_tickets.items()):
        if chan_id == channel.id:
            del user_tickets[user_id]
            break

    await ctx.respond("🗑️ Deleting this ticket...", ephemeral=True)
    await channel.delete()

@bot.slash_command(name="pay", description="Show payment instructions")
async def pay(ctx):
    embed = discord.Embed(
        title="How To Pay",
        description="`Cashapp: $MacAndCheeseFr`\n`Crypto: Tell Me Which You are paying with.`",
        color=discord.Color.magenta()
    )
    await ctx.respond(embed=embed)

bot.run(os.getenv("TOKEN"))
