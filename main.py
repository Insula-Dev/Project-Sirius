# Imports
from math import ceil
import random
from os import path
import json

# Discord specific imports
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow, ButtonStyle

# Local imports
from log_handling import *

# from commands.help import _help


# Variables

TOKEN = ""
PREFIX = "-"
DEBUG = True
LEVEL = "DEBUG"
COLOUR = 0xffc000
JOKE_SERVERS = []


def update_config():
    with open("config.json", "w", encoding='utf-8') as file:
        json.dump(
            {
                "token": TOKEN,
                "prefix": PREFIX,
                "debug": DEBUG,
                "level": LEVEL,
                "joke servers": JOKE_SERVERS
            },
            file, indent=4)


def setup_config():
    global TOKEN, PREFIX, DEBUG, LEVEL, JOKE_SERVERS

    def initiate_const(name, default, dictionary):
        """Returns value if found in the dictionary, else makes new entry with default value first"""
        if name not in dictionary:
            dictionary[name] = default
        return dictionary[name]

    if not path.exists("config.json"):
        update_config()
    else:
        with open("config.json", encoding='utf-8') as file:
            config = json.load(file)
            TOKEN = initiate_const("token", TOKEN, config)
            PREFIX = initiate_const("prefix", PREFIX, config)
            DEBUG = initiate_const("debug", DEBUG, config)
            LEVEL = initiate_const("level", LEVEL, config)
            JOKE_SERVERS = initiate_const("joke servers", JOKE_SERVERS, config)
        update_config()
        print(config)

setup_config()


# Functions
def populate_actionrows(button_list):
    """Returns a list of actionrows of 5 or less buttons."""

    actionrow_list = []
    for x in range(ceil(len(button_list) / 5)):
        if len(button_list[(5 * x):]) > 5:
            actionrow_list.append(create_actionrow(*button_list[(5 * x):(5 * x) + 5]))
        else:
            actionrow_list.append(create_actionrow(*button_list[(5 * x):]))
    return actionrow_list


# Main code
if DEBUG is True:
    x = logging.StreamHandler()
    x.setLevel(LEVEL)
    logger.addHandler(x)

bot = commands.Bot(command_prefix=PREFIX, help_command=None)
slash = SlashCommand(bot, sync_commands=True)

bot.activity = discord.Activity(type=discord.ActivityType.listening, name="the rain")


@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} is ready.")


guild_ids = []
for guild in bot.guilds:
    guild_ids = guild_ids


@slash.slash(
    name="help",
    description="...",
    options=[
        create_option(
            name="command",
            description="...",
            option_type=3,
            required=False
        )
    ],
    guild_ids=guild_ids
)
async def _help(ctx, question=None):
    logger.debug(f"`{PREFIX}help` called by {ctx.author.name}")
    try:
        if question is not None:
            embed = discord.Embed(title="🤔 Need help?", description=f"Here's a list of {bot.user.name}'s commands!",
                                  colour=COLOUR)
            embed.add_field(name="__help__", value="...")
            await ctx.send(embed=embed)
    except Exception as exception:
        logger.error(f"Failed to run `{PREFIX}help` in {ctx.guild.name} ({ctx.guild.id})")


@slash.slash(
    name="ping",
    description="...",
    guild_ids=guild_ids
)
async def _ping(ctx):
    logger.debug(f"`{PREFIX}ping` called by {ctx.author.name}")
    try:
        await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")
    except Exception as exception:
        logger.error(f"Failed to run `{PREFIX}ping` in {ctx.guild.name} ({ctx.guild.id})")


@slash.slash(
    name="8ball",
    description="...",
    options=[
        create_option(
            name="question",
            description="...",
            option_type=3,
            required=True
        )
    ],
    guild_ids=guild_ids
)
async def _8ball(ctx, question):
    logger.debug(f"`{PREFIX}eightball` called by {ctx.author.name}")
    try:
        responses = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.",
                     "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.",
                     "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
                     "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
                     "Outlook not so good.", "Very doubtful."]
        await ctx.reply(random.choice(responses))
    except Exception as exception:
        logger.error(f"Failed to run `{PREFIX}eightball` in {ctx.guild.name} ({ctx.guild.id})")


@slash.slash(
    name="poll",
    description="description",
    options=[
                create_option(
                    name="question",
                    description="The poll's question",
                    option_type=3,
                    required=True
                ),
                create_option(
                    name="option 1",
                    description="...",
                    option_type=3,
                    required=True
                ),
                create_option(
                    name="option 2",
                    description="...",
                    option_type=3,
                    required=True
                )
            ] + [create_option(name="option " + str(x), description="1", option_type=3, required=False) for x in
                 range(3, 10)],
    guild_ids=guild_ids
)
async def _poll(ctx, question, option1, option2, option3=None, option4=None, option5=None, option6=None, option7=None,
                option8=None, option9=None):
    logger.debug(f"`/poll` called by {ctx.author.name}")

    try:
        embed = discord.Embed(title=question, description="...")
        message = await ctx.send(embed=embed)
        options = list(filter(None, [option1, option2, option3, option4, option5, option6, option7, option8, option9]))
        buttons = []
        for x in range(len(options)):
            buttons.append(create_button(style=ButtonStyle.blue, label=options[x], custom_id=str(x)))
        for x in range(len(options) % 5):

            """Create buttons here"""

            action_row = create_actionrow(*buttons())

            for i in range(len()):
                buttons.append(create_button(style=ButtonStyle.blue, label=options[x], custom_id="poll:" + str(x)))
        components = [create_actionrow(*buttons)]
    except Exception as exception:
        logger.error(f"Failed to run `/poll` in {ctx.guild.name} ({ctx.guild.id})")


@slash.slash(
    name="kill",
    description="Kills the bot",
    guild_ids=guild_ids
)
async def _kill(ctx):
    logger.debug(f"`{PREFIX}kill` called by {ctx.author.name}")
    try:
        bot.close()
    except Exception as exception:
        logger.error(f"Failed to `{PREFIX}kill` in {ctx.guild.name} ({ctx.guild.id})")


bot.run(TOKEN)
