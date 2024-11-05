""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

from discord.ext import commands


class VierOpEenRij(commands.Cog, name="vieropeenrij"):
    def __init__(self, bot):
        self.bot = bot

    #todo maak vier op een rij

async def setup(bot):
    await bot.add_cog(VierOpEenRij(bot))
