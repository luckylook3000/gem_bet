import os
import discord
import random
import asyncio
import json
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# ==========================================
# 1. SETUP & SECRETS
# ==========================================
load_dotenv()
TOKEN = os.getenv("TOKEN")

# ==========================================
# 2. INTEGRATED ECONOMY SYSTEM (The Bank)
# ==========================================
DATA_FILE = "balances.json"

def load_bal():
    if not os.path.exists(DATA_FILE): return {}
    with open(DATA_FILE, "r") as f: return json.load(f)

def save_bal(b):
    with open(DATA_FILE, "w") as f: json.dump(b, f, indent=4)

def get_bal(u_id):
    return load_bal().get(str(u_id), 1000)

def update_bal(u_id, amt):
    b = load_bal()
    u_id = str(u_id)
    b[u_id] = b.get(u_id, 1000) + amt
    save_bal(b)
    return b[u_id]

# ==========================================
# 3. BOT CORE
# ==========================================
class GemBetBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ ALL COMMANDS SYNCED!")

bot = GemBetBot()

def get_embed(title, desc, color=0x2f3136):
    embed = discord.Embed(title=title, description=desc, color=color)
    embed.set_footer(text="GemBet💎 | Virtual Games")
    return embed

# ==========================================
# 4. UTILITY & ADMIN COMMANDS
# ==========================================
@bot.command()
async def sync(ctx):
    await bot.tree.sync(guild=ctx.guild)
    await ctx.send("🚀 **Commands Synced! Restart Discord (Ctrl+R) and use `/`**")

