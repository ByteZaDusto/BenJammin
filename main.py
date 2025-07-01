import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv("secrets.env")
TOKEN = os.getenv("DISCORD_TOKEN")

# ID of the user to timeout if "Yes" wins
TARGET_USER_ID = 123456789012345678  # <-- Replace this with the actual user's Discord ID

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

# Slash command: /vote
@bot.tree.command(name="vote", description="Start a Yes/No vote")
async def vote(interaction: discord.Interaction):
    await interaction.response.send_message("Vote now! ✅ = Yes, ❌ = No (30 seconds)", ephemeral=False)

    message = await interaction.original_response()
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    await asyncio.sleep(30)  # Voting duration

    message = await interaction.channel.fetch_message(message.id)
    yes_votes = 0
    no_votes = 0

    for reaction in message.reactions:
        if reaction.emoji == "✅":
            yes_votes = reaction.count - 1  # exclude bot
        elif reaction.emoji == "❌":
            no_votes = reaction.count - 1

    total_votes = yes_votes + no_votes
    if total_votes == 0:
        await interaction.followup.send("No votes were cast.")
        return

    result = f"✅ Yes: {yes_votes}, ❌ No: {no_votes} — "

    if yes_votes / total_votes > 0.5:
        target_user = interaction.guild.get_member(253108416518553600)
        if target_user:
            try:
                # Timeout for 60 seconds
                await target_user.timeout(duration=60, reason="Vote passed to timeout user.")
                result += f"{target_user.mention} has been timed out!"
            except discord.Forbidden:
                result += "I don't have permission to timeout that user."
            except Exception as e:
                result += f"Failed to timeout user: {e}"
        else:
            result += "Target user not found."
    else:
        result += "Vote did not pass."

    await interaction.followup.send(result)

bot.run(TOKEN)
