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
        self.response = None
        self.players = None
        self.current_turn = 0

        self.board = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ] 
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

        self.players = [interaction.user, tegenspeler]
        game_embed = self.get_updated_embed()

        # respond to interaction
        await interaction.response.send_message(embed=game_embed, view=ButtonGridView(self))
        self.response = interaction.response

    
    def get_updated_embed(self):
        brd = ''
        for row in self.board:
            emoji_row = ''
            for symbol in row:
                emoji_row += self.emoji_conversion[symbol]

            brd += emoji_row + '\n'


        return embeds.DefaultEmbed(
            title = "TicTacToe",
            description = brd
        )
    
    def play_move(self, row, col, user):
        if not user == self.players[self.current_turn]:
            return False
        
        self.board[row][col] = 'X' if self.current_turn == 0 else 'O'
        self.current_turn = 1 if self.current_turn == 0 else 0
        return True


class ButtonGridView(View):
    def __init__(self, cog):
        super().__init__()

        self.cog = cog
        self.update_buttons()


    async def button_callback(self, interaction: discord.Interaction):
        _, row, col = interaction.data['custom_id'].split("_")

        # wrong user pressed the button
        if not self.cog.play_move(int(row), int(col), interaction.user):
            # TODO check if wrong turn
            return await interaction.response.send_message('You are not playing this game, use /tictactoe to start your own!')

        self.update_buttons()
        embed = self.cog.get_updated_embed()
        await interaction.response.edit_message(embed=embed, view=self)


    def update_buttons(self):
        self.clear_items()

        # Create a 3x3 grid of buttons
        for row in range(3):
            for col in range(3):
                disabled = self.cog.board[row][col] is not None

                custom_id = f"button_{row}_{col}"

                button = Button(
                    label=f"{row * 3 + col + 1}", 
                    style=discord.ButtonStyle.primary, 
                    row=row, 
                    disabled=disabled, 
                    custom_id=custom_id,
                )
                button.callback = self.button_callback

                self.add_item(button)



async def setup(bot):
    await bot.add_cog(TicTacToe(bot))