@bot.tree.command(name="balance", description="Check your balance")
async def balance(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    await interaction.response.send_message(embed=get_embed("💰 Balance", f"{target.mention}: **{get_bal(target.id)}** coins", 0x00ff00))

@bot.tree.command(name="tip", description="Tip another user")
async def tip(interaction: discord.Interaction, member: discord.Member, amount: int):
    if member.id == interaction.user.id: return await interaction.response.send_message("❌ No self-tipping!", ephemeral=True)
    if amount > get_bal(interaction.user.id) or amount <= 0: return await interaction.response.send_message("❌ Invalid amount!", ephemeral=True)
    update_bal(interaction.user.id, -amount)
    update_bal(member.id, amount)
    await interaction.response.send_message(embed=get_embed("💸 Tip Sent", f"Tipped {member.mention} **{amount}** coins!", 0xf1c40f))

@bot.tree.command(name="add", description="[MOD] Add coins")
async def add(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not interaction.user.guild_permissions.administrator: return await interaction.response.send_message("❌ No permission!", ephemeral=True)
    update_bal(member.id, amount)
    await interaction.response.send_message(embed=get_embed("➕ Added", f"Added **{amount}** to {member.mention}", 0x00ff00))

@bot.tree.command(name="remove", description="[MOD] Remove coins")
async def remove(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not interaction.user.guild_permissions.administrator: return await interaction.response.send_message("❌ No permission!", ephemeral=True)
    update_bal(member.id, -amount)
    await interaction.response.send_message(embed=get_embed("➖ Removed", f"Removed **{amount}** from {member.mention}", 0xff0000))

# ==========================================
# 5. INTERACTIVE GAMES
# ==========================================

@bot.tree.command(name="colordice", description="Bet on Red, Blue, or Green")
@app_commands.choices(color=[app_commands.Choice(name="🔴 Red", value="🔴"), app_commands.Choice(name="🔵 Blue", value="🔵"), app_commands.Choice(name="🟢 Green", value="🟢")])
async def colordice(interaction: discord.Interaction, bet: int, color: str):
    if bet > get_bal(interaction.user.id) or bet <= 0: return await interaction.response.send_message("❌ Invalid bet!", ephemeral=True)
    colors = ["🔴", "🔵", "🟢"]
    await interaction.response.send_message(embed=get_embed("🎲 Color Dice", f"Betting {bet} on {color}... Spinning! 🎰"))
    for _ in range(4):
        await asyncio.sleep(0.5)
        await interaction.edit_original_response(embed=get_embed("🎲 Color Dice", f"Spinning... {random.choice(colors)}"))
    final = random.choice(colors)
    if final == color:
        update_bal(interaction.user.id, bet)
        res, col = f"🎉 **WIN!** It was {final}!\nWon **{bet}** coins!", 0x00ff00
    else:
        update_bal(interaction.user.id, -bet)
        res, col = f"💀 **LOSS!** It was {final}.\nLost **{bet}** coins!", 0xff0000
    await interaction.edit_original_response(embed=get_embed("🎲 Color Dice", f"{res}\nBalance: **{get_bal(interaction.user.id)}**", col))

@bot.tree.command(name="roulette", description="Bet on 0-36")
async def roulette(interaction: discord.Interaction, bet: int, number: int):
    if not (0 <= number <= 36): return await interaction.response.send_message("❌ 0-36 only!", ephemeral=True)
    if bet > get_bal(interaction.user.id) or bet <= 0: return await interaction.response.send_message("❌ Invalid bet!", ephemeral=True)
    await interaction.response.send_message(embed=get_embed("🎡 Roulette", f"Betting {bet} on {number}... Spinning! 🎡"))
    for _ in range(4):
        await asyncio.sleep(0.4)
        await interaction.edit_original_response(embed=get_embed("🎡 Roulette", f"Spinning... {random.randint(0, 36)}"))
    final = random.randint(0, 36)
    if final == number:
        update_bal(interaction.user.id, bet * 35)
        res, col = f"🎊 **JACKPOT!** {final}!\nWon **{bet * 35}** coins!", 0x00ff00
    else:
        update_bal(interaction.user.id, -bet)
        res, col = f"💀 **LOSS!** It was {final}.\nLost **{bet}** coins!", 0xff0000
    await interaction.edit_original_response(embed=get_embed("🎡 Roulette", f"{res}\nBalance: **{get_bal(interaction.user.id)}**", col))

@bot.tree.command(name="blackjack", description="Play 21!")
async def blackjack(interaction: discord.Interaction, bet: int):
    if bet > get_bal(interaction.user.id) or bet <= 0: return await interaction.response.send_message("❌ Invalid bet!", ephemeral=True)
    p = [random.randint(2, 11), random.randint(2, 11)]
    d = [random.randint(2, 11), random.randint(2, 11)]
    
    class BJView(discord.ui.View):
        def __init__(self, user, bet, p_hand, d_hand):
            super().__init__(timeout=60)
            self.user, self.bet, self.p_hand, self.d_hand = user, bet, p_hand, d_hand
        @discord.ui.button(label="Hit 🃏", style=discord.ButtonStyle.green)
        async def hit(self, inter, btn):
            if inter.user != self.user: return await inter.response.defer()
            self.p_hand.append(random.randint(2, 11))
            if sum(self.p_hand) > 21:
                update_bal(self.user.id, -self.bet)
                await inter.response.edit_message(content=f"💥 **BUST!** Total {sum(self.p_hand)}. Lost {self.bet} coins.", embed=None, view=None)
            else:
                await inter.response.edit_message(content=f"🃏 Hand: `{self.p_hand}` (Total: {sum(self.p_hand)})", view=self)
        @discord.ui.button(label="Stand ✋", style=discord.ButtonStyle.red)
        async def stand(self, inter, btn):
            if inter.user != self.user: return await inter.response.defer()
            while sum(self.d_hand) < 17: self.d_hand.append(random.randint(2, 11))
            p_sum, d_sum = sum(self.p_hand), sum(self.d_hand)
            if d_sum > 21 or p_sum > d_sum:
                update_bal(self.user.id, bet)
                res = f"🎉 **WIN!** Dealer had {d_sum}."
            elif p_sum < d_sum:
                update_bal(self.user.id, -bet)
                res = f"💀 **LOSS!** Dealer had {d_sum}."
            else: res = "🤝 **PUSH!**"
            await inter.response.edit_message(content=f"{res}\nFinal: `{self.p_hand}`", embed=None, view=None)
    await interaction.response.send_message(f"🃏 **Blackjack!** Your hand: `{p}` (Total: {sum(p)})\nDealer shows: `{d[0]}`", view=BJView(interaction.user, bet, p, d))

@bot.event
async def on_ready():
    print(f'👑 Gem Bet is ONLINE as {bot.user}')

bot.run(TOKEN)
