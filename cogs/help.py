import discord
from discord.ext import commands


class Help(commands.Cog):  # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    @discord.slash_command()
    async def abi(self, ctx):
        await ctx.respond('Varsti tulemas!')

    # Custom help command
    class MyHelp(commands.HelpCommand):

        def get_command_signature(self, command):
            return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

        async def send_cog_help(self, cog):
            embed = discord.Embed(title=cog.qualified_name or "No Category",
                                  description=cog.description, color=discord.Color.blurple())

            if filtered_commands := await self.filter_commands(cog.get_commands()):
                for command in filtered_commands:
                    embed.add_field(name=self.get_command_signature(
                        command), value=command.help or "No Help Message Found... ")

            await self.get_destination().send(embed=embed)


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Help(bot))  # add the cog to the bot
