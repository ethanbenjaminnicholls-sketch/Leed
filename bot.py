import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

import os
import json
import re
from datetime import timedelta

# -----------------------------
# Load Environment
# -----------------------------
load_dotenv()
TOKEN = os.getenv("TOKEN")

# -----------------------------
# Bot Intents
# -----------------------------
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

WELCOME_FILE = "welcome.json"

# -----------------------------
# Welcome Config
# -----------------------------
def load_welcome():
    if not os.path.exists(WELCOME_FILE):
        with open(WELCOME_FILE, "w") as f:
            json.dump({}, f)

    with open(WELCOME_FILE, "r") as f:
        return json.load(f)

def save_welcome(data):
    with open(WELCOME_FILE, "w") as f:
        json.dump(data, f, indent=4)

welcome_data = load_welcome()

# -----------------------------
# Time Parser
# -----------------------------
def parse_time(duration: str):

    match = re.fullmatch(r"(\d+)([mhdw])", duration.lower())

    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2)

    if unit == "m":
        return timedelta(minutes=amount)

    if unit == "h":
        return timedelta(hours=amount)

    if unit == "d":
        return timedelta(days=amount)

    if unit == "w":
        return timedelta(weeks=amount)

# -----------------------------
# Bot Ready
# -----------------------------
@bot.event
async def on_ready():

    synced = await bot.tree.sync()

    print("-------------------------")
    print(f"Logged in as {bot.user}")
    print(f"Synced {len(synced)} commands.")
    print("-------------------------")

# -----------------------------
# Member Join
# -----------------------------
@bot.event
async def on_member_join(member):

    guild_id = str(member.guild.id)

    if guild_id not in welcome_data:
        return

    data = welcome_data[guild_id]

    channel = member.guild.get_channel(data["channel"])

    if channel is None:
        return

    message = (
        data["message"]
        .replace("{mention}", member.mention)
        .replace("{user}", member.name)
        .replace("{server}", member.guild.name)
        .replace("{membercount}", str(member.guild.member_count))
    )

    await channel.send(message)

# -----------------------------
# /welcomesetup
# -----------------------------
@bot.tree.command(
    name="welcomesetup",
    description="Set the welcome channel and welcome message."
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    channel="Channel to send welcome messages",
    message="Use {mention}, {user}, {server}, {membercount}"
)
async def welcomesetup(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str
):

    guild_id = str(interaction.guild.id)

    welcome_data[guild_id] = {
        "channel": channel.id,
        "message": message
    }

    save_welcome(welcome_data)

    embed = discord.Embed(
        title="✅ Welcome System Setup",
        description="Your welcome system has been configured.",
        colour=discord.Colour.green()
    )

    embed.add_field(
        name="Channel",
        value=channel.mention,
        inline=False
    )

    embed.add_field(
        name="Message",
        value=message,
        inline=False
    )

    embed.set_footer(
        text="Supports: {mention} {user} {server} {membercount}"
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

# -----------------------------
# Welcome Permission Error
# -----------------------------
@welcomesetup.error
async def welcomesetup_error(interaction: discord.Interaction, error):

    if isinstance(error, app_commands.MissingPermissions):

        await interaction.response.send_message(
            "❌ You need Administrator permission to use this command.",
            ephemeral=True
        )

# -----------------------------
# /help
# -----------------------------
@bot.tree.command(
    name="help",
    description="View all commands."
)
async def help_command(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📖 Help",
        description="Available Commands",
        colour=discord.Colour.blurple()
    )

    embed.add_field(
        name="👋 Welcome",
        value="`/welcomesetup` - Configure welcome messages.",
        inline=False
    )

    embed.add_field(
        name="🛡️ Moderation",
        value=(
            "`/ban` - Ban a member\n"
            "`/kick` - Kick a member\n"
            "`/timeout` - Timeout a member\n"
            "`/role` - Give a role"
        ),
        inline=False
    )

    embed.set_footer(
        text="Administrator permission is required for moderation commands."
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

# -----------------------------
# /ban
# -----------------------------
@bot.tree.command(
    name="ban",
    description="Ban a member from the server."
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    user="User to ban",
    reason="Reason for the ban"
)
async def ban(
    interaction: discord.Interaction,
    user: discord.Member,
    reason: str = "No reason provided"
):

    await user.ban(reason=reason)

    embed = discord.Embed(
        title="🔨 User Banned",
        colour=discord.Colour.red()
    )

    embed.add_field(
        name="User",
        value=user.mention,
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


# -----------------------------
# /kick
# -----------------------------
@bot.tree.command(
    name="kick",
    description="Kick a member from the server."
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    user="User to kick",
    reason="Reason for the kick"
)
async def kick(
    interaction: discord.Interaction,
    user: discord.Member,
    reason: str = "No reason provided"
):

    await user.kick(reason=reason)

    embed = discord.Embed(
        title="👢 User Kicked",
        colour=discord.Colour.orange()
    )

    embed.add_field(
        name="User",
        value=user.mention,
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


# -----------------------------
# /role
# -----------------------------
@bot.tree.command(
    name="role",
    description="Give a role to a user."
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    user="User to give the role to",
    role="Role to give"
)
async def role(
    interaction: discord.Interaction,
    user: discord.Member,
    role: discord.Role
):

    await user.add_roles(role)

    embed = discord.Embed(
        title="✅ Role Added",
        colour=discord.Colour.green()
    )

    embed.add_field(
        name="User",
        value=user.mention,
        inline=False
    )

    embed.add_field(
        name="Role",
        value=role.mention,
        inline=False
    )

    embed.set_footer(
        text=f"Added by {interaction.user}"
    )

    await interaction.response.send_message(
        embed=embed
    )


# -----------------------------
# /timeout
# -----------------------------
@bot.tree.command(
    name="timeout",
    description="Timeout a member."
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    user="User to timeout",
    time="Duration e.g. 10m, 1h, 2d",
    reason="Reason for timeout"
)
async def timeout(
    interaction: discord.Interaction,
    user: discord.Member,
    time: str,
    reason: str = "No reason provided"
):

    duration = parse_time(time)

    if duration is None:
        await interaction.response.send_message(
            "❌ Invalid time format. Use: `10m`, `1h`, `2d`, `1w`",
            ephemeral=True
        )
        return

    await user.timeout(
        duration,
        reason=reason
    )

    embed = discord.Embed(
        title="⏳ User Timed Out",
        colour=discord.Colour.yellow()
    )

    embed.add_field(
        name="User",
        value=user.mention,
        inline=False
    )

    embed.add_field(
        name="Duration",
        value=time,
        inline=False
    )

    embed.add_field(
        name="Reason",
        value=reason,
        inline=False
    )

    embed.set_footer(
        text=f"Timed out by {interaction.user}"
    )

    await interaction.response.send_message(
        embed=embed
    )

# -----------------------------
# Global Permission Error Handler
# -----------------------------
@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error
):

    if isinstance(error, app_commands.MissingPermissions):

        message = (
            "❌ You need **Administrator** permission "
            "to use this command."
        )

        if interaction.response.is_done():

            await interaction.followup.send(
                message,
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                message,
                ephemeral=True
            )


    elif isinstance(error, app_commands.CommandInvokeError):

        if interaction.response.is_done():

            await interaction.followup.send(
                "❌ Something went wrong while running this command.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ Something went wrong while running this command.",
                ephemeral=True
            )

# -----------------------------
# Start Bot
# -----------------------------
if TOKEN is None:

    print("❌ ERROR: No bot token found in .env file!")

else:

    bot.run(TOKEN)
