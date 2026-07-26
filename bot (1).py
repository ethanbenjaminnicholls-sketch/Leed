# ==========================================================
# Discord Moderation Bot
# PART 1
# ==========================================================

import discord
from discord.ext import commands
from discord import app_commands

import json
import os

# -----------------------------
# BOT SETUP
# -----------------------------

from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

WELCOME_FILE = "welcome.json"

# -----------------------------
# CREATE WELCOME FILE
# -----------------------------

if not os.path.exists(WELCOME_FILE):
    with open(WELCOME_FILE, "w") as f:
        json.dump({}, f)

# -----------------------------
# LOAD / SAVE FUNCTIONS
# -----------------------------

def load_welcome():

    with open(WELCOME_FILE, "r") as f:
        return json.load(f)


def save_welcome(data):

    with open(WELCOME_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -----------------------------
# BOT READY
# -----------------------------

@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")

    except Exception as e:
        print(e)

    print(f"Logged in as {bot.user}")

# -----------------------------
# MEMBER JOIN
# -----------------------------

@bot.event
async def on_member_join(member):

    data = load_welcome()

    guild_id = str(member.guild.id)

    if guild_id not in data:
        return

    channel = bot.get_channel(
        data[guild_id]["channel"]
    )

    if channel is None:
        return

    message = data[guild_id]["message"]

    message = message.replace(
        "{mention}",
        member.mention
    )

    await channel.send(message)

# ==========================================================
# /BAN COMMAND
# ==========================================================

@bot.tree.command(
    name="ban",
    description="Ban a member"
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No reason provided"
):

    if member == interaction.user:

        await interaction.response.send_message(
            "❌ You cannot ban yourself.",
            ephemeral=True
        )
        return

    try:

        await member.ban(reason=reason)

        embed = discord.Embed(
            title="🔨 Member Banned",
            colour=discord.Colour.red()
        )

        embed.add_field(
            name="User",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(
            text=f"Banned by {interaction.user}"
        )

        await interaction.response.send_message(
            embed=embed
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ I don't have permission to ban that member.",
            ephemeral=True
        )

# ==========================================================
# PASTE PART 2 BELOW THIS LINE
# ==========================================================

# ==========================================================
# /KICK COMMAND
# ==========================================================

@bot.tree.command(
    name="kick",
    description="Kick a member"
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No reason provided"
):

    if member == interaction.user:

        await interaction.response.send_message(
            "❌ You cannot kick yourself.",
            ephemeral=True
        )
        return

    try:

        await member.kick(reason=reason)

        embed = discord.Embed(
            title="👢 Member Kicked",
            colour=discord.Colour.orange()
        )

        embed.add_field(
            name="User",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(
            text=f"Kicked by {interaction.user}"
        )

        await interaction.response.send_message(
            embed=embed
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ I don't have permission to kick that member.",
            ephemeral=True
        )


# ==========================================================
# /ROLE COMMAND
# ==========================================================

@bot.tree.command(
    name="role",
    description="Give or remove a role from a member"
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def role(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role
):

    try:

        if role in member.roles:

            await member.remove_roles(role)

            embed = discord.Embed(
                title="➖ Role Removed",
                colour=discord.Colour.red()
            )

            embed.description = (
                f"Removed {role.mention} from {member.mention}"
            )

        else:

            await member.add_roles(role)

            embed = discord.Embed(
                title="➕ Role Added",
                colour=discord.Colour.green()
            )

            embed.description = (
                f"Added {role.mention} to {member.mention}"
            )

        embed.set_footer(
            text=f"Action by {interaction.user}"
        )

        await interaction.response.send_message(
            embed=embed
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ I don't have permission to manage that role.",
            ephemeral=True
        )


# ==========================================================
# PERMISSION ERROR HANDLER
# ==========================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    if isinstance(error, app_commands.MissingPermissions):

        await interaction.response.send_message(
            "❌ You need Administrator permission to use this command.",
            ephemeral=True
        )

    else:
        raise error


# ==========================================================
# PASTE PART 3 BELOW THIS LINE
# ==========================================================

# ==========================================================
# /WELCOMESETUP COMMAND
# ==========================================================

@bot.tree.command(
    name="welcomesetup",
    description="Setup the server welcome message"
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def welcomesetup(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str
):

    data = load_welcome()

    guild_id = str(interaction.guild.id)

    data[guild_id] = {
        "channel": channel.id,
        "message": message
    }

    save_welcome(data)

    embed = discord.Embed(
        title="✅ Welcome System Setup",
        colour=discord.Colour.green()
    )

    embed.add_field(
        name="Welcome Channel",
        value=channel.mention,
        inline=False
    )

    embed.add_field(
        name="Message",
        value=message,
        inline=False
    )

    embed.add_field(
        name="Mention Support",
        value="Use `{mention}` to mention new members.",
        inline=False
    )

    embed.set_footer(
        text=f"Setup by {interaction.user}"
    )

    await interaction.response.send_message(
        embed=embed
    )