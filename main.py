# Imports
import random
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow

# Local imports
from log_handling import *
from commands.help import _help


# Variables
TOKEN = "ODMxOTQ0NTIyNzQ4NTI2Njg0.YHcmtw.XfoMoovL5mkn8RZHvKlvhf9a-mU"
PREFIX = "."
DEBUG = True
LEVEL = "DEBUG"
COLOUR = 0xffc000


# Functions
def populate_actionrows(button_list):
    """Returns a list of actionrows of 5 or less buttons."""

    actionrow_list = []
    for x in range(ceil(len(buttons_list) / 5)):
        if len(buttons_list[(5 * x):]) > 5:
            actionrow_list.append(create_actionrow(*button_list[(5 * x):(5 * x) + 5]))
        else:
            actionrow_list.append(create_actionrow(*buttons[(5 * x):]))
    return actionrow_list


# Main code
if DEBUG is True:
	x = logging.StreamHandler()
	x.setLevel(LEVEL)
	logger.addHandler(x)

client = commands.Bot(command_prefix=PREFIX, help_command=None)

client.activity = discord.Activity(type=discord.ActivityType.listening, name="the rain")

@client.event
async def on_ready():
	logger.info(f"{client.user.name} is ready.")


guild_ids = []
for guild in client.guilds:
	guild_ids=guild_ids

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
		embed = discord.Embed(title="🤔 Need help?", description=f"Here's a list of {client.user.name}'s commands!", colour=COLOUR)
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
		await ctx.send(f"Pong! {round(client.latency * 1000)}ms")
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
		responses = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.", "Outlook not so good.", "Very doubtful."]
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
	] + [create_option(name="option " + str(x), description="1", option_type=3, required=False) for x in range(3, 10)],
	guild_ids=guild_ids
)
async def _poll(ctx, question, option1, option2, option3=None, option4=None, option5=None, option6=None, option7=None, option8=None, option9=None):
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

client.run(TOKEN)
