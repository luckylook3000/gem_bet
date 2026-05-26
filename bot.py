import os
import discord
import random
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import economy

load_dotenv()
TOKEN = os.getenv("TOKEN")

class GemBetBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This syncs globally (slow)
        await self.tree.sync()
        print("✅ Global Slash commands synced!")

bot = GemBetBot()

def get_casino_embed(title, description, color=0x2f3136):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="💎 Gem Bet | 18+ Virtual Gambling")
    return embed

# --- ADMIN SYNC COMMAND (THE SECRET WEAPON) ---
@bot.command()
@commands.is_owner() # Only you can use this
async def sync(ctx):
    """Force syncs slash commands to the current server instantly"""
    await bot.tree.sync(guild=ctx.guild)
    await ctx.send("🚀 **Slash commands forced to sync! Restart your Discord app and type `/`**")

# --- SLASH COMMANDS ---

@bot.tree.command(name="balance", description="Check your coin balance")
async def balance(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    bal = economy.get_balance(target.id)
    await interaction.response.send_message(embed=get_casino_embed("💰 Balance Check", f"{target.mention} has **{bal}** coins.", 0x00ff00))

@bot.tree.command(name="dice", description="Bet on high (4-6) or low (1-3)")
@app_commands.choices(choice=[
    app_commands.Choice(name="High (4-6)", value="high"),
    app_commands.Choice(name="Low (1-3)", value="low"),
])
async def dice(interaction: discord.Interaction, bet: int, choice: str):
    bal = economy.get_balance(interaction.user.id)
    if bet > bal or bet <= 0:
        return await interaction.response.send_message("❌ Invalid bet amount!", ephemeral=True)

    roll = random.randint(1, 6)
    win = (choice == 'high' and roll >= 4) or (choice == 'low' and roll <= 3)
    
    if win:
        economy.update_balance(interaction.user.id, bet)
        res = f"🎉 **WIN!** Rolled {roll}. You won **{bet}** coins!"
        color = 0x00ff00
    else:
        economy.update_balance(interaction.user.id, -bet)
        res = f"💀 **LOSS!** Rolled {roll}. You lost **{bet}** coins!"
        color = 0xff0000

    await interaction.response.send_message(embed=get_casino_embed("🎲 Dice Roll", f"{interaction.user.mention} bet {bet} on {choice}...\n{res}\n\nBalance: **{economy.get_balance(interaction.user.id)}**", color))

@bot.tree.command(name="rain", description="Distribute coins to random online users")
async def rain(interaction: discord.Interaction, amount: int, recipients: int = 5):
    # Add permission check manually since it's a slash command
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Only admins can rain coins!", ephemeral=True)
    
    members = [m for m in interaction.guild.members if not m.bot and m.status != discord.Status.offline]
    if len(members) < recipients:
        return await interaction.response.send_message(f"Not enough online members!")

    lucky_users = random.sample(members, recipients)
    per_person = amount // recipients
    for user in lucky_users: economy.update_balance(user.id, per_person)
    
    mentions = " ".join([u.mention for u in lucky_users])
    await interaction.response.send_message(embed=get_casino_embed("💸 RAIN!", f"{interaction.user.mention} rained **{amount}** coins!\n{recipients} users got **{per_person}** each!\n\n{mentions}", 0x3498db))

@bot.tree.command(name="tip", description="Tip another user")
async def tip(interaction: discord.Interaction, member: discord.Member, amount: int):
    if member.id == interaction.user.id:
        return await interaction.response.send_message("You can't tip yourself!", ephemeral=True)
    bal = economy.get_balance(interaction.user.id)
    if amount > bal or amount <= 0:
        return await interaction.response.send_message("❌ Insufficient funds!", ephemeral=True)
    economy.update_balance(interaction.user.id, -amount)
    economy.update_balance(member.id, amount)
    await interaction.response.send_message(embed=get_casino_embed("💸 Tip Sent", f"{interaction.user.mention} tipped {member.mention} **{amount}** coins!", 0xf1c40f))

@bot.tree.command(name="redeem", description="Redeem a promo code")
async def redeem(interaction: discord.Interaction, code: str):
    codes = {"GEMBET100": 100, "KING": 500}
    code = code.upper()
    if code in codes:
        reward = codes[code]
        economy.update_balance(interaction.user.id, reward)
        await interaction.response.send_message(embed=get_casino_embed("🎉 Code Redeemed", f"You used `{code}` and won **{reward}** coins!", 0x00ff00))
    else:
        await interaction.response.send_message("❌ Invalid code!", ephemeral=True)

@bot.event
async def on_ready():
    print(f'👑 Gem Bet is ONLINE as {bot.user}')

bot.run(TOKEN)
