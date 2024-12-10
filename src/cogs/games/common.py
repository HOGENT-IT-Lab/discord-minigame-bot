import discord
from discord.ext import commands
from embeds import DefaultEmbed

class Common(commands.Cog, name="common"):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="games",
        description="Lijst van alle beschikbare games",
        extras={'list_in_games': False} # toont dat deze command geen game is
    )
    async def games(self, interaction: discord.Interaction):
        commands=[]
        for command in self.bot.tree.get_commands():
            if command.extras.get('list_in_games', True):
                commands.append(f"</{command.name}:{command.id}> - {command.description}")

        embed = DefaultEmbed(
            title="🎮 Beschikbare Games",
            description='\n'.join(commands),
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Common(bot))