import os
import discord
from discord.ext import commands

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN not found in GitHub Secrets!")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'🤖 {bot.user} is online! Serving {len(bot.guilds)} servers.')
    print(f'🔗 Invite link: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=268435456&scope=bot')

@bot.command(name="help")
async def help(ctx):
    await ctx.send("💎 GEM BET - SAFE MODE 💎\n`!ping` - Test if bot is alive\n`!help` - This message")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! 🏓")

bot.run(TOKEN)
