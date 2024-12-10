import discord
from discord.ext import commands
from discord.ui import View, Button
from embeds import DefaultEmbed

class RockPaperScissors(commands.Cog, name="steenpapierschaar"):
    def __init__(self, bot):
        self.bot = bot
        self.choices = {
            "steen": "🪨",
            "papier": "📜",
            "schaar": "✂️",
        }

    @discord.app_commands.command(
        name="blad-steen-schaar",
        description="Speel blad-steen-schaar tegen een andere speler",
    )
    @discord.app_commands.describe(tegenspeler="Tegen wie wil je spelen")
    async def rps(self, interaction: discord.Interaction, tegenspeler: discord.Member):
        """Start a Blad-Steen-Schaar game."""

        if tegenspeler.bot:
            return await interaction.response.send_message('Je kan niet tegen een bot spelen!')

        # Create the game embed
        embed = DefaultEmbed(
            title="Blad-Steen-Schaar",
            description=f"{interaction.user.mention} daagt {tegenspeler.mention} uit voor een potje Blad-Steen-Schaar!",
        )
        embed.set_footer(text="Klik hieronder op jouw keuze om te spelen!")

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
        for name, emoji in [("steen", "🪨"), ("papier", "📜"), ("schaar", "✂️")]:
            button = Button(label=name.capitalize(), emoji=emoji, custom_id=name)
            button.callback = self.button_callback
            self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        # Ensure only the participants can play
        if interaction.user not in [self.player1, self.player2]:
            return await interaction.response.send_message(
                "Je speelt niet mee in dit spel!", ephemeral=True
            )

        # Record the player's choice
        self.choices[interaction.user] = interaction.data["custom_id"]

        # Check if both players have made their choice
        if len(self.choices) == 2:
            await self.process_results(interaction)
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} heeft gekozen! Aan het wachten op je tegenspeler...", ephemeral=True
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
        if winner == "Gelijkspel":
            result = "Het is gelijkspel! 🤝"
        elif winner == self.player1:
            result = f"{self.player1.mention} wint! 🎉"
        else:
            result = f"{self.player2.mention} wint! 🎉"

        # Send the results
        embed = DefaultEmbed(
            title="Blad-Steen-Schaar Resultaten",
            description=(
                f"{self.player1.mention} heeft {self.get_emoji(p1_choice)} gekozen\n"
                f"{self.player2.mention} heeft {self.get_emoji(p2_choice)} gekozen\n\n{result}"
            ),
        )
        await interaction.response.edit_message(embed=embed, view=PlayAgainView(self.player1, self.player2))

    def get_winner(self, p1, p2):
        """Determines the winner based on the game rules."""
        rules = {
            "steen": "schaar",
            "schaar": "papier",
            "papier": "steen",
        }
        if p1 == p2:
            return "draw"
        return self.player1 if rules[p1] == p2 else self.player2

    def get_emoji(self, choice):
        """Returns the emoji for a given choice."""
        return {"steen": "🪨", "papier": "📜", "schaar": "✂️"}.get(choice, "❓")

class PlayAgainView(View):
    def __init__(self, player1, player2):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        button = Button(label="Opnieuw spelen", style=discord.ButtonStyle.success, custom_id="play_again", emoji="🔄")
        button.callback = self.play_again
        self.add_item(button)

    async def play_again(self, interaction: discord.Interaction):
        if interaction.user not in [self.player1, self.player2]:
            return await interaction.response.send_message(
                "Je speelt niet mee in dit spel!", ephemeral=True
            )
        # Restart the game
        embed = DefaultEmbed(
            title="Blad-Steen-Schaar",
            description=f"{self.player1.mention} daagt {self.player2.mention} uit tot een nieuw spel Blad-Steen-Schaar!",
        )
        embed.set_footer(text="Klik hieronder op jouw keuze om te spelen!")
        await interaction.message.edit(embed=embed, view=RPSView(self.player1, self.player2))

async def setup(bot):
    await bot.add_cog(RockPaperScissors(bot))