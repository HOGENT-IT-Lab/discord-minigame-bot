import discord
from discord.ext import commands

class Common(commands.Cog, name="common"):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="games",
        description="List all the available games",
        extras={'list_in_games': False} # toont dat deze command geen game is
    )
    async def games(self, interaction: discord.Interaction):
        commands=[]
        for command in self.bot.tree.get_commands():
            if command.extras.get('list_in_games', True):
                commands.append(f"</{command.name}:{command.id}> - {command.description}")

        embed = discord.Embed(
            title="🎮 Available Games",
            description='\n'.join(commands),
            color=discord.Color.blurple(),
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Common(bot))