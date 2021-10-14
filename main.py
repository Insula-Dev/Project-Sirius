# Imports
import time
import json
import socket
import re
import requests
from math import ceil
from random import randint
from datetime import date, datetime
# Discord imports
import discord
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
# Experimental imports
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle


# Local imports
from log_handling import *
from imaging import generate_level_card


# Variables
START_TIME = datetime.now()
try:
	with open("data.json", encoding="utf-8") as file:
		data = json.load(file)
	logger.debug("Loaded data.json")
except Exception as exception:
	logger.critical("Failed to load data.json. Exception: " + str(exception))
cache = {}
poll = {}
connected = False
purge_messages = {}
SERVER_STRUCTURE = {
	"config": {
		"level system": False,
		"admin role id": 0,
		"announcements channel id": None
	},
	"rules": {
		"title": "Server rules",
		"description": "",
		"list": [],
		"image link": ""
	},
	"roles": {
		"CATEGORY NAME": {
			"message id": 0,
			"list": {}
		}
	},
	"levels": {}
}
DEBUG = True
LEVEL = "DEBUG"
# For debugging purposes, prints logs at and above a certain level to the console
if DEBUG is True:
	x = logging.StreamHandler()  # Create new handler
	x.setLevel(LEVEL)  # Set handler level
	logger.addHandler(x)  # Add handler to logger
command_data = {
	"ping": {
		"description": "Pings the bot, checking latency."
	},
	"help": {
		"description": "Displays help information."
	},
	"embed": {
		"description": "Sends a custom-made embed."
	},
	"level": {
		"description": "Sends the user's level card, showing their current level and their progress to the next level."
	},
	"leaderboard": {
		"description": "Sends the level leaderboard, showing everybody's position in the server."
	},
	"stats": {
		"description": "Sends the server's stats embed. Admin only feature."
	},
	"rules": {
		"description": "Sends the server's rules embed. Admin only feature."
	},
	"roles": {
		"description": "Sends the server's roles embed. Admin only feature."
	},
	"cls": {
		"description": "Purges five messages from the channel. Admin only feature."
	},
	"status": {
		"description": "Reports the status of the current instance. Developer only feature."
	},
	"kill": {
		"description": "Kills the current instance. Developer only feature."
	}
}
#commands = {
#	"ping": {
#		"description": "Engage in a ruthless game of table tennis."
#		},
#	"help": {
#		"command description": "Sends the bot's help embed, listing the bot's commands.",
#		"options": {
#			"command": {
#				"option description": ""
#				"values": [
#					"ping",
#					"help"
#				]
#				}
#			}
#		},
#	"embed"
#}


# Functions
def update_data():
	"""Writes the updated data variable to the file."""

	try:
		with open("data.json", "w", encoding='utf-8') as file:
			json.dump(data, file, indent=4)
		logger.debug("Updated data")
	except Exception as exception:
		logger.error("Failed to update data. Exception: " + str(exception))

def initialise_guild(guild):
	"""Initialises data for a new guild."""

	try:
		data["servers"][str(guild.id)] = SERVER_STRUCTURE
		cache[str(guild.id)] = {}
		poll[str(guild.id)] = {}

		# Write the updated data
		logger.debug("Initialised guild " + guild.name + " (" + str(guild.id) + ")")
		update_data()
	except Exception as exception:
		logger.error("Failed to initialise guild " + guild.name + " (" + str(guild.id) + "). Exception: " + str(exception))

