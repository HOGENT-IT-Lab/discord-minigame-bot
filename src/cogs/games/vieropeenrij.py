""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import discord
from discord.ext import commands
from discord.ui import View, Button
from uuid import uuid4

class ConnectFour(commands.Cog, name="connectfour"):
    def __init__(self, bot):
        self.bot = bot
        self.games = []

        self.emoji_conversion = {
            None: ":black_large_square:",
            'Red': ":red_circle:",
            'Yellow': ":yellow_circle:",
        }

    @discord.app_commands.command(
        name="connectfour",
        description="Play Connect Four",
    )
    @discord.app_commands.describe(tegenspeler="Tegen wie wil je spelen")
    async def connectfour(self, interaction, tegenspeler: discord.Member) -> None:
        """Start a Connect Four game."""

        if tegenspeler.bot:
            return await interaction.response.send_message('Cannot play versus a bot!')
        
        # Create a new game
        new_game = GameSession(str(uuid4()), self)
        new_game.players = [interaction.user.id, tegenspeler.id]
    
        game_embed = new_game.get_updated_embed()

        await interaction.response.send_message(embed=game_embed, view=ColumnView(new_game))
        new_game.response = interaction.response

        self.games.append(new_game)

class ColumnView(View):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.update_buttons()

    async def button_callback(self, interaction: discord.Interaction):
        _, col = interaction.data['custom_id'].split("_")

        if not self.game.play_move(int(col), interaction.user):
            if interaction.user.id in self.game.players:
                return await interaction.response.send_message('Please wait for your turn!', ephemeral=True)
            
            return await interaction.response.send_message('You are not part of this game. Start your own with /connectfour!', ephemeral=True)

        self.update_buttons()
        embed = self.game.get_updated_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def update_buttons(self):
        self.clear_items()
        if self.game.ended:
            return

        for col in range(7):
            disabled = self.game.column_full(col)

            button = Button(
                label=str(col + 1),
                style=discord.ButtonStyle.primary,
                custom_id=f"button_{col}",
                disabled=disabled,
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
        self.ended = None

        self.board = [[None for _ in range(7)] for _ in range(6)]

    def get_updated_embed(self):
        if self.ended:
            return discord.Embed(
                title="Connect Four",
                description=self.ended
            )

        brd = ''
        for row in self.board:
            brd += ''.join(self.cog.emoji_conversion[cell] for cell in row) + '\n'

        embed = discord.Embed(
            title="Connect Four",
            description=brd
        )
        return embed

    def play_move(self, col, user):
        if user.id != self.players[self.current_turn]:
            return False

        for row in reversed(self.board):
            if row[col] is None:
                row[col] = 'Red' if self.current_turn == 0 else 'Yellow'
                break
        else:
            return False  # Column is full

        self.current_turn = 1 if self.current_turn == 0 else 0
        self.ended = self.check_victory()
        return True

    def column_full(self, col):
        return all(row[col] is not None for row in self.board)

    def check_victory(self):
        def check_line(line):
            for i in range(len(line) - 3):
                if line[i] is not None and line[i:i+4] == [line[i]] * 4:
                    return line[i]
            return None

        # Check rows
        for row in self.board:
            if winner := check_line(row):
                return f"{winner} wins!"

        # Check columns
        for col in range(7):
            column = [self.board[row][col] for row in range(6)]
            if winner := check_line(column):
                return f"{winner} wins!"

        # Check diagonals
        for row in range(3):
            for col in range(7 - 3):
                diagonal_down = [self.board[row + i][col + i] for i in range(4)]
                diagonal_up = [self.board[row + 3 - i][col + i] for i in range(4)]
                if winner := check_line(diagonal_down) or check_line(diagonal_up):
                    return f"{winner} wins!"

        # Check draw
        if all(cell is not None for row in self.board for cell in row):
            return "It's a draw!"

        return None

async def setup(bot):
    await bot.add_cog(ConnectFour(bot))
