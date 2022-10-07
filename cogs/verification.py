import re
import discord
from discord.ext import commands
import json
tries = 0
# Get config from config.json
with open("config.json", "r") as f:
    config = json.load(f)


class InfoModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="Täisnimi",
                placeholder="John Doe",
            ),
            discord.ui.InputText(
                label="Sünnikuupäev (järjekord: päev, kuu, aasta)",
                placeholder="06.12.2007",
            ),
            discord.ui.InputText(
                label="Klass",
                placeholder="9C",
            ),

            *args,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction):
        global results
        results = [self.children[0].value,
                   self.children[1].value, self.children[2].value]
        await check(results, interaction)


class Verification(commands.Cog):
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.slash_command()
    @commands.has_permissions(manage_roles=1)
    async def kinnita(self, ctx: discord.ApplicationContext, member: discord.Option(discord.Member)):
        # Check if the user is already verified
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM verification WHERE user_id = ?", (member.id,))
            result = await cursor.fetchone()
            if result[2] == 1:
                await ctx.respond("Tema on juba kodanik!")
                return
        citizen_role = ctx.guild.get_role(config["citizen_role_id"])
        await member.add_roles(citizen_role)
        # Create modal that asks for name and birthdate
        modal = InfoModal(title="Kodaniku kinnitamine")
        await ctx.send_modal(modal)
        global check

        async def check(results, interaction):
            # Check if the name is valid
            if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", results[0]):
                # Check if the birthdate is valid
                if re.match(r"^[0-9]{2}\.[0-9]{2}\.[0-9]{4}$", results[1]):
                    # Check if the class is valid
                    if re.match(r"^[0-9][A-C]$", results[2]):
                        async with self.bot.db.cursor() as cursor:
                            result = await cursor.fetchone()
                            await cursor.execute("UPDATE verification SET name = ?, birthdate = ?, class = ?, verified = ?, channel_id = ? WHERE user_id = ?", (results[0], results[1], results[2], 1, 0, member.id))
                            await self.bot.db.commit()
                        # Send a message to the user
                        await interaction.response.send_message("Kinnitatud.")
                        await member.send("Tere, sinu kinnitamine õnnestus!")
                        # Delete the channel
                        await interaction.channel.delete()

                    else:
                        await interaction.response.send_message("Viga! Palun sisesta klass õiges vormingus!")
                else:
                    await interaction.response.send_message("Viga! Palun sisesta sünnikuupäev õiges vormingus!")
            else:
                await interaction.response.send_message("Viga! Palun sisesta täisnimi õiges vormingus!")

    @commands.slash_command()
    @commands.has_permissions(manage_roles=1)
    async def eemalda(self, ctx: discord.ApplicationContext, member: discord.Option(discord.Member)):
        # Check if the user is already verified
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM verification WHERE user_id = ?", (member.id,))
            result = await cursor.fetchone()
            if result[2] == 1:
                # Remove the citizen role
                citizen_role = ctx.guild.get_role(config["citizen_role_id"])
                await member.remove_roles(citizen_role)
                # Update the database
                await cursor.execute("UPDATE verification SET verified = ? WHERE user_id = ?", (0, member.id))
                await self.bot.db.commit()
                # Set channel to 0
                await cursor.execute("UPDATE verification SET channel_id = ? WHERE user_id = ?", (0, member.id))
                await self.bot.db.commit()
                await ctx.respond("Kodaniku roll eemaldatud.")
            else:
                await ctx.respond("Tema pole veel kodanik!")
                return

    @commands.slash_command()
    @commands.has_permissions(manage_roles=1)
    async def reset_users(self, ctx: discord.ApplicationContext):
        # Delete verification table
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("DROP TABLE verification")
            await self.bot.db.commit()
            # Restart bot
            await ctx.respond("Kasutajad on resetitud.")
            await self.bot.close()

    @ commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        # Check if message author is self
        if ctx.author == self.bot.user:
            return
        if ctx.content == "Tere":
            # Check if message is in DMs
            if ctx.guild is None:
                # Check if user is already verified
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute(
                        "SELECT * FROM verification WHERE user_id = ?", (ctx.author.id,))
                    result = await cursor.fetchone()
                    # Check if name is ""
                    if result:
                        if result[1] > 0:
                            await ctx.reply("Palun oota, kuni administraatorid sind kinnitavad.")
                            return

                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT * FROM verification WHERE user_id = ?", (ctx.author.id,))
                    result = await cursor.fetchone()
                    if result is None or result[2] == 0:
                        # Check if the users channel id is more than 1 is already in progress

                        await ctx.channel.send(
                            "**Tere!** Mina olen jumal. **Palun vastake `jah`, kui soovite saada kodanikuks.**")
                        reply = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if reply.content == "jah":

                            async def jah():
                                await ctx.channel.send(
                                    "Palun **saatke pilt** oma Tallinna Reaalkooli **õpilaspiletist**. Võite oma isikukoodi ära blurrida, kui soovite.")
                                # Wait for attachment
                                attachment = await self.bot.wait_for('message', check=lambda message: ctx.author == message.author)
                                # Check if it is an attachment
                                if attachment.attachments:
                                    # Check if it is an image
                                    if attachment.attachments[0].filename.endswith('.png') or attachment.attachments[0].filename.endswith('.jpg') or attachment.attachments[0].filename.endswith('.jpeg'):
                                        # Create channel for verification in verification category which id is in config.json, also get guild from config.json
                                        guild = self.bot.get_guild(
                                            config["guild_id"])
                                        category = self.bot.get_channel(
                                            config["verification_category_id"])
                                        channel = await guild.create_text_channel(
                                            name=ctx.author.name + "-verification",
                                            category=category,
                                            reason="Verification channel created")

                                        # Send attachment to verification channel
                                        await channel.send(
                                            "Kasutaja: " + ctx.author.name + "#" + ctx.author.discriminator)
                                        await channel.send(
                                            "Kasutaja ID: " + str(ctx.author.id))  # Send user id
                                        await channel.send(
                                            "Õpilaspilet: " + str(attachment.attachments[0].url))  # Send user attachment url

                                        async with self.bot.db.cursor() as cursor:
                                            await cursor.execute("SELECT * FROM verification WHERE user_id = ?", (ctx.author.id,))
                                            result = await cursor.fetchone()
                                            await cursor.execute("INSERT INTO verification VALUES (?, ?, ?, ?, ?, ?)", (ctx.author.id, channel.id, 0, "", "", ""))
                                            await self.bot.db.commit()
                                        await ctx.channel.send(
                                            "**Aitäh.** Teile avati eraldi kanal: " + channel.mention + ".**")

                                    else:
                                        await ctx.channel.send(
                                            "Pilt peab olema kas **png**, **jpg** või **jpeg formaadis**. **Alustage** protsessi **uuesti** mulle kirjutades.**")
                                else:
                                    global tries
                                    tries += 1
                                    tries_left = str(3 - tries)
                                    if tries == 3:
                                        await ctx.channel.send(
                                            "**Alustage protsessi uuesti.**")
                                        return
                                    else:
                                        await ctx.channel.send(
                                            "**Sõnumis**, mis te saatsite **ei** ole ühtegi **attachmenti**, teil on " + tries_left + " **katset veel. Peale seda peate protsessi uuesti alustama.**")
                                        await jah()

                            await jah()
                        else:  # If reply is not "jah"
                            await ctx.channel.send(
                                "**Okei, kahju. Kas te teadsite, et 98% lahedatest inimestest on juba kodanikud? Ja sina kindlasti seal 2% seas ei ole.**")
                    elif result is not None:
                        await ctx.channel.send(
                            "**Olete juba kodanik.**")


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Verification(bot))  # add the cog to the bot
