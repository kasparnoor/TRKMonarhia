import discord
from discord.ext import commands


# create a class for our cog that inherits from commands.Cog
class Verifcation(commands.Cog):
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    @discord.slash_command()
    async def kinnita(self, ctx):
        await ctx.respond('Kirjuta minule privaatsõnum!')

    @commands.Cog.listener()  # we can add event listeners to our cog
    async def on_message(self, message):
        if message.author.bot:
            return
        # Check if message is in DMs
        if message.guild is None:
            await message.channel.send(
                "**Tere!** Mina olen jumal. **Palun vastake `jah`, kui soovite jätkata.**")


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Verifcation(bot))  # add the cog to the bot
