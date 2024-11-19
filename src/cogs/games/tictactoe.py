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
from uuid import uuid4


class TicTacToe(commands.Cog, name="tictactoe"):
    def __init__(self, bot):
        self.bot = bot
        self.games = []

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

        if tegenspeler.bot:
            return await interaction.response.send_message('Cannot play versus a bot!')
        
        # Create a new game
        new_game = GameSession(str(uuid4()), self)
        new_game.players = [interaction.user, tegenspeler]
    
        game_embed = new_game.get_updated_embed()

        # respond to interaction
        await interaction.response.send_message(embed=game_embed, view=ButtonGridView(new_game))
        new_game.response = interaction.response

        self.games.append(new_game)



class ButtonGridView(View):
    def __init__(self, game):
        super().__init__()

        self.game = game
        self.update_buttons()


    async def button_callback(self, interaction: discord.Interaction):
        _, row, col = interaction.data['custom_id'].split("_")

        # wrong user pressed the button
        if not self.game.play_move(int(row), int(col), interaction.user):
            # other players turn
            if interaction.user in self.game.players:
                return await interaction.response.send_message('Please wait until your opponent plays their move!', ephemeral=True)
            
            return await interaction.response.send_message('You are not playing this game, use /tictactoe to start your own!', ephemeral=True)

        self.update_buttons()
        embed = self.game.get_updated_embed()
        await interaction.response.edit_message(embed=embed, view=self)


    def update_buttons(self):
        self.clear_items()

        # Create a 3x3 grid of buttons
        for row in range(3):
            for col in range(3):
                disabled = self.game.board[row][col] is not None

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

class GameSession():
    def __init__(self, uuid, cog):
        self.uuid = uuid
        self.cog = cog
        self.response = None
        self.players = None
        self.current_turn = 0

        self.board = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ] 

    def get_updated_embed(self):
        brd = ''
        for row in self.board:
            emoji_row = ''
            for symbol in row:
                emoji_row += self.cog.emoji_conversion[symbol]

            brd += emoji_row + '\n'


        embed = embeds.DefaultEmbed(
            title = "TicTacToe",
            description = brd
        )

        return embed

    def play_move(self, row, col, user):
        if not user == self.players[self.current_turn]:
            return False
        
        self.board[row][col] = 'X' if self.current_turn == 0 else 'O'
        self.current_turn = 1 if self.current_turn == 0 else 0
        return True

async def setup(bot):
    await bot.add_cog(TicTacToe(bot))
