import discord
import datetime
from discord.ext import commands
from discord import Object, app_commands, abc
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv("secrets.env")
TOKEN = os.getenv("DISCORD_TOKEN")

# IDs of Guilds (=Servers) that this bot is allowed in
CARC_KINGDOM_ID = 1274816593289019485
BYTE_TEST_SERVER_ID = 1184448108042670170

allowedGuilds = [
    CARC_KINGDOM_ID,
    BYTE_TEST_SERVER_ID,
]

allowed_guilds_objects = [discord.Object(id=guild_id) for guild_id in allowedGuilds]

# ID of the user to timeout if "Yes" wins
BENNY_ID = 797785685813493790
SPLOOF_ID = 806964705008025611
BYTE_ID = 253108416518553600

SECOND_RATE_CITIZENS = {
    BENNY_ID,
    SPLOOF_ID,
    #BYTE_ID,
}

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    for object in allowed_guilds_objects:
        await bot.tree.sync(guild=object)

    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

# Slash command: /vote
@bot.tree.command(name="vote", description="Start a Yes/No vote to timeout a user")
@app_commands.describe(user="The user to timeout if the vote passes")
async def vote(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(
        f"{interaction.user.mention} started a vote to timeout {user.mention}! ✅ = Yes, ❌ = No (30 seconds)",
        ephemeral=False
    )

    message = await interaction.original_response()
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    await asyncio.sleep(30)

    message = await interaction.channel.fetch_message(message.id)
    yes_votes = 0
    no_votes = 0

    for reaction in message.reactions:
        if reaction.emoji == "✅":
            yes_votes = reaction.count - 1
        elif reaction.emoji == "❌":
            no_votes = reaction.count - 1

    total_votes = yes_votes + no_votes
    if total_votes == 0:
        await interaction.followup.send("No votes were cast.")
        return

    result = f"✅ Yes: {yes_votes}, ❌ No: {no_votes} — "

    if yes_votes / total_votes > 0.5:
        target_user = interaction.guild.get_member(user.id)
        if target_user: 
            result += " " + str(datetime.timedelta(seconds=60))
            if target_user.id in SECOND_RATE_CITIZENS:
                try:
                    # Timeout for 60 seconds
                    await user.timeout(datetime.timedelta(seconds=60), reason="Vote passed to timeout user.")
                    result += f"{user.mention} has been timed out!"
                except discord.Forbidden:
                    result += "I don't have permission to timeout that user."
                except Exception as e:
                    result += f"Failed to timeout user: {e}"
            else: result += "You tried to timeout someone that's not a known liar."
    else:
         result += "Vote did not pass."

    await interaction.followup.send(result)

bot.run(TOKEN)
