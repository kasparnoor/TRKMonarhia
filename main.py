import discord
from discord.ext import commands
import os  # default module
from dotenv import load_dotenv
import aiosqlite

load_dotenv()  # load all the variables from the env file
bot = commands.Bot(command_prefix='!',
                   intents=discord.Intents.all())  # create a bot instance

cogs_list = [
    'help',
    'levels',
    'verification',
    'settings',
    'leader',
]

for cog in cogs_list:
    print(f'Loading {cog}...')
    bot.load_extension(f'cogs.{cog}')


# this is the event that runs when the bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    setattr(bot, 'db', await aiosqlite.connect('db/data.db'))
    async with bot.db.cursor() as cursor:
        await cursor.execute(
            "CREATE TABLE IF NOT EXISTS levels (user_id INTEGER, xp INTEGER, level INTEGER)")
        await cursor.execute(
            "CREATE TABLE IF NOT EXISTS verification (user_id INTEGER, channel_id INTEGER, verified BOOLEAN, name TEXT, birthdate TEXT, class TEXT)")
        await cursor.execute(
            "CREATE TABLE IF NOT EXISTS settings (guild_id INTEGER, verification_category_id INTEGER, citizen_role_id INTEGER, elections_channel_id INTEGER, announcements_channel_id INTEGER, leader_role_id INTEGER, leader_ideology TEXT, elections_message_id INTEGER, elections_buttons_message_id INTEGER)")
        # Elections table
        await cursor.execute(
            "CREATE TABLE IF NOT EXISTS elections (id INTEGER, embed TEXT)")
        await cursor.execute(
            "CREATE TABLE IF NOT EXISTS candidates (id INTEGER, user_id INTEGER, guild_id INTEGER, ideology TEXT, votes INTEGER)")
        await cursor.execute(
            "CREATE TABLE IF NOT EXISTS votes (id INTEGER, user_id INTEGER, candidate_id INTEGER)")
        await bot.db.commit()


# TO BE REWRITTEN
# Help command temporarily taken from the pycord docs
class SupremeHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Abi", color=discord.Color.blurple())
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            if command_signatures := [
                self.get_command_signature(c) for c in filtered
            ]:
                cog_name = getattr(cog, "qualified_name", "Puudub kategooria")
                embed.add_field(name=cog_name, value="\n".join(
                    command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(
            command), color=discord.Color.blurple())
        if command.help:
            embed.description = command.help
        if alias := command.aliases:
            embed.add_field(
                name="Aliased", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    # a helper function to add commands to an embed
    async def send_help_embed(self, title, description, commands):
        embed = discord.Embed(
            title=title, description=description or "Abi puudub...")

        if filtered_commands := await self.filter_commands(commands):
            for command in filtered_commands:
                embed.add_field(name=self.get_command_signature(
                    command), value=command.help or "Abi ei leitud...")

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        title = self.get_command_signature(group)
        await self.send_help_embed(title, group.help, group.commands)

    async def send_cog_help(self, cog):
        title = cog.qualified_name or "Ei"
        await self.send_help_embed(f'{title} Kategooria', cog.description, cog.get_commands())


bot.help_command = SupremeHelpCommand()

bot.run(os.getenv('TOKEN'))  # run the bot with the token
