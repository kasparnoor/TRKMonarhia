import discord
from discord.ext import commands
from discord.ext import tasks

import datetime as DT
import dateutil.relativedelta as REL


class Leader(commands.Cog):  # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot
        # Get context
        update.start()

    def cog_unload(self):
        update.cancel()

    # Elections are an event that happen every sunday at 18:30 GMT+2 Tallinn Time
    # The elections are held in the #valimised channel
    # The elections are held by the bot
    # Every verified user can vote for one leader
    # The leader with the most votes wins

    # Create embed that will show time until next elections, current leader, their ideology
    # and the number of votes they got

    def get_time_until_elections():
        # Get time until next sunday at 18:30 GMT+2 Tallinn Time
        today = DT.date.today()
        rd = REL.relativedelta(weekday=REL.SU)
        # Check if it's sunday
        if today.weekday() == 6:
            # Check if it's after 18:30
            if today.hour >= 18 and today.minute >= 30:
                # Add one week
                return("Eelmine valimine oli täna. Järgmine valimine on " + str(today + rd + DT.timedelta(days=7)))
            else:
                return("✅ Valimised on alanud!")
        else:
            return str(today + rd)

    # Create the elections info message
    embed = discord.Embed(
        title="Valimised" + " " + "🗳️",
        description="Igal kodanikul on kohustus valida. Kui rohkem kui 3 korda mitte valida, kaotab kodanik kodakondsuse ning peab kirjutama haiku. Tule valima!\n",
        color=discord.Color.dark_grey()
    )
    embed.set_footer(
        text="Valimised toimuvad iga nädal pühapäeval alates kella 00:00st. Võitja selgitatakse välja 18:30.")
    embed.add_field(name="Järgmine valimine toimub: ",
                    value=get_time_until_elections(), inline=False)

    global ButtonsView

    class ButtonsView(discord.ui.View):
        @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
            # the placeholder text that will be displayed if nothing is selected
            placeholder="Langeta oma valik!",
            min_values=1,  # the minimum number of values that must be selected by the users
            max_values=1,  # the maximum number of values that can be selected by the users
            options=[  # the list of options from which users can choose, a required field
                discord.SelectOption(
                    label="Vali kandidaat",
                    description="Vali oma lemmik",
                ),
                discord.SelectOption(
                    label="Kandideeri",
                    description="Kandideeri ja saa valituks",
                ),
            ]
        )
        # the function called when the user is done selecting options
        async def select_callback(self, select, interaction):
            await interaction.response.send_message(f"Awesome! I like {select.values[0]} too!")

    global update

    @tasks.loop(seconds=120)
    async def update(self):
        await update_embed(self)

    @update.before_loop
    async def before_update(self):
        print('waiting...')
        await self.bot.wait_until_ready()

    # Get elections message from the database
    # if there is no message, create one
    # if there is a message, edit it

    global update_embed

    async def update_embed(self):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM settings WHERE guild_id = ?", (self.bot.guilds[0].id,))
            result = await cursor.fetchone()
            if result is None:
                # Send the embed to elections channel
                print("No settings found")
            elif result[7] is None or result[7] == 0 or result[7] == "":
                # Send the embed to elections channel
                channel_id = result[3]
                channel = self.bot.get_channel(channel_id)
                msg = await channel.send(embed=self.embed)
                await cursor.execute("UPDATE settings SET elections_message_id = ? WHERE guild_id = ?", (msg.id, msg.guild.id))
                await self.bot.db.commit()
            elif result[7] is not None:
                # Already has a message
                # Update the message
                channel_id = result[3]
                channel = self.bot.get_channel(channel_id)
                try:
                    msg = await channel.fetch_message(result[7])
                    await msg.edit(embed=self.embed)
                except:
                    msg = await channel.send(embed=self.embed)
                    await cursor.execute("UPDATE settings SET elections_message_id = ? WHERE guild_id = ?", (msg.id, msg.guild.id))
                    await self.bot.db.commit()
                await msg.edit(embed=self.embed)
                await cursor.execute("UPDATE settings SET elections_message_id = ? WHERE guild_id = ?", (msg.id, msg.guild.id))
                await self.bot.db.commit()
        async with self.bot.db.cursor() as cursor:
            # Get the buttons message
            # If there is no message, create one
            # If there is a message, edit it
            # Get guild id
            await cursor.execute("SELECT * FROM settings WHERE guild_id = ?", (self.bot.guilds[0].id,))
            result = await cursor.fetchone()
            if result is None:
                print("No results found")
            elif result[8] is None or result[8] == 0 or result[8] == "":
                # Send the embed to elections channel
                channel_id = result[3]
                channel = self.bot.get_channel(channel_id)
                msg = await channel.send("Erinevad võimalused:", view=self.ButtonsView())
                await cursor.execute("UPDATE settings SET elections_buttons_message_id = ? WHERE guild_id = ?", (msg.id, msg.guild.id))
                await self.bot.db.commit()

            elif result[8] is not None:
                # Try to locate the message
                channel_id = result[3]
                channel = self.bot.get_channel(channel_id)
                try:
                    msg = await channel.fetch_message(result[8])
                    # Update the message
                    await msg.delete()
                    new_msg = await channel.send("Erinevad võimalused:", view=self.ButtonsView())
                    await cursor.execute("UPDATE settings SET elections_buttons_message_id = ? WHERE guild_id = ?", (new_msg.id, new_msg.guild.id))
                    await self.bot.db.commit()

                except:
                    msg = await channel.send("Erinevad võimalused:", view=ButtonsView())
                    await cursor.execute("UPDATE settings SET elections_buttons_message_id = ? WHERE guild_id = ?", (msg.id, msg.guild.id))
                    await self.bot.db.commit()

    @commands.slash_command()
    async def setup(self, ctx):
        await update_embed(self, ctx)
        await ctx.respond("Valimiste info on uuendatud!")


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Leader(bot))  # add the cog to the bot
