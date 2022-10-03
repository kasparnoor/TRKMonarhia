import discord
from discord.ext import commands
tries = 0

# create a class for our cog that inherits from commands.Cog


class Verifcation(commands.Cog):
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.slash_command()
    async def kinnita(self, ctx):
        await ctx.respond('Kirjuta minule privaatsõnum!')

    @commands.Cog.listener()  # we can add event listeners to our cog
    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        # Check if message author is self
        if ctx.author == self.bot.user:
            return
        if ctx.content == "Tere":
            # Check if message is in DMs
            if ctx.guild is None:
                await ctx.channel.send('Message author: ' + ctx.author.name)
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
                                await ctx.channel.send(
                                    "**Aitäh.**")
                                await ctx.channel.send(attachment.attachments[0].url)
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


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Verifcation(bot))  # add the cog to the bot
