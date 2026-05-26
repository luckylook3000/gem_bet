import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import economy
import casino # This imports the casino.py file

load_dotenv()
TOKEN = os.getenv("TOKEN")

class GemBetBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Load the Casino cog
        await self.add_cog(Casino(bot))
        await self.tree.sync()
        print("✅ Casino Loaded & Slash commands synced!")

bot = GemBetBot()

def get_casino_embed(title, desc, color=0x2f3136):
    embed = discord.Embed(title=title, description=desc, color=color)
    embed.set_footer(text="GemBet💎 | Virtual Games")
    return embed

# --- ADMIN SYNC ---
@bot.command()
async def sync(ctx):
    await bot.tree.sync(guild=ctx.guild)
    await ctx.send("🚀 **Commands Synced! Restart Discord (Ctrl+R) and use `/`**")

# --- PUBLIC ECONOMY ---
@bot.tree.command(name="balance", description="Check your coin balance")
async def balance(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    bal = economy.get_balance(target.id)
    await interaction.response.send_message(embed=get_casino_embed("💰 Balance Check", f"{target.mention} has **{bal}** coins.", 0x00ff00))

@bot.tree.command(name="tip", description="Tip another user")
async def tip(interaction: discord.Interaction, member: discord.Member, amount: int):
    if member.id == interaction.user.id: return await interaction.response.send_message("Can't tip yourself!", ephemeral=True)
    bal = economy.get_balance(interaction.user.id)
    if amount > bal or amount <= 0: return await interaction.response.send_message("❌ Insufficient funds!", ephemeral=True)
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
        await interaction.response.send_message(embed=get_casino_embed("🎉 Code Redeemed", f"You won **{reward}** coins!", 0x00ff00))
    else:
        await interaction.response.send_message("❌ Invalid code!", ephemeral=True)

# --- MOD ONLY ---
@bot.tree.command(name="add", description="[MOD] Add coins")
async def add(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not interaction.user.guild_permissions.administrator: return await interaction.response.send_message("❌ Not a Mod!", ephemeral=True)
    economy.update_balance(member.id, amount)
    await interaction.response.send_message(embed=get_casino_embed("➕ Added", f"Added **{amount}** coins to {member.mention}.", 0x00ff00))

@bot.tree.command(name="remove", description="[MOD] Remove coins")
async def remove(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not interaction.user.guild_permissions.administrator: return await interaction.response.send_message("❌ Not a Mod!", ephemeral=True)
    economy.update_balance(member.id, -amount)
    await interaction.response.send_message(embed=get_casino_embed("➖ Removed", f"Removed **{amount}** coins from {member.mention}.", 0xff0000))

@bot.tree.command(name="rain", description="[MOD] Rain coins")
async def rain(interaction: discord.Interaction, amount: int, recipients: int = 5):
    if not interaction.user.guild_permissions.administrator: return await interaction.response.send_message("❌ Not a Mod!", ephemeral=True)
    members = [m for m in interaction.guild.members if not m.bot and m.status != discord.Status.offline]
    if len(members) < recipients: return await interaction.response.send_message("Not enough online members!")
    lucky = random.sample(members, recipients)
    per_person = amount // recipients
    for u in lucky: economy.update_balance(u.id, per_person)
    await interaction.response.send_message(embed=get_casino_embed("💸 RAIN!", f"{interaction.user.mention} rained **{amount}** coins!\n{recipients} users got **{per_person}** each!", 0x3498db))

@bot.event
async def on_ready():
    print(f'👑 Gem Bet is ONLINE as {bot.user}')

bot.run(TOKEN)


