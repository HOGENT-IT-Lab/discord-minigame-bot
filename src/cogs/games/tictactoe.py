""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""
import discord
import embeds

from discord.ext import commands
from discord.ui import View, Button


class TicTacToe(commands.Cog, name="tictactoe"):
    def __init__(self, bot):
        self.bot = bot

        self.board = [['X', None, 'X']*3] 
        # self.emoji_conversion = {
        #     'None': str(PartialEmoji(name="empty", id=1234567890)),
        #     'X': str(PartialEmoji(name="nerd", id=1300766941828481025)),
        #     'O': str(PartialEmoji(name="nerd", id=1300766941828481025)),
        # }
        self.emoji_conversion = {
            None: ":black_large_square:",
            'X': ":x:",
            'O': ":o:",
        }

    @discord.app_commands.command(
        name="tictactoe",
        description="Play the tictactoe game",
    )
    @discord.app_commands.describe(tegenspeler="Tegen wie wil je spelen")
    async def tictactoe(self, interaction, tegenspeler: discord.Member) -> None:
        """Play tictactoe against another player

        Args:
            interaction (Interaction): Users Interaction
            tegenspeler (discord.User): Which user
        """
        game_embed = self.update_board_in_embed()

        # respond to interaction
        await interaction.response.send_message(embed=game_embed, view=ButtonGridView())

    
    def update_board_in_embed(self):
        rows = []
        for row in self.board:
            emoji_row = ''
            for symbol in row:
                emoji_row += self.emoji_conversion[symbol]

            rows.append(emoji_row)

        return embeds.DefaultEmbed(
            title = "TicTacToe",
            description = '\n'.join(rows)
        )

class ButtonGridView(View):
    def __init__(self):
        super().__init__()
        
        # Create a 3x3 grid of buttons
        for row in range(3):
            for col in range(3):
                button = Button(label=f"{row * 3 + col + 1}", style=discord.ButtonStyle.primary, row=row)
                button.callback = self.button_callback

                self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You clicked button {interaction.data['custom_id']}!")



async def setup(bot):
    await bot.add_cog(TicTacToe(bot))
