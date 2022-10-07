import discord
from discord.ext import commands
import json


class Settings(commands.Cog):  # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    # This command is to change settings of the server from the settings table of the database. It will have subcommands for each setting.
    @discord.slash_command()
    @commands.has_permissions(administrator=1)
    async def settings(self, ctx, setting: discord.Option(str, "Enter the setting you would like to change:", required=False), value: discord.Option(str, "Enter the value you would like to set the setting to:", required=False)):
        # If argument is not given, show all settings
        if setting is None:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM settings WHERE guild_id = ?", (ctx.guild.id,))
                result = await cursor.fetchone()
                if result is None:
                    # Set default settings
                    await cursor.execute("INSERT INTO settings VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (ctx.guild.id, 0, 0, 0, 0, 0, "", 0))
                    await self.bot.db.commit()
                    await ctx.respond("Serveri vaikimisi seaded on nüüd seadistatud. Jooksuta see käsk uuesti, et vaadata seadeid.")
                    return
                # Show all settings in one embed
                embed = discord.Embed(
                    title=f"{ctx.guild.name} seaded",
                    description=f"verification_category_id: {result[1]}\ncitizen_role_id: {result[2]}\nelections_channel_id: {result[3]}\nannouncements_channel_id: {result[4]}\nleader_role_id: {result[5]}\nleader_ideology: {result[6]} \nelections_message_id: {result[7]}",
                    color=discord.Color.blurple()
                )
                await ctx.respond(embed=embed)
        # If argument is given, show the setting
        elif setting and value is None:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM settings WHERE guild_id = ?", (ctx.guild.id,))
                result = await cursor.fetchone()
                if result is None:
                    # Set default settings
                    await cursor.execute("INSERT INTO settings VALUES (?, ?, ?, ?, ?, ?, ?)", (ctx.guild.id, 0, 0, 0, 0, 0, ""))
                    await self.bot.db.commit()
                    await ctx.respond("Serveri vaikimisi seaded on nüüd seadistatud. Jooksuta see käsk uuesti, et vaadata seadeid.")
                    return
                # Show the setting in one embed
                embed = discord.Embed(
                    title=f"{ctx.guild.name} seaded",
                    description=f"{setting}: {result[1]}",
                    color=discord.Color.blurple()
                )
                await ctx.respond(embed=embed)
        elif value and setting:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM settings WHERE guild_id = ?", (ctx.guild.id,))
                result = await cursor.fetchone()
                if result is None:
                    # Set default settings
                    await cursor.execute("INSERT INTO settings VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (ctx.guild.id, 0, 0, 0, 0, 0, "", 0))
                    await self.bot.db.commit()
                    await ctx.respond("Serveri vaikimisi seaded on nüüd seadistatud. Jooksuta see käsk uuesti, et vaadata seadeid.")
                    return
                # Set the setting to the value
                await cursor.execute(f"UPDATE settings SET {setting} = ? WHERE guild_id = ?", (value, ctx.guild.id))
                await self.bot.db.commit()
                await ctx.respond(f"{setting} on nüüd {value}.")

    @commands.command()
    @commands.has_permissions(administrator=1)
    async def defaults(self, ctx):
        # Set default settings to database, load them from config.json
        async with self.bot.db.cursor() as cursor:
            # Read config.json
            with open("config.json", "r") as f:
                config = json.load(f)
            # Get from config.json
            guild_id = config["guild_id"]
            verification_category_id = config["verification_category_id"]
            citizen_role_id = config["citizen_role_id"]
            elections_channel_id = config["elections_channel_id"]
            announcements_channel_id = config["announcements_channel_id"]
            leader_role_id = config["leader_role_id"]
            leader_ideology = config["leader_ideology"]
            elections_message_id = config["elections_message_id"]
            elections_button_message_id = config["elections_button_message_id"]
            # Set to database if it is not already set
            await cursor.execute("SELECT * FROM settings WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            if result is None:
                await cursor.execute("INSERT INTO settings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (guild_id, verification_category_id, citizen_role_id, elections_channel_id, announcements_channel_id, leader_role_id, leader_ideology, elections_message_id, elections_button_message_id))
            # Else update
            else:
                await cursor.execute("UPDATE settings SET guild_id = ?, verification_category_id = ?, citizen_role_id = ?, elections_channel_id = ?, announcements_channel_id = ?, leader_role_id = ?, leader_ideology = ?, elections_message_id = ? WHERE guild_id = ?", (guild_id, verification_category_id, citizen_role_id, elections_channel_id, announcements_channel_id, leader_role_id, leader_ideology, elections_message_id, guild_id))
            await self.bot.db.commit()
            await ctx.channel.send("Serveri vaikimisi seaded on nüüd seadistatud.")

    @commands.command()
    @commands.has_permissions(administrator=1)
    async def reset_settings(self, ctx):
        # Reset settings to default
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("DELETE FROM settings WHERE guild_id = ?", (ctx.guild.id,))
            await self.bot.db.commit()
            await ctx.channel.send("Serveri seaded on resetitud.")


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Settings(bot))  # add the cog to the bot
