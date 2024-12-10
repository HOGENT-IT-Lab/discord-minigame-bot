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
            None: "<:Transparant:1303307134326280284>",
            'X': "<:X1:1303307006924558376>",
            'O': "<:O1:1303306880642187264>",
        }

    @discord.app_commands.command(
        name="boter-kaas-eieren",
        description="Speel Boter-Kaas-Eieren",
    )
    @discord.app_commands.describe(tegenspeler="Tegen wie wil je spelen")
    async def tictactoe(self, interaction, tegenspeler: discord.Member) -> None:
        """Play tictactoe against another player

        Args:
            interaction (Interaction): Users Interaction
            tegenspeler (discord.User): Which user
        """

        if tegenspeler.bot:
            return await interaction.response.send_message('Je kan niet tegen een bot spelen!')
        
        # Create a new game
        new_game = GameSession(str(uuid4()), self)
        new_game.players = [interaction.user.id, tegenspeler.id]
    
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
            if interaction.user.id in self.game.players:
                return await interaction.response.send_message('Wacht tot uw tegenstander zijn zet speelt!', ephemeral=True)
            
            return await interaction.response.send_message('Je speelt dit spel niet, gebruik /boter-kaas-eieren om je eigen spel te starten!', ephemeral=True)

        self.update_buttons()
        embed = self.game.get_updated_embed()
        await interaction.response.edit_message(embed=embed, view=self)


    def update_buttons(self):
        self.clear_items()

        if self.game.ended: return

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
        self.ended = None

        self.board = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ] 

    def get_updated_embed(self):

        if self.ended:
            return embeds.DefaultEmbed(
                title = "Boter-Kaas-Eieren",
                description = self.ended
            )

        brd = ''
        for row in self.board:
            emoji_row = ''
            for symbol in row:
                emoji_row += self.cog.emoji_conversion[symbol]

            brd += emoji_row + '\n'


        embed = embeds.DefaultEmbed(
            title = "Boter-Kaas-Eieren",
            description = brd
        )

        return embed

    def play_move(self, row, col, user):

        if not user.id == self.players[self.current_turn]:
            return False
        
        self.board[row][col] = 'X' if self.current_turn == 0 else 'O'
        self.current_turn = 1 if self.current_turn == 0 else 0

        self.ended = self.check_victory()
        return True

    
    def check_victory(self):
        # Check rows for victory
        for row in self.board:
            if row[0] is not None and all(cell == row[0] for cell in row):
                return row[0]  # Return 'X' or 'O' as the winner

        # Check columns for victory
        for col in range(3):
            if self.board[0][col] is not None and all(self.board[row][col] == self.board[0][col] for row in range(3)):
                return self.board[0][col]  # Return 'X' or 'O' as the winner

        # Check diagonals for victory
        if self.board[0][0] is not None and all(self.board[i][i] == self.board[0][0] for i in range(3)):
            return self.board[0][0]  # Return 'X' or 'O' as the winner
        if self.board[0][2] is not None and all(self.board[i][2 - i] == self.board[0][2] for i in range(3)):
            return self.board[0][2]  # Return 'X' or 'O' as the winner

        # Check for draw (no empty cells left)
        if all(cell is not None for row in self.board for cell in row):
            return "Draw"

        # No winner or draw
        return None


async def setup(bot):
    await bot.add_cog(TicTacToe(bot))
