import discord
from discord.ext import commands
from discord.ui import View, Button
from random import choice

class RockPaperScissors(commands.Cog, name="rockpaperscissors"):
    def __init__(self, bot):
        self.bot = bot
        self.choices = {
            "rock": "🪨",
            "paper": "📜",
            "scissors": "✂️",
        }

    @discord.app_commands.command(
        name="rps",
        description="Play Rock-Paper-Scissors against another user",
    )
    @discord.app_commands.describe(tegenspeler="Tegen wie wil je spelen")
    async def rps(self, interaction: discord.Interaction, tegenspeler: discord.Member):
        """Start a Rock-Paper-Scissors game."""

        if tegenspeler.bot:
            return await interaction.response.send_message('Cannot play against a bot!')

        # Create the game embed
        embed = discord.Embed(
            title="Rock-Paper-Scissors",
            description=f"{interaction.user.mention} challenges {tegenspeler.mention} to a game of Rock-Paper-Scissors!",
            color=discord.Color.blurple(),
        )
        embed.set_footer(text="Click your choice below to play!")

        # Start the game with a custom view
        await interaction.response.send_message(embed=embed, view=RPSView(interaction.user, tegenspeler))

class RPSView(View):
    def __init__(self, player1, player2):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        self.choices = {}
        self.add_buttons()

    def add_buttons(self):
        for name, emoji in [("rock", "🪨"), ("paper", "📜"), ("scissors", "✂️")]:
            button = Button(label=name.capitalize(), emoji=emoji, custom_id=name)
            button.callback = self.button_callback
            self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        # Ensure only the participants can play
        if interaction.user not in [self.player1, self.player2]:
            return await interaction.response.send_message(
                "You're not a participant in this game!", ephemeral=True
            )

        # Record the player's choice
        self.choices[interaction.user] = interaction.data["custom_id"]

        # Check if both players have made their choice
        if len(self.choices) == 2:
            await self.process_results(interaction)
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} has chosen! Waiting for the other player...", ephemeral=True
            )

    async def process_results(self, interaction: discord.Interaction):
        # Disable buttons after the game is decided
        for child in self.children:
            child.disabled = True

        # Get the choices
        p1_choice = self.choices[self.player1]
        p2_choice = self.choices[self.player2]

        # Determine the winner
        winner = self.get_winner(p1_choice, p2_choice)
        if winner == "draw":
            result = "It's a draw! 🤝"
        elif winner == self.player1:
            result = f"{self.player1.mention} wins! 🎉"
        else:
            result = f"{self.player2.mention} wins! 🎉"

        # Send the results
        embed = discord.Embed(
            title="Rock-Paper-Scissors Results",
            description=(
                f"{self.player1.mention} chose {self.get_emoji(p1_choice)}\n"
                f"{self.player2.mention} chose {self.get_emoji(p2_choice)}\n\n{result}"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed, view=PlayAgainView(self.player1, self.player2))

    def get_winner(self, p1, p2):
        """Determines the winner based on the game rules."""
        rules = {
            "rock": "scissors",
            "scissors": "paper",
            "paper": "rock",
        }
        if p1 == p2:
            return "draw"
        return self.player1 if rules[p1] == p2 else self.player2

    def get_emoji(self, choice):
        """Returns the emoji for a given choice."""
        return {"rock": "🪨", "paper": "📜", "scissors": "✂️"}.get(choice, "❓")

class PlayAgainView(View):
    def __init__(self, player1, player2):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        button = Button(label="Play Again", style=discord.ButtonStyle.success, custom_id="play_again", emoji="🔄")
        button.callback = self.play_again
        self.add_item(button)

    async def play_again(self, interaction: discord.Interaction):
        if interaction.user not in [self.player1, self.player2]:
            return await interaction.response.send_message(
                "You're not a participant in this game!", ephemeral=True
            )
        # Restart the game
        embed = discord.Embed(
            title="Rock-Paper-Scissors",
            description=f"{self.player1.mention} challenges {self.player2.mention} to another round of Rock-Paper-Scissors!",
            color=discord.Color.blurple(),
        )
        embed.set_footer(text="Click your choice below to play!")
        await interaction.message.edit(embed=embed, view=RPSView(self.player1, self.player2))

async def setup(bot):
    await bot.add_cog(RockPaperScissors(bot))