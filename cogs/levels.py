import discord
from discord.ext import commands
import aiosqlite
from easy_pil import *


class Levels(commands.Cog):  # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    @discord.slash_command()
    async def level(self, ctx):
        # Command to check your level
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM levels WHERE user_id = ?", (ctx.author.id,))
            result = await cursor.fetchone()
            if result is None:
                await cursor.execute("INSERT INTO levels VALUES (?, ?, ?)", (ctx.author.id, 0, 0))
                await self.bot.db.commit()
                # Embed
                embed = discord.Embed(
                    title=f"{ctx.author.name}'i level",
                    description=f"Sa oled level 0",
                    color=discord.Color.blurple()
                )
                await ctx.respond(embed=embed)
            else:
                # Embed
                embed = discord.Embed(
                    title=f"{ctx.author.name}'i level",
                    description=f"Level: {result[2]}\nXP: {result[1]}",
                    color=discord.Color.blurple()
                )
                await ctx.respond(embed=embed)

    @commands.Cog.listener()  # we can add event listeners to our cog
    async def on_message(self, message):
        if message.author.bot:
            return

        # Cooldown for 5 seconds

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM levels WHERE user_id = ?", (message.author.id,))
            result = await cursor.fetchone()
            if result is None:
                await cursor.execute("INSERT INTO levels VALUES (?, ?, ?)", (message.author.id, 1, 0))
            else:
                await cursor.execute("UPDATE levels SET xp = ? WHERE user_id = ?", (result[1] + 1, message.author.id))
                await self.bot.db.commit()
                level = int(result[1] ** (1 / 4))
                if level > result[2]:
                    embed = discord.Embed(
                        title=f"{message.author.name} on nüüd level {level}!",
                        description=f"Palju õnne!",
                        color=discord.Color.blurple()
                    )
                    await message.channel.send(embed=embed)
                    await cursor.execute("UPDATE levels SET level = ? WHERE user_id = ?", (level, message.author.id))


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Levels(bot))  # add the cog to the bot