def get_uptime():
	"""Returns instance uptime."""

	try:
		seconds = round((datetime.now() - START_TIME).total_seconds())
		uptime = ""
		if seconds >= 3600:
			uptime += str(seconds // 3600) + " "
			if seconds // 3600 == 1:
				uptime += "hour"
			else:
				uptime += "hours"
		if seconds % 3600 >= 60:
			if uptime != "":
				uptime += " "
			uptime += str(seconds % 3600 // 60) + " "
			if seconds % 3600 // 60 == 1:
				uptime += "minute"
			else:
				uptime += "minutes"
		if seconds % 60 > 0:
			if uptime != "":
				uptime += " "
			uptime += str(seconds % 60) + " "
			if seconds % 60 == 1:
				uptime += "second"
			else:
				uptime += "seconds"
		logger.debug("Calculated uptime")  # Event log
		return uptime
	except Exception as exception:
		logger.error("Failed to calculate uptime. Exception: " + str(exception))  # Event log
		return None


# Main code
if __name__ == "__main__":
	# Client stuff
	client = discord.Client(intents=discord.Intents.all())

	# Client events
	@client.event
	async def on_ready():
		"""Runs when the client is ready."""

		logger.debug("`on_ready` start")

		global connected
		connected = True

		if client.guilds != []:
			logger.info(client.user.name + " is ready (commencing on_ready)")
			for guild in client.guilds:

				# Client message
				logger.info("    " + guild.name + " (ID: " + str(guild.id) + ")")

				# If the bot has been added to a guild while offline
				if str(guild.id) not in data["servers"]:
					logger.warning("The bot is in a guild (" + guild.name + " (" + str(guild.id) + ")) but has no data for it.")

					# Initialise guild
					initialise_guild(guild)

				# Initialise cache for guilds
				else:
					cache[str(guild.id)] = {}
					poll[str(guild.id)] = {}

				# If the guild has announcements enabled, sends an announcement in their announcements channel
				try:
					if data["servers"][str(guild.id)]["config"]["announcements channel id"] != None:
						channel = discord.utils.get(guild.channels, id=data["servers"][str(guild.id)]["config"]["announcements channel id"])
						await channel.send("**" + client.user.name + "** online\nVersion " + data["config"]["version"] + ".")
				except Exception as exception:
					logger.error("Failed to send announcement message in " + guild.name + " (" + str(guild.id) + "). Exception: " + str(exception))

		logger.debug("`on_ready` end")

	@client.event
	async def on_disconnect():
		"""Runs when the client disconnects."""

		global connected

		# Stops code from being run every time discord realises its still disconnected
		if connected == True:
			logger.info("Bot disconnected")
			connected = False

	@client.event
	async def on_guild_join(guild):
		"""Runs when the client joins a guild."""

		logger.debug("`on_guild_join` " + guild.name + " (" + str(guild.id) + ").")

		# If server data doesn't already exist, initialises server data
		if str(guild.id) not in data["servers"]:
			initialise_guild(guild)

	@client.event
	async def on_guild_remove(guild):
		"""Runs when the client is removed from a guild."""

		logger.debug("`on_guild_remove` " + guild.name + " (" + str(guild.id) + ").")

	@client.event
	async def on_message(message):
		"""Runs when a message is sent."""

		logger.debug("Message sent by " + message.author.name + ".")

		# Ignores bots
		if message.author.bot is True:
			return

		# If the levels functionality is enabled
		if "levels" in data["servers"][str(message.guild.id)]:
			try:

				# If the user hasn't spoken in an hour or more
				if (message.author.id not in cache[str(message.guild.id)]) or ((datetime.now() - cache[str(message.guild.id)][message.author.id]).seconds // 3600 > 0):

					# Update the cache and increment the user's experience
					cache[str(message.guild.id)][message.author.id] = datetime.now()
					if str(message.author.id) in data["servers"][str(message.guild.id)]["levels"]:
						data["servers"][str(message.guild.id)]["levels"][str(message.author.id)] += 1
					else:
						data["servers"][str(message.guild.id)]["levels"][str(message.author.id)] = 1

					# Write the updated data
					update_data()

			except Exception as exception:
				logger.error("Failed to add experience to " + message.author.name + " in " + message.guild.name + " (" + str(message.guild.id) + "). Exception: " + str(exception))

	@client.event
	async def on_raw_reaction_add(payload):
		"""Runs when a reaction is added."""

		# Ignores bots
		if payload.member.bot is True:
			return

		# If the message is one of the server's purge messages
		if payload.message_id in purge_messages:
			logger.debug("Purge message reacted to")  # Temp log
			if payload.member.guild_permissions.administrator is True:
				logger.info("Purge confirmed by admin")  # Temp log
				if str(payload.emoji) == "👍":

					# Purge messages
					try:
						await client.get_channel(payload.channel_id).purge(limit=purge_messages[payload.message_id])
						logger.error("Purged messages from " + payload.channel.name + " in " + payload.guild.name + " (" + payload.guild_id + ").")
						await client.get_channel(payload.channel_id).send("Channel purged " + str(purge_messages[payload.message_id]) + " messages")
					except Exception as exception:
						logger.error("Failed to purge messages from " + payload.channel.name + " in " + payload.guild.name + " (" + payload.guild_id + "). Exception: " + str(exception))
					finally:
						purge_messages.pop(payload.message_id)
						return

		# If the roles functionality is enabled
		if "roles" in data["servers"][str(payload.guild_id)]:
			try:

				# Checks if the message is one of the server's roles messages
				message_relevant = False
				for category in data["servers"][str(payload.guild_id)]["roles"]:
					if payload.message_id == data["servers"][str(payload.guild_id)]["roles"][category]["message id"]:
						message_relevant = True
						break
				if message_relevant is False:
					return

				# Checks if the bot is still in the server and if it's cached
				if client.get_guild(payload.guild_id) is None:
					return

				# Checks if the reaction is one of the ones we care about
				role_id = -1
				for category in data["servers"][str(payload.guild_id)]["roles"]:
					for role in data["servers"][str(payload.guild_id)]["roles"][category]["list"]:
						if str(payload.emoji) == data["servers"][str(payload.guild_id)]["roles"][category]["list"][role]["emoji"]:
							role_id = int(role)
							break
				if role_id == -1:  # Removes the reaction if it one of the ones we care about
					channel = await client.fetch_channel(payload.channel_id)
					message = await channel.fetch_message(payload.message_id)
					# If the emoji is a custom emoji
					if payload.emoji.is_custom_emoji() is False:
						reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
					# If the emoji is not a custom emoji
					else:
						reaction = discord.utils.get(message.reactions, emoji=payload.emoji)
					await reaction.remove(payload.member)
					return

				# Checks if the role exists and is valid
				role = client.get_guild(payload.guild_id).get_role(role_id)
				if role is None:
					return

				# Adds the role
				await payload.member.add_roles(role)
				logger.debug("Added role " + role.name + " to " + payload.member.name)

			except Exception as exception:
				logger.error("Failed to add role " + role.name + " to " + payload.member.name + ". Exception: " + str(exception))

	@client.event
	async def on_raw_reaction_remove(payload):
		"""Runs when a reaction is removed."""

		# If the roles functionality is enabled
		if "roles" in data["servers"][str(payload.guild_id)]:

			try:
				# The payload for `on_raw_reaction_remove` does not provide `.member`
				# so we must get the member ourselves from the payload's `.user_id`
				member = client.get_guild(payload.guild_id).get_member(payload.user_id)

				# Ignores bots
				if member.bot is True:
					return

				# Checks if the message is one of the server's roles messages
				message_relevant = False
				for category in data["servers"][str(payload.guild_id)]["roles"]:
					if payload.message_id == data["servers"][str(payload.guild_id)]["roles"][category]["message id"]:
						message_relevant = True
						break
				if message_relevant is False:
					return

				# Checks if the bot is still in the server and if it's cached
				if client.get_guild(payload.guild_id) is None:
					return

				# Checks if the reaction is one of the ones we care about
				role_id = -1
				for category in data["servers"][str(payload.guild_id)]["roles"]:
					for role in data["servers"][str(payload.guild_id)]["roles"][category]["list"]:
						if str(payload.emoji) == data["servers"][str(payload.guild_id)]["roles"][category]["list"][role]["emoji"]:
							role_id = int(role)
							break

				# Checks if the role exists and is valid
				role = client.get_guild(payload.guild_id).get_role(role_id)
				if role is None:
					return

				# Removes the role
				await member.remove_roles(role)
				logger.debug("Removed role " + role.name + " from " + member.name)
			except Exception as exception:
				logger.error("Failed to remove role " + role.name + " from " + member.name + ". Exception: " + str(exception))

	# Buttons...
	# The following must be tested:
	#     - Bots cannot press buttons
	#     - What happens when the bot isn't in the guild or the guild isn't cached (see
	#       on_raw_reaction_add for details)
	@client.event
	async def on_component(ctx):
		"""Runs on button press."""

		print("Button pressed by " + ctx.author.name)

		guild = ctx.origin_message.guild

		# If the roles functionality is enabled
		if "roles" in data["servers"][str(guild.id)]:
			try:

				# Checks if the message is one of the server's roles messages
				message_relevant = False
				for category in data["servers"][str(guild.id)]["roles"]:
					if ctx.origin_message_id == data["servers"][str(guild.id)]["roles"][category]["message id"]:
						message_relevant = True
						break
				if message_relevant is False:
					return

				# Checks if the role ID is one of the server's roles
				role_id_found = False
				for category in data["servers"][str(guild.id)]["roles"]:
					if ctx.custom_id in data["servers"][str(guild.id)]["roles"][category]["list"]:
						role_id_found = True
						break
				if role_id_found is False:
					return

				# Checks if the role exists and is valid
				role = guild.get_role(int(ctx.custom_id))
				if role is None:
					return

				# Adds the role if the user doesn't have it
				if role not in ctx.author.roles:
					await ctx.author.add_roles(role)
					await ctx.edit_origin(content="You pressed a button!")
					logger.debug("Added role " + role.name + " to " + ctx.author.name)

				# Removes the role if the user already has it
				else:
					await ctx.author.remove_roles(role)
					await ctx.edit_origin(content="You pressed a button!")
					logger.debug("Removed role " + role.name + " from " + ctx.author.name)

				# Send Pong response. Incipit Helminth...
				with open("token.txt") as file:
					url = "https://discordapp.com/api/channels/{}/messages".format(ctx.origin_message.channel.id)
					headers = {
						"Authorization": "Bot {}".format(file.read()),
						"Content-Type": "application/json"
					}
					JSON = {
						"type": 1
					}
					r = requests.post(url, headers=headers, data=json.dumps(JSON))
				print(r.status_code, r.reason)
				return

			except Exception as exception:
				logger.error("Failed to add role " + role.name + " to " + ctx.author.name + ". Exception: " + str(exception))  # Error: this may run even if the intention of the button press isn't to add a role
			finally:
				return

		# Placeholder for other buttons functionality. Do not remove without consulting Pablo's forboding psionic foresight
		if False is True:
			print("https://media.tenor.co/videos/6361572ebe664cc462727807a7359f7c/mp4")

	# Slash commands
	# The following must be tested:
	#     - Bots cannot run commands
	#     - What happens when the bot isn't in the guild or the guild isn't cached (see
	#       on_raw_reaction_add for details)
	# The following must be made better:
	#     - Standardise command and option descriptions
	slash = SlashCommand(client, sync_commands=True)
	# This is a temporary (partially functional) solution to uploading global slash commands, which
	# are cached hourly and would cause problems on a debugging timescale. This approach will not
	# work, however, for guilds that the bot joins while running. This could be solved easily by
	# adding code to on_guild_join or initialise_guild, but I'd rather keep it partially functional
	# while we're figuring this out.
	guild_ids = []
	for guild in client.guilds:
		guild_ids += guild.id

	# Ping command
	@slash.slash(
		name="ping",
		description=command_data["ping"]["description"],
		guild_ids=guild_ids)
	async def _ping(ctx):
		"""Runs on the ping slash command."""

		logger.debug("`/ping` called by " + ctx.author.name)

		try:
			await ctx.send("Pong! (%.3fms)" % (client.latency * 1000))
		except Exception as exception:
			logger.error("Failed to send ping message in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception))

	# Help command
	@slash.slash(
		name="help",
		description=command_data["help"]["description"],
		options=[create_option(
			name="command",
			description="The slash command you want help with. Leave blank if you want to see help for all commands.",
			option_type=3,
			required=False)],
		guild_ids=guild_ids)
	async def _help(ctx, command=None):
		"""Runs on the help slash command."""

		logger.debug("`/help` called by " + ctx.author.name)

		try:
			if command == None:
				help_embed = discord.Embed(title="🤔 Need help?", description="Here's a list of " + client.user.name + "'s commands!\nFor more detailed help, go to https://www.lingscars.com/", color=0xffc000)
				help_embed.add_field(name=str("/ping"), value="Pings the bot to check latency.")
				help_embed.add_field(name=str("/help"), value="Displays help information.")
				help_embed.add_field(name=str("/embed"), value="Sends a custom-made embed.")
				help_embed.add_field(name=str("/level"), value="Sends the user's level card, showing their current level and their progress to the next level.")
				help_embed.add_field(name=str("/stats"), value="Sends the server's stats embed.\nAdmin only feature.")
				help_embed.add_field(name=str("/rules"), value="Sends the server's rules embed.\nAdmin only feature.")
				help_embed.add_field(name=str("/roles"), value="Sends the server's roles embed.\nAdmin only feature.")
				await ctx.send(embed=help_embed)

			else:
				if command == "ping":
					help_embed = discord.Embed(title="🗒️ Information for /ping", description="Engage in a ruthless game of table tennis. Also pings the bot to check latency.", color=0xffc000)
					await ctx.send(embed=help_embed)
				elif command == "help":
					help_embed = discord.Embed(title="🗒️ Information for /help", description="Lists the bot's commands.\nOptional parameter `command` specifies the command to display information for.", color=0xffc000)
					await ctx.send(embed=help_embed)
				elif command == "embed":
					help_embed = discord.Embed(title="🗒️ Information for /help", description="Sends a custom-made embed.\n Required parameters `title` and `description specify the embed's title and description. Optional parameter `color` specifies the embed's color.", color=0xffc000)
				elif command == "level":
					help_embed = discord.Embed(title="🗒️ Information for /level", description="Sends the user's level card, showing their current level and their progress to the next level.", color=0xffc000)
				else:
					await ctx.send("Command not recognised...\nUse `/help` to see all commands and `/help command:` to get help for a specific command.")

		except Exception as exception:
			logger.error("Failed to send help message in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception))

	# Embed command
	@slash.slash(name="embed",
		description=command_data["embed"]["description"],
		options=[create_option(
			name="title",
			description="The embed title.",
			option_type=3,
			required=False),
		create_option(
			name="description",
			description="The embed description.",
			option_type=3,
			required=False),
		create_option(
			name="color",
			description="The embed color. Takes hexadecimal color values (without a #).",
			option_type=3,
			required=False)],
		guild_ids=guild_ids)
	async def _embed(ctx, title=discord.Embed.Empty, description=discord.Embed.Empty, color="0xffc000"):
		"""Runs on the embed slash command."""

		logger.debug("`/embed` called by " + ctx.author.name)

		try:
			# If a color is supplied, check that it is a valid hex code
			try:
				color = int(color, 16)
			# Otherwise, default to the original color
			except ValueError:
				color = 0xffc000

			embed = discord.Embed(title=title, description=description, color=color)
			embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
			await ctx.send(embed=embed)

		except Exception as exception:
			logger.error("Failed to send embed message in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception))

	# Level command
	@slash.slash(
		name="level",
		description=command_data["level"]["description"],
		guild_ids=guild_ids)
	async def _level(ctx):
		"""Runs on the level slash command."""

		logger.debug("`/level` called by " + ctx.author.name)

		# If the levels functionality is enabled
		if "levels" in data["servers"][str(ctx.guild.id)]:

			try:
				# Generates the level card
				if str(ctx.author.id) in data["servers"][str(ctx.guild.id)]["levels"]:
					level = int((data["servers"][str(ctx.guild.id)]["levels"][str(ctx.author.id)] ** 0.5) // 1)
					percentage = int(round((data["servers"][str(ctx.guild.id)]["levels"][str(ctx.author.id)] - (level ** 2)) / (((level + 1) ** 2) - (level ** 2)) * 100))
				else:
					level = 0
					percentage = 0
				generate_level_card(ctx.author.avatar_url, ctx.author.name, level, percentage)

				# Creates and sends the level embed
				file = discord.File("level_card.png")
				await ctx.send(file=file)

			except Exception as exception:
				logger.error("Failed to send level message in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception))

		# If the levels functionality is disabled
		else:
			await ctx.send("Uh oh, you haven't set up any levels! Get a server admin to set them up at https://www.lingscars.com/")

	# Leaderboard command
	@slash.slash(
		name="leaderboard",
		description=command_data["leaderboard"]["description"],
		guild_ids=guild_ids)
	async def _leaderboard(ctx):
		"""Runs on the leaderboard slash command."""

		logger.info("`/leaderboard` called by " + ctx.author.name)

		# If the levels functionality is enabled
		if "levels" in data["servers"][str(ctx.guild_id)]:

			try:
				# Generates the leaderboard
				leaderboard = reversed(sorted(data["servers"][str(ctx.guild.id)]["levels"].items(), key=lambda item: item[1]))  # This is scuffed
				lb_message = ""
				lb_count = ""
				lb_no = ""
				count = 1
				for item in leaderboard:
					try:
						name = client.get_user(int(item[0])).name
						lb_message += str(name) + "\n"
						lb_count += str(item[1]) + "\n"
						lb_no += str(count) + "\n"
						count += 1
					except AttributeError:
						logger.debug("Member not found in server")

				# Creates and sends leaderboard embed
				leaderboard_embed = discord.Embed(title="Leaderboard", color=0xffc000)
				leaderboard_embed.add_field(name="No.", value=lb_no, inline=True)
				leaderboard_embed.add_field(name="User", value=lb_message, inline=True)
				leaderboard_embed.add_field(name="Count", value=lb_count, inline=True)
				await ctx.send(embed=leaderboard_embed)

			except Exception as exception:
				logger.error("Failed to send leaderboard in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception))

	# Buttons command
	@slash.slash(
		name="buttons",
		description="Hmm...",
		guild_ids=guild_ids)
	async def _buttons(ctx):
		"""Runs on the buttons slash command."""

		logger.info("`/buttons` called by " + ctx.author.name)

		# Experimental buttons code...
		buttons = [
			create_button(style=ButtonStyle.green, label="A green button", custom_id="green1"),
			create_button(style=ButtonStyle.blue, label="A blue button", custom_id="blue1"),
			create_button(style=ButtonStyle.red, label="A red button", custom_id="red1"),
			create_button(style=ButtonStyle.green, label="A second green button", custom_id="green2"),
			create_button(style=ButtonStyle.blue, label="A second blue button", custom_id="blue2")
		]
		action_row = create_actionrow(*buttons)

		buttons_two = [
			create_button(style=ButtonStyle.red, label="A second red button", custom_id="red2"),
			create_button(style=ButtonStyle.green, label="Another green button", custom_id="green3"),
			create_button(style=ButtonStyle.blue, label="Another blue button", custom_id="blue3"),
			create_button(style=ButtonStyle.red, label="Another second red button", custom_id="red3"),
			create_button(style=ButtonStyle.green, label="And another green button", custom_id="green4")
		]
		action_row_two = create_actionrow(*buttons_two)

		buttons_three = [
			create_button(style=ButtonStyle.blue, label="And another blue button", custom_id="blue4"),
			create_button(style=ButtonStyle.red, label="And another red button", custom_id="red4"),
			create_button(style=ButtonStyle.green, label="A last green button", custom_id="green5"),
			create_button(style=ButtonStyle.blue, label="A last blue button", custom_id="blue5"),
			create_button(style=ButtonStyle.red, label="A last red button", custom_id="red5")
		]
		action_row_three = create_actionrow(*buttons_three)

		await ctx.send(content="Howdy pardner", components=[action_row, action_row_two, action_row_three])

	# Admin commands
	# Statistics command
	@slash.slash(
		name="stats",
		description=command_data["stats"]["description"],
		guild_ids=guild_ids)
	async def _stats(ctx):
		"""Runs on the stats slash command."""

		# If the user doesn't have administrator permissions
		if ctx.author.guild_permissions.administrator is False:
			return

		logger.debug("`/stats` called by " + ctx.author.name + ".")

		try:
			# Generate statistics
			members = {}
			channel_statistics = ""
			member_statistics = ""
			for channel in ctx.guild.text_channels:
				message_count = 0
				async for message_sent in channel.history(limit=None):
					message_count += 1
					if message_sent.author.bot is False:  # Don't count messages from bots
						if message_sent.author not in members:
							members[message_sent.author] = 1
						else:
							members[message_sent.author] += 1
				channel_statistics += channel.name + ": " + str(message_count) + "\n"
			for member in members:
				member_statistics += member.name + ": " + str(members[member]) + "\n"

			# Create and send statistics embed
			stats_embed = discord.Embed(title="📈 Statistics for " + ctx.guild.name, color=0xffc000)
			stats_embed.add_field(name="Channels", value=channel_statistics)
			stats_embed.add_field(name="Members", value=member_statistics)
			stats_embed.set_footer(text="Statistics updated • " + date.today().strftime("%d/%m/%Y"), icon_url=ctx.guild.icon_url)
			await ctx.send(embed=stats_embed)

		except Exception as exception:
			logger.error("Failed to send statistics message in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception))

	# Rules command
	@slash.slash(
		name="rules",
		description=command_data["rules"]["description"],
		guild_ids=guild_ids)
	async def _rules(ctx):
		"""Runs on the rules slash command."""

		# If the user doesn't have administrator permissions
		if ctx.author.guild_permissions.administrator is False:
			return

		logger.debug("`/rules` called by " + ctx.author.name)

		# If the rules functionality is enabled
		if "rules" in data["servers"][str(ctx.guild.id)]:

			try:
				# Creates and sends the rules embed
				rules_embed = discord.Embed(title=data["servers"][str(ctx.guild.id)]["rules"]["title"], description=data["servers"][str(ctx.guild.id)]["rules"]["description"], color=0xffc000, inline=False)
				rules_embed.set_footer(text="Rules updated • " + date.today().strftime("%d/%m/%Y"), icon_url=ctx.guild.icon_url)
				rules_embed.add_field(name="Rules", value="\n".join(data["servers"][str(ctx.guild.id)]["rules"]["list"]))
				await ctx.send(embed=rules_embed)

			except Exception as exception:
				logger.error("Failed to send rules message in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception))

		# If the rules functionality is disabled
		else:
			await ctx.send("Uh oh, you haven't set up any rules! Get a server admin to set them up at https://www.lingscars.com/")

	# Roles command
	@slash.slash(
		name="roles",
		description=command_data["roles"]["description"],
		guild_ids=guild_ids)
	async def _roles(ctx):
		"""Runs on the roles slash command."""

		# If the user doesn't have administrator permissions
		if ctx.author.guild_permissions.administrator is False:
			return

		logger.debug("`/roles` called by " + ctx.author.name)

		# If the roles functionality is enabled
		if "roles" in data["servers"][str(ctx.guild.id)]:
			#try:

			# Creates and sends the roles messages
			await ctx.send("🗒️ **Role selection**\nReact to get a role, unreact to remove it.")
			for category in data["servers"][str(ctx.guild.id)]["roles"]:
				buttons = []
				for role in data["servers"][str(ctx.guild.id)]["roles"][category]["list"]:
					buttons.append(create_button(style=ButtonStyle.red, label=data["servers"][str(ctx.guild.id)]["roles"][category]["list"][role]["emoji"] + " " + data["servers"][str(ctx.guild.id)]["roles"][category]["list"][role]["name"], custom_id=role))
				components = []
				for x in range(ceil(len(buttons) / 5)):
					if len(buttons[(5 * x):]) > 5:
						components.append(create_actionrow(*buttons[(5 * x):(5 * x) + 5]))
					else:
						components.append(create_actionrow(*buttons[(5 * x):]))
				category_message = await ctx.send(content="**" + category + "**\n" + "Select the roles for this category!", components=components)

				# Updates the category's message id
				data["servers"][str(ctx.guild.id)]["roles"][category]["message id"] = category_message.id

			# Write the updated data
			update_data()

			#except Exception as exception:
			#	logger.error("Failed to send roles message in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception))

		# If the roles functionality is disabled
		else:
			await ctx.send("Uh oh, you haven't set up any roles! Get a server admin to set them up at https://www.lingscars.com/")

	# CLS command
	@slash.slash(
		name="cls",
		description=command_data["cls"]["description"],
		guild_ids=guild_ids)
	async def _cls(ctx):
		"""Runs on the cls slash command."""

		# If the user doesn't have administrator permissions
		if ctx.author.guild_permissions.administrator is False:
			return

		logger.debug("`/cls` called by " + ctx.author.name)

		await ctx.channel.purge(limit=5)

		await ctx.send("Channel purged, son.")

	# status command
	@slash.slash(
		name="status",
		description=command_data["status"]["description"],
		guild_ids=guild_ids)
	async def _status(ctx):
		"""Runs on the status slash command."""

		# If the user doesn't have administrator permissions
		if ctx.author.guild_permissions.administrator is False:
			return

		logger.debug("`/status` called by " + ctx.author.name)

		hostname = socket.gethostname()
		await ctx.send("This instance is being run on **" + hostname + "**, IP address **" + socket.gethostbyname(hostname) + ("** (**%.3fms**)\nUptime: " % (client.latency * 1000)) + get_uptime() + ".")

	# Kill command
	@slash.slash(
		name="kill",
		description=command_data["kill"]["description"],
		options=[create_option(
			name="reason",
			description="The reason for killing my son.",
			option_type=3,
			required=False)],
		guild_ids=guild_ids)
	async def _kill(ctx, reason=None):
		"""Runs on the kill slash command."""

		# If the user doesn't have administrator permissions
		if ctx.author.guild_permissions.administrator is False:
			return

		logger.debug("`/kill` called by " + ctx.author.name)

		# Send kill announcement
		for guild in client.guilds:

			# Check if an announcement channel is given
			if data["servers"][str(ctx.guild.id)]["config"]["announcements channel id"] is not None:
				announcement_sent = False
				for channel in guild.text_channels:
						logger.debug("Sending kill announcement to " + guild.name + " (" + str(guild.id) + ") in " + channel.name)
						announcement_sent = True
						await channel.send(reason)
						break
				if announcement_sent is False:
					logger.debug("Failed to send kill announcement to " + guild.name + " (" + str(guild.id) + ")")

		await ctx.channel.send(reason + "\nUptime: " + get_uptime() + ".")
		await client.close()


	# Run client
	with open("token.txt") as file:
		client.run(file.read())
		client.activity = discord.Activity(type=discord.ActivityType.listening, name="the rain")
