import random
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from economy import get_balance, update_balance

class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_embed(self, title, desc, color=0x2f3136):
        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_footer(text="GemBet💎 | Virtual Games")
        return embed

    # --- COLOR DICE (ANIMATED) ---
    @app_commands.command(name="colordice", description="Bet on a color! (Red, Blue, Green)")
    @app_commands.choices(color=[
        app_commands.Choice(name="🔴 Red", value="🔴"),
        app_commands.Choice(name="🔵 Blue", value="🔵"),
        app_commands.Choice(name="🟢 Green", value="🟢"),
    ])
    async def colordice(self, interaction: discord.Interaction, bet: int, color: str):
        bal = get_balance(interaction.user.id)
        if bet > bal or bet <= 0:
            return await interaction.response.send_message("❌ Invalid bet!", ephemeral=True)

        colors = ["🔴", "🔵", "🟢"]
        await interaction.response.send_message(embed=self.get_embed("🎲 Color Dice", f"Betting {bet} on {color}... Spinning! 🎰"))
        
        # Animation effect
        for _ in range(5):
            await asyncio.sleep(0.5)
            current_color = random.choice(colors)
            await interaction.edit_original_response(embed=self.get_embed("🎲 Color Dice", f"Spinning... {current_color}"))
        
        final_color = random.choice(colors)
        win = (final_color == color)
        
        if win:
            economy.update_balance(interaction.user.id, bet * 2)
            res = f"🎉 **WIN!** The color was {final_color}!\nWon **{bet * 2}** coins!"
            color_embed = 0x00ff00
        else:
            economy.update_balance(interaction.user.id, -bet)
            res = f"💀 **LOSS!** The color was {final_color}.\nLost **{bet}** coins!"
            color_embed = 0xff0000

        await interaction.edit_original_response(embed=self.get_embed("🎲 Color Dice", f"{res}\nBalance: **{get_balance(interaction.user.id)}**", color_embed))

    # --- ROULETTE (ANIMATED) ---
    @app_commands.command(name="roulette", description="Bet on a number (0-36)")
    async def roulette(self, interaction: discord.Interaction, bet: int, number: int):
        if number < 0 or number > 36:
            return await interaction.response.send_message("❌ Pick a number between 0 and 36!", ephemeral=True)
        bal = get_balance(interaction.user.id)
        if bet > bal or bet <= 0:
            return await interaction.response.send_message("❌ Invalid bet!", ephemeral=True)

        await interaction.response.send_message(embed=self.get_embed("🎡 Roulette", f"Betting {bet} on {number}... Spinning! 🎡"))
        
        for _ in range(5):
            await asyncio.sleep(0.4)
            await interaction.edit_original_response(embed=self.get_embed("🎡 Roulette", f"Spinning... {random.randint(0, 36)}"))

        final_num = random.randint(0, 36)
        if final_num == number:
            economy.update_balance(interaction.user.id, bet * 35)
            res = f"🎊 **JACKPOT!** The number was {final_num}!\nWon **{bet * 35}** coins!"
            color_embed = 0x00ff00
        else:
            economy.update_balance(interaction.user.id, -bet)
            res = f"💀 **LOSS!** The number was {final_num}.\nLost **{bet}** coins!"
            color_embed = 0xff0000

        await interaction.edit_original_response(embed=self.get_embed("🎡 Roulette", f"{res}\nBalance: **{get_balance(interaction.user.id)}**", color_embed))

    # --- BLACKJACK (BUTTONS) ---
    @app_commands.command(name="blackjack", description="Play 21!")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        bal = get_balance(interaction.user.id)
        if bet > bal or bet <= 0: return await interaction.response.send_message("❌ Invalid bet!", ephemeral=True)

        player = [random.randint(2, 11), random.randint(2, 11)]
        dealer = [random.randint(2, 11), random.randint(2, 11)]

        class BJView(discord.ui.View):
            def __init__(self, bot, user, bet, p_hand, d_hand):
                super().__init__(timeout=60)
                self.bot = bot
                self.user = user
                self.bet = bet
                self.p_hand = p_hand
                self.d_hand = d_hand

            @discord.ui.button(label="Hit 🃏", style=discord.ButtonStyle.green)
            async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != self.user: return await interaction.response.defer()
                self.p_hand.append(random.randint(2, 11))
                total = sum(self.p_hand)
                if total > 21:
                    update_balance(self.user.id, -self.bet)
                    await interaction.response.edit_message(content=f"💥 **BUST!** Total {total}. Lost **{self.bet}** coins.", embed=None, view=None)
                else:
                    await interaction.response.edit_message(content=f"🃏 Hand: `{self.p_hand}` (Total: {total})", view=self)

            @discord.ui.button(label="Stand ✋", style=discord.ButtonStyle.red)
            async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != self.user: return await interaction.response.defer()
                while sum(self.d_hand) < 17: self.d_hand.append(random.randint(2, 11))
                p_sum, d_sum = sum(self.p_hand), sum(self.d_hand)
                if d_sum > 21 or p_sum > d_sum:
                    update_balance(self.user.id, self.bet)
                    res = f"🎉 **WIN!** Dealer had {d_sum}."
                elif p_sum < d_sum:
                    update_balance(self.user.id, -self.bet)
                    res = f"💀 **LOSS!** Dealer had {d_sum}."
                else:
                    res = "🤝 **PUSH!** Tie."
                await interaction.response.edit_message(content=f"{res}\nFinal Hand: `{self.p_hand}`", embed=None, view=None)

        view = BJView(self.bot, interaction.user, bet, player, dealer)
        await interaction.response.send_message(f"🃏 **Blackjack!** Your hand: `{player}` (Total: {sum(player)})\nDealer shows: `{dealer[0]}`", view=view)

    # --- MINES (BUTTONS) ---
    @app_commands.command(name="mines", description="Reveal squares to win!")
    async def mines(self, interaction: discord.Interaction, bet: int, mine_count: int = 3):
        bal = get_balance(interaction.user.id)
        if bet > bal or bet <= 0: return await interaction.response.send_message("❌ Invalid bet!", ephemeral=True)
        if mine_count < 1 or mine_count > 24: return await interaction.response.send_message("❌ Mines must be 1-24!")

        grid = ["💎" for _ in range(25)]
        mine_indices = random.sample(range(25), mine_count)
        for i in mine_indices: grid[i] = "💣"

        class MinesView(discord.ui.View):
            def __init__(self, bot, user, bet, grid):
                super().__init__(timeout=60)
                self.bot = bot
                self.user = user
                self.bet = bet
                self.grid = grid
                self.revealed = 0

            async def update_msg(self, interaction):
                rows = [ " ".join(self.grid[i:i+5]) for i in range(0, 25, 5) ]
                msg = "\n".join(rows)
                await interaction.response.edit_message(content=f"💣 **Mines** | Revealed: {self.revealed}\n{msg}\nReact with 💰 to Cash Out!", view=self)

            @discord.ui.button(label="Cash Out 💰", style=discord.ButtonStyle.gold)
            async def cashout(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != self.user: return await interaction.response.defer()
                win = int(self.bet * (1 + (self.revealed * 0.2)))
                update_balance(self.user.id, win - self.bet)
                await interaction.response.edit_message(content=f"💰 **Cashed Out!** Won **{win}** coins!", embed=None, view=None)

        # Create 25 buttons for the grid
        view = MinesView(self.bot, interaction.user, bet, grid)
        for i in range(25):
            btn = discord.ui.Button(label="?", style=discord.ButtonStyle.gray)
            async def btn_callback(inter, b=btn, idx=i):
                if inter.user != view.user: return await inter.response.defer()
                if view.grid[idx] == "💣":
                    update_balance(view.user.id, -view.bet)
                    await inter.response.edit_message(content=f"💥 **BOOM!** You hit a mine! Lost **{view.bet}** coins.", view=None)
                else:
                    view.grid[idx] = "💎"
                    view.revealed += 1
                    await view.update_msg(inter)
            btn.callback = btn_callback
            view.add_item(btn)

        rows = [ " ".join(grid[i:i+5]) for i in range(0, 25, 5) ]
        await interaction.response.send_message(f"💣 **Mines** | Bet: {bet} | Mines: {mine_count}\n{'\n'.join(rows)}", view=view)

async def setup(bot):
    await bot.add_cog(Casino(bot))
