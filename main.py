# Imports
import asyncio
from math import ceil
from random import randint, random, shuffle
from os import path
from datetime import date, datetime
import sched, time
import json
import re
import requests
import socket
import cv2
import discord
import discord.ext.commands
# from discord.ui import Modal, InputText
# from discord_slash.utils.manage_commands import create_option, create_permission, remove_all_commands
# from discord_slash.utils.manage_components import create_button, create_actionrow, ButtonStyle, create_select, create_select_option
# from discord_slash.model import SlashCommandPermissionType, ContextMenuType
# import interactions
from discord import app_commands

import challenger
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Local imports
from challenger import formatChallenge
from log_handling import *
from imaging import generate_level_card
import AI
from colours import colours

# Loads config CONST variables
DEFAULT_TOKEN = "ENTER TOKEN HERE"
DEFAULT_PREFIX = "-"
DEFAULT_DEBUG = True
DEFAULT_LEVEL = "INFO"
DEFAULT_JOKE_SERVERS = []
DEFAULT_REPORT_CHANNEL = None
DEFAULT_DEVELOPERS = [241772848564142080, 258284765776576512]
DEFAULT_DEFAULT_COLOUR = 0xffc000 # Default

hostname = socket.gethostname()

VERSION = "1.3.4 beta"
SERVER_STRUCTURE = \
	{
		"config": {
			"announcements channel id": 0
		},
		"rules": {
			"title": "Server rules",
			"description": "",
			"list": [],
			"image link": ""
		},
		"roles": {
			"verify role": 0,
			"categories": {}
		},
		"ranks": {}
	}

TOKEN = DEFAULT_TOKEN
PREFIX = DEFAULT_PREFIX
DEBUG = DEFAULT_DEBUG
LEVEL = DEFAULT_LEVEL
JOKE_SERVERS = DEFAULT_JOKE_SERVERS
REPORT_CHANNEL = DEFAULT_REPORT_CHANNEL
DEVELOPERS = DEFAULT_DEVELOPERS
DEFAULT_COLOUR = DEFAULT_DEFAULT_COLOUR

# Data upgrade
def upgrade_data():
	global DEVELOPERS
	new_data = {}
	data = {}
	config = {}
	try:
		with open("data.json", encoding='utf-8') as file:
			data = json.load(file)
		with open("config.json", encoding='utf-8') as config_file:
			config = json.load(config_file)
		if "config" in data:
			print("Upgrading data file")

			# Data "config" rename to "bot settings"
			new_data = {"bot settings": data["config"]}
			del data["config"]

			new_data.update(data)

			# Developers move to config
			if "developers" in new_data["bot settings"]:
				print("Detected developers in old location")
				# Checks if config or data developers should be used
				move = "y"
				if "developers" in config:
					move = input("Developers found in config file, would you like to replace with ones in data file? Y/N").lower()
				if move == "y":
					print("Moving developers data")
					DEVELOPERS = new_data["bot settings"]["developers"]
					config["developers"] = DEVELOPERS
				del new_data["bot settings"]["developers"]

		else:
			new_data.update(data)

		with open("data.json", "w", encoding='utf-8') as file:
			json.dump(new_data, file, indent=4)
		with open("config.json", "w") as file:
			json.dump(config,file, indent=4)
	except FileNotFoundError:
		print("data.json not setup. This is a fresh install!")
	except Exception as exception:
		print(f"Failed to check data file was upgraded: \"{type(exception).__name__}\" : {exception.args[0]}\n")
upgrade_data()

def create_config():
	with open("config.json", "w") as file:
		TOKEN = input("Please input your bot's token (this will be stored in the config.json file)")
		json.dump({"token": TOKEN,"prefix":PREFIX,"debug":DEBUG,"level":LEVEL,"joke servers":JOKE_SERVERS,"report channel":REPORT_CHANNEL,"developers":DEVELOPERS,"default colour":DEFAULT_COLOUR}, file, indent=4)
		print("Additional config can be written in config.json")

def setup_config():
	global TOKEN, PREFIX, DEBUG, LEVEL, JOKE_SERVERS, REPORT_CHANNEL, DEVELOPERS, DEFAULT_COLOUR

	def initiate_const(name, default, dictionary):
		try:
			return dictionary[name]
		except KeyError:
			return default

	if not path.exists("config.json"):
		create_config()
		print("config.json created")
	with open("config.json", encoding='utf-8') as file:
		try:
			data = json.load(file)
		except json.JSONDecodeError:
			data = {}
		TOKEN = initiate_const("token", DEFAULT_TOKEN, data)
		if TOKEN == DEFAULT_TOKEN:
			create_config()
			print("config.json setup")
		PREFIX = initiate_const("prefix", DEFAULT_PREFIX, data)
		DEBUG = initiate_const("debug", DEFAULT_DEBUG, data)
		LEVEL = initiate_const("level", DEFAULT_LEVEL, data)
		JOKE_SERVERS = initiate_const("joke servers", DEFAULT_JOKE_SERVERS, data)
		REPORT_CHANNEL = initiate_const("report channel", DEFAULT_REPORT_CHANNEL, data)
		DEVELOPERS = initiate_const("developers", DEFAULT_DEVELOPERS, data)
		DEFAULT_COLOUR = initiate_const("default colour", DEFAULT_DEFAULT_COLOUR, data)

setup_config()

# Functions
def populate_actionrows(button_list):
	"""Returns a list of actionrows of 5 or fewer buttons."""

	actionrow_list = []
	for x in range(ceil(len(button_list) / 5)):
		if len(button_list[(5 * x):]) > 5:
			actionrow_list.append(create_actionrow(*button_list[(5 * x):(5 * x) + 5]))
		else:
			actionrow_list.append(create_actionrow(*button_list[(5 * x):]))
	return actionrow_list

# Definitions
class MyClient(discord.ext.commands.Bot):

	def __init__(self, *args, **kwargs):
		"""Constructor."""

		super().__init__(*args, **kwargs,command_prefix=PREFIX)
		self.connected = True  # Starts true so on first boot, it won't think its restarted
		self.start_time = datetime.now()
		self.last_disconnect = datetime.now()
		self.data = {}
		self.cache = {}
		self.poll = {}
		self.purge_messages = {}
		self.activity = discord.Activity(type=discord.ActivityType.listening, name="the rain")  # There is no room for purple gods here

		# Prints logs to the console
		if DEBUG is True:
			x = logging.StreamHandler()
			x.setLevel(LEVEL)
			logger.addHandler(x)

	def update_data(self):
		"""Writes the data attribute to the file."""

		try:
			with open("data.json", "w", encoding='utf-8') as file:
				json.dump(self.data, file, indent=4)
			logger.debug("Updated data.json")  # Event log
		except Exception as exception:
			logger.critical("Failed to update data.json. Exception: " + str(exception))  # Event log

	def initialise_guild(self, guild):
		"""Creates data for a new guild."""

		try:
			if str(guild.id) not in self.data["servers"]: # Check if server data already exists
				self.data["servers"][str(guild.id)] = SERVER_STRUCTURE
			self.cache[str(guild.id)] = {}
			self.poll[str(guild.id)] = {}

			# Write the updated data
			self.update_data()
			logger.info("Initialised guild: " + guild.name + " (ID: " + str(guild.id) + ")")  # Event log
		except Exception as exception:
			logger.critical("Failed to initialise guild: " + guild.name + " (ID: " + str(guild.id) + "). Exception: " + str(exception))  # Event log

	def get_uptime(self):
		"""Returns instance uptime."""

		try:
			seconds = round((datetime.now() - self.start_time).total_seconds())
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

	async def terminate_poll(self, message):
		"""Closes poll"""

		reactions = message.reactions
		highest_count = 0
		emojis = []
		counts = []

		for reaction in reactions:
			emoji = reaction.emoji
			if emoji not in emojis:
				emojis.append(emoji)
			if str(emoji) != "🔚":  # Doesn't count end emote
				counts.append(str(reaction.count - 1))
			if reaction.count > highest_count:
				highest_count = reaction.count
				highest_emoji = reaction.emoji
		highest_count -= 1  # Takes away the bots reaction

		poll = self.poll[str(message.guild.id)][str(message.id)]

		options = []
		# for option in poll["options"]:  # Makes list of options
		for emoji in emojis:
			if str(emoji) != "🔚":
				options.append(str(emoji) + " " + poll["voters"][str(emoji)])

		title = str(poll["title"])
		if title == "Embed.Empty":
			title = ""
		embed_results = discord.Embed(title=title + " Results")
		embed_results.add_field(name="Candidates", value="\n".join(options), inline=True)
		embed_results.add_field(name="Count", value="\n".join(counts), inline=True)
		if poll["config"]["winner"] == "highest":  # Winner is shown as the highest scoring candidate
			embed_results.add_field(name="Winner", value=(str(highest_emoji) + " " + poll["voters"][str(highest_emoji)] + " Score: " + str(highest_count)), inline=False)

		await message.channel.send(embed=embed_results)
		self.poll[str(message.guild.id)].pop(str(message.id))  # Removes poll entry from dictionary

	async def get_formatted_emoji(self, emoji_reference, guild):
		"""Returns an emoji that discord should always be able to use"""

		if emoji_reference.startswith("<"):
			parts = emoji_reference.split(":")
			return discord.utils.get(guild.emojis, name=parts[1])  # Uses the name part to get the emoji
		else:
			return emoji_reference

	async def create_thread_message(self, channel_id, content, tts=False, embeds=[]):  # Made from the corpse of helminth
		token = 'Bot ' + TOKEN

		# Converts embed(s) into json
		try:
			for x in range(len(embeds)):
				embeds[x] = embeds[x].to_dict()
		except TypeError:
			embeds = [embeds.to_dict()]

		headers = {
			"authorization": token,
			"content-type": "application/json"
		}
		request_body = {
			"content": content,
			"tts": tts,
			"embeds": embeds
		}

		return requests.post("https://discordapp.com/api/channels/" + str(channel_id) + "/messages", headers=headers,data=json.dumps(request_body))

	def get_server_colour(self,guild_id):
		if "colour theme" in self.data["servers"][str(guild_id)]["config"]:
			return self.data["servers"][str(guild_id)]["config"]["colour theme"]
		else:
			return DEFAULT_COLOUR

	async def announce(self, announcement, announcement_type="generic"):
		"""Sends announcement messages to each guild's assigned announcement channel."""

		if announcement_type == "alert":
			try:
				await self.get_channel(REPORT_CHANNEL).send(announcement)
			except AttributeError:
				logger.info("No report channel set. It is highly recommended to set one in config.json")

		else:
			for guild in self.guilds:
				if self.data["servers"][str(guild.id)]["config"]["announcements channel id"] != 0:  # Only finds announcement channel if the guild has one set
					announcement_sent = False
					for channel in guild.text_channels:
						if channel.id == self.data["servers"][str(guild.id)]["config"]["announcements channel id"]:
							logger.debug("Sending " + announcement_type + " announcement to " + guild.name + " in " + channel.name)  # Event log
							announcement_sent = True
							await channel.send(announcement)
							break
					if announcement_sent is False:
						logger.debug("Failed to send " + announcement_type + " announcement. Announcement channel not found in " + guild.name)  # Event log

	async def on_ready(self):
		"""Runs when the client is ready."""

		logger.debug("Connected!")

		if self.connected == False:
			logger.info("Last disconnect was " + str(self.last_disconnect))
			await self.announce("**Reconnected**\nLast disconnect was " + str(self.last_disconnect), announcement_type="reconnection")
		self.connected = True

		# Load the data file into the data variable
		try:
			with open("data.json", encoding='utf-8') as file:
				self.data = json.load(file)
			logger.debug("Loaded data.json")  # Event log
		except Exception as exception:
			logger.debug(f"Failed to load data.json. Exception: {exception}. Attempting to make new data.")  # Event log
			self.data = {"bot settings":{
					"jokes": False,
					"safety": True,
					"add info": True},
				"servers":{}}
			self.update_data()

		# Check if the bot has been added to a guild while offline
		for guild in self.guilds:
			if str(guild.id) not in self.data["servers"]:
				logger.warning("The bot is in " + guild.name + " but has no data for it")  # Event log

				# Initialise guild
				self.initialise_guild(guild)

		# Initialise cache for servers
		for guild in self.guilds:
			self.cache[str(guild.id)] = {}
			self.poll[str(guild.id)] = {}

		logger.info(self.user.name + " is ready (finished on_ready)")  # Event log

		# Log on_ready messages
		logger.info(self.user.name + " is ready (commencing on_ready)")  # Event log
		if self.guilds != []:
			logger.info(self.user.name + " is connected to the following guilds:")  # Event log
			for guild in self.guilds:
				logger.info("    " + guild.name + " (ID: " + str(guild.id) + ")")  # Event log

		# Send on_ready announcement
		await self.announce("**" + self.user.name + " online**\nVersion: " + VERSION, announcement_type="on_ready")
		guild_ids = []
		for guild in self.guilds:
			guild_ids.append(guild.id)

	async def on_disconnect(self):
		"""Runs on disconnection.
		Logs disconnection."""

		if self.connected == True:  # Stops code being ran every time discord realises its still disconnected since the last minute or so
			logger.info("Bot disconnected")
			self.last_disconnect = datetime.now()
			self.connected = False

	async def on_guild_join(self, guild):
		"""Runs on joining a guild.
		The bot initialises the guild if it has no data on it."""

		logger.info(self.user.name + " has joined the guild: " + guild.name + " with id: " + str(guild.id))  # Event log
		await self.announce(self.user.name + " has joined the guild: " + guild.name + " with id: " + str(guild.id),"alert")  # Event log

		# Initialise guild
		self.initialise_guild(guild)

		await guild.text_channels[0].send(f"Oh this place looks nice. Setup my settings by doing {PREFIX}settings if you have admin permissions.\nIf you need help with anything else {PREFIX}help is the way to go!")

	async def on_message(self, message):
		"""Runs on message."""

		logger.debug("Message sent by " + message.author.name)  # Event log

		# Don't respond to yourself
		if message.author.id == self.user.id:
			return

		# Don't respond to other bots
		if message.author.bot is True:  # !!! Needs to be tested. Can replace "message.author.id == self.user.id" if so. Same goes for reactions.
			return

		# Set guild of origin
		guild = self.get_guild(message.guild.id)

		# Update the user's experience
		try:
			if (message.author.id not in self.cache[str(guild.id)]) or (((datetime.now().minute + datetime.now().hour * 60) - self.cache[str(guild.id)][message.author.id]) > 60):  # This is the longest like of code I've ever seen survive a scrutinised and picky merge from me. Well played.

				logger.debug("Adding experience to " + message.author.name)  # Event log

				# Update the cache and increment the user's experience
				self.cache[str(guild.id)][message.author.id] = datetime.now().minute + datetime.now().hour * 60
				try:
					self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] += 1
				except KeyError:
					self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] = 1

				# Write the updated data
				self.update_data()
			else:
				logger.debug("Not adding experience to " + message.author.name)  # Event log
		except KeyError:
			logger.debug("Failed to add experience to " + message.author.name)

		if not message.content.startswith(PREFIX):
			# Joke functionality
			if self.data["bot settings"]["jokes"] is True:

				# Shut up Arun
				if message.author.id == 258284765776576512:
					if randint(1, 128) == 1:
						logger.debug("Shut up Arun triggered by " + message.author.name)  # Event log
						if randint(1, 3) != 3:
							await message.channel.send("shut up arun")
						else:
							await message.channel.send("arun, why are you still talking")

				# Shut up Pablo
				if message.author.id == 241772848564142080 or message.author.id == 842479806217060363:
					if randint(1, 25) == 1:
						logger.debug("Shut up Pablo triggered by " + message.author.name)  # Event log
						if randint(1, 2) == 1:
							await message.channel.send("un-shut up pablo")
						else:
							await message.channel.send("pablo, put that big brain back on sleep mode")

				if guild.id in JOKE_SERVERS:
					# Gameboy mention
					if "gameboy" in message.content.lower():
						logger.debug("`gameboy` mentioned by " + message.author.name)  # Event log
						await message.channel.send("Gameboys are worthless (apart from micro. micro is cool)")

					# Raspberry mention
					if "raspberries" in message.content.lower() or "raspberry" in message.content.lower():
						logger.debug("`raspberry racers` mentioned by " + message.author.name)  # Event log
						await message.channel.send(
							"The Raspberry Racers are a team which debuted in the 2018 Winter Marble League. Their 2018 season was seen as the second-best rookie team of the year, behind only the Hazers. In the 2018 off-season, they won the A-Maze-ing Marble Race, making them one of the potential title contenders for the Marble League. They eventually did go on to win Marble League 2019.")

					# Pycharm mention
					if "pycharm" in message.content.lower():
						logger.debug("`pycharm` mentioned by " + message.author.name)  # Event log
						await message.channel.send(
							"Pycharm enthusiasts vs Sublime Text enjoyers: https://youtu.be/HrkNwjruz5k")
						await message.channel.send(
							"85 commits in and haha bot print funny is still our sense of humour.")

				# Token command
				if message.content == "token":
					logger.debug("`token` called by " + message.author.name)  # Event log
					await message.channel.send("IdrOppED ThE TokEN gUYS!!!!")

				# Summon lizzie command
				if message.content == "summon lizzie":
					logger.debug("`summon_lizzie` called by " + message.author.name)  # Event log
					for x in range(100):
						await message.channel.send(guild.get_member(692684372247314445).mention)

				# Summon leo command
				if message.content == "summon leo":
					logger.debug("`summon_leo` called by " + message.author.name)  # Event log
					for x in range(100):
						await message.channel.send(guild.get_member(242790351524462603).mention)

				# Teaching bitches how to swim
				if message.content == "swim":
					logger.debug("`swim` called by " + message.author.name)  # Event log
					await message.channel.send("/play https://youtu.be/uoZgZT4DGSY")
					await message.channel.send("No swimming lessons today ):")

				# Overlay Israel (Warning: DEFCON 1)
				if message.content == "israeli defcon 1":
					logger.debug("`israeli_defcon_1` called by " + message.author.name)  # Event log
					await message.channel.send("apologies in advance...")
					while True:
						await message.channel.send(".overlay israel")

			return
		else:
			message.content = message.content[len(PREFIX):]
		# Get level command
		if message.content == "level":

			logger.info("`level` called by " + message.author.name)  # Event log

			# Generate the rank card
			if str(message.author.id) in self.data["servers"][str(guild.id)]["ranks"]:
				rank = int((self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] ** 0.5) // 1)
				percentage = int(round((self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] - (rank ** 2)) / (((rank + 1) ** 2) - (rank ** 2)) * 100))
			else:
				rank = 0
				percentage = 0
			generate_level_card(message.author.avatar.url, message.author.name, rank, percentage, server_picture=guild.icon)

			# Create the rank embed
			embed_level = discord.Embed()
			file = discord.File("card.png")
			embed_level.set_image(url="attachment://card.png")

			# Send the embed
			await message.channel.send(file=file)

		# Level leaderboard command
		if message.content == "leaderboard":

			logger.info("`leaderboard` called by " + message.author.name)  # Event log

			leaderboard = reversed(sorted(self.data["servers"][str(guild.id)]["ranks"].items(), key=lambda item: item[1]))  # Sorts rank dictionary into list
			lb_message = ""
			lb_count = ""
			lb_no = ""

			count = 1
			for item in leaderboard:
				try:
					name = self.get_user(int(item[0])).name
					lb_message += str(name) + "\n"  # Reverse adds on higher scored names
					lb_count += str(item[1]) + "\n"  # Reverse adds on higher scores to separate string for separate embed field
					lb_no += str(count) + "\n"
					if count >= 100:
						break
					count += 1
				except AttributeError:
					logger.debug("Member not found in server")

			embed_leaderboard = discord.Embed(title="Leaderboard", colour=self.get_server_colour(guild.id))
			embed_leaderboard.add_field(name="No.", value=lb_no, inline=True)
			embed_leaderboard.add_field(name="User", value=lb_message, inline=True)
			embed_leaderboard.add_field(name="Count", value=lb_count, inline=True)
			await message.channel.send(embed=embed_leaderboard)

		# Embed command
		if message.content.startswith("embed"):

			logger.info("`embed` called by " + message.author.name)  # Event log

			try:
				argument_string = message.content[len("embed "):]
				arguments = re.split(",(?!\s)", argument_string)  # Splits arguments when there is not a space after the comma, if there is, it is assumed to be part of a sentance.
				title = discord.Embed.Empty
				description = discord.Embed.Empty
				colour = self.get_server_colour(guild.id)
				fields = []

				# Analyse argument
				for argument in arguments:
					argument = argument.split("=")
					if len(argument) == 2:
						if argument[0] == "title":
							title = argument[1]
						elif argument[0] == "description":
							description = argument[1]
						elif argument[0] == "colour":
							try:
								colour = int(argument[1][-6:], 16)
							except ValueError:
								if argument[1] in colours:
									colour = colours[argument[1]]
						else:
							fields.append({argument[0]: argument[1]})
					else:
						description = argument[0]

				# Create and send user's embed
				embed = discord.Embed(title=title, description=description, colour=colour)
				embed.set_author(name=message.author.name, url=discord.Embed.Empty, icon_url=message.author.avatar_url)
				for field in fields:
					embed.add_field(name=list(field.keys())[0], value=field[list(field.keys())[0]])

				await message.channel.send(embed=embed)
				await message.delete()
			except Exception as exception:
				logger.error(f"Failed understand embed command. Exception: \"{type(exception).__name__}\" : {exception.args[0]}")
				await message.channel.send("Embed Failed: Check you put something to embed and that it's under 1024 character.\n" + str(exception))

		# QR command
		if message.content == "qr":

			logger.info("`qr` called by " + message.author.name)  # Event log

			if len(message.attachments) == 1:
				await message.attachments[0].save("qrcode.png")
				img = cv2.imread("qrcode.png")
				det = cv2.QRCodeDetector()
				val, pts, st_code = det.detectAndDecode(img)
				await message.channel.send(val)

		# Help command
		if message.content == "help":

			logger.info("`help` called by " + message.author.name)  # Event log

			# Create and send the help embed
			embed_help = discord.Embed(title="🤔 Need help?", description="Here's a list of " + self.user.name + "'s commands!", colour=self.get_server_colour(guild.id))
			embed_help.add_field(name=str(PREFIX + "__level__"), value="Creates your level card, showing your current level and progress to the next level.")
			embed_help.add_field(name=str(PREFIX + "__leaderboard__"), value="Displays leaderboard for Sirius' levelling system")
			embed_help.add_field(name=str(PREFIX + "__help__"), value="Creates the bot's help embed, listing the bot's commands.")
			embed_help.add_field(name=str(PREFIX + "__embed__"), value="Creates an embed. Arguments: title=,description=,colour=[a colour],[name of field]=[string (Do not include commas or =)] (or just write and it'll be put in the description by deafult)")
			embed_help.add_field(name=str(PREFIX + "__(/)poll__"), value="Creates a poll embed. Arguments: title=, colour=[a colour], anonymous(anon)=[true/false], [name of candidate]=[emoji]. All paramaters are optional. Admins react with 🔚 (end) to end poll) or right click>Apps>Close poll for anon poll")
			embed_help.add_field(name=str("__/confess__"), value="Send your confession to the database anonymously for admins to review and post")
			embed_help.add_field(name=str("__/question__"), value="Asks Sirius a question. Don't expect a very insightful response...")
			embed_help.add_field(name=str("__/anonymous__"), value="Posts your message anonymously in the current channel")
			embed_help.add_field(name=str(PREFIX + "__rules__"), value="Creates the server's rules embed.\n**Admin only feature.**")
			embed_help.add_field(name=str(PREFIX + "__roles__"), value="Creates the server's roles embed.\n**Admin only feature.**")
			embed_help.add_field(name=str(PREFIX + "__stats__"), value="Creates the server's stats embed by default. Can send csv file instead.Argument: csv=[true/false] (Optional. False by default)\n**Admin only feature.**")
			embed_help.add_field(name=str(PREFIX + "__(/)purge__"), value="Deletes last x amount of messages. Argument: number of messages. **Consider using the slash command instead!**\n**Admin only feature.**")
			embed_help.add_field(name=str(PREFIX + "__review confessions__"), value="Shows all unposted confessions in the channel the is sent in. Each confession has a button to remove it from " + self.user.name + "'s data.\n**Admin only feature.**")
			embed_help.add_field(name=str(PREFIX + "__post confessions__"), value="Posts all unposted confessions in the channel the command is sent in.\n**Admin only feature.**")
			embed_help.add_field(name=str(PREFIX + "__settings__"), value="Brings up server settings page\n**Admin only feature.**")
			embed_help.add_field(name=str(PREFIX + "__config__"), value="Brings up " + self.user.name + " configuration page.\n**Dev only feature.**")
			embed_help.add_field(name=str(PREFIX + "__report__"), value="Reports the value of the variable(s) given. Argument: [name of almost any variable]\n**Dev only feature. safety off to use.**")
			embed_help.add_field(name=str(PREFIX + "__announce__"), value="Sends a generic announcement with a parameter for the message.\n**Dev only feature.**")
			embed_help.add_field(name=str(PREFIX + "__locate__"), value="Locates the instance of " + self.user.name + ".\n**Dev only feature.**")
			embed_help.add_field(name=str(PREFIX + "__kill__"), value="Ends the instance of " + self.user.name + ".\n**Dev only feature.**")
			await message.channel.send(embed=embed_help)

		# Set Challenge command
		if message.content.startswith("set challenges"):

			logger.info("`set challenges` called by " + message.author.name)  # Event log
			if "challenges" not in self.data["servers"][str(guild.id)]:
				self.data["servers"][str(guild.id)]["challenges"] = []
			content = message.content[len("set challenges "):]
			challenges = re.split(r"\n|\r",content)
			challenges = [challenge.strip() for challenge in challenges]
			# Find every line beginning with * and have everything under this as a new set
			setIndexes = []
			for i in range(len(challenges)):
				if challenges[i].startswith("*"):
					setIndexes.append(i)
			challengeSets = {} # JSON pointing to lists of challenges
			for i in range(len(setIndexes)):
				if i == len(setIndexes) - 1:
					challengeSets[challenges[setIndexes[i]][1:]] = challenges[setIndexes[i]+1:]
				else:
					challengeSets[challenges[setIndexes[i]][1:]] = challenges[setIndexes[i]+1:setIndexes[i+1]]
	
			self.data["servers"][str(guild.id)]["challenges"] = challengeSets
			self.update_data()
			await message.channel.send(f"{len(challenges)} challenges set!")

		# Challenge command
		if message.content == "challenge":

			logger.info("`challenge` called by " + message.author.name)  # Event log
			if "challenges" not in self.data["servers"][str(guild.id)]:
				await message.channel.send("No challenges have been added. Please ask an admin to set them up!")
			else:
				challengesSets = self.data["servers"][str(guild.id)]["challenges"]
				# Joing all lists together
				challengesList = []
				for challenges in challengesSets.values():
					challengesList.extend(challenges)
				# Randomise the order of the challenges
				shuffle(challengesList)
				
				await message.channel.send(formatChallenge(challengesList[0]))
		
		# Pub crawl top trumps command
		if message.content == "pub":
			logger.info("`pub` called by " + message.author.name)  # Event log

			taskNumber = 0
			challengeSets = self.data["servers"][str(guild.id)]["challenges"]
			challengeSetA = challengeSets[list(challengeSets.keys())[0]]
			shuffle(challengeSetA)
			challengeSetB = challengeSets[list(challengeSets.keys())[1]]
			shuffle(challengeSetB)
			# Run function at 17:00
			s = sched.scheduler(time.time, time.sleep)
			# 1 - 5pm
			s.enterabs(datetime.now().replace(hour=17, minute=00, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetA[taskNumber])))
			s.enterabs(datetime.now().replace(hour=17, minute=00, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetB[taskNumber])))
			taskNumber += 1

			# 2 - 6pm
			s.enterabs(datetime.now().replace(hour=18, minute=00, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetA[taskNumber])))
			s.enterabs(datetime.now().replace(hour=18, minute=00, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetB[taskNumber])))

			taskNumber += 1
			# 3 - 6:45pm
			s.enterabs(datetime.now().replace(hour=18, minute=45, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetA[taskNumber])))
			s.enterabs(datetime.now().replace(hour=18, minute=45, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetB[taskNumber])))

			taskNumber += 1
			# 4 - 7:30pm
			s.enterabs(datetime.now().replace(hour=19, minute=30, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetA[taskNumber])))
			s.enterabs(datetime.now().replace(hour=19, minute=30, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetB[taskNumber])))

			taskNumber += 1
			# 5 - 8:15pm
			s.enterabs(datetime.now().replace(hour=20, minute=15, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetA[taskNumber])))
			s.enterabs(datetime.now().replace(hour=20, minute=15, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetB[taskNumber])))

			taskNumber += 1
			# 6 - 9pm
			s.enterabs(datetime.now().replace(hour=21, minute=00, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetA[taskNumber])))
			s.enterabs(datetime.now().replace(hour=21, minute=00, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetB[taskNumber])))

			taskNumber += 1
			# 7 - 9:30pm
			s.enterabs(datetime.now().replace(hour=21, minute=30, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetA[taskNumber])))
			s.enterabs(datetime.now().replace(hour=21, minute=30, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetB[taskNumber])))

			taskNumber += 1
			# 8 - 10pm
			s.enterabs(datetime.now().replace(hour=23, minute=23, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetA[taskNumber])))
			s.enterabs(datetime.now().replace(hour=23, minute=23, second=00, microsecond=0).timestamp(),1,lambda: asyncio.create_task(challenger.pubCrawl(message,challengeSetB[taskNumber])))


			s.run()

			await message.channel.send("Pub crawl top trumps started!")


		# If the message was sent by the admins
		if message.author.guild_permissions.administrator:

			# Rules command
			if message.content == "rules":

				logger.info("`rules` called by " + message.author.name)  # Event log

				# If the rules have been set up
				if len(self.data["servers"][str(guild.id)]["rules"]["list"]) != 0:

					# Delete the command message
					await message.delete()

					# Create the welcome embed !!! This is messy. Decide embed format and what should be customisable
					embed_welcome = discord.Embed(title="👋 Welcome to " + message.guild.name + ".", description="[Discord community server description]\n\nTake a moment to familiarise yourself with the rules below.\nChannel <#000000000000000000> is for this, and <#000000000000000001> is for that.", colour=self.get_server_colour(guild.id))

					# Create the rules embed
					embed_rules = discord.Embed(title=self.data["servers"][str(guild.id)]["rules"]["title"], description=self.data["servers"][str(guild.id)]["rules"]["description"], colour=self.get_server_colour(guild.id), inline=False)
					embed_rules.set_footer(text="Rules updated • " + date.today().strftime("%d/%m/%Y"),  icon_url=guild.icon(size=128))
					embed_rules.add_field(name="Rules", value="\n".join(self.data["servers"][str(guild.id)]["rules"]["list"]), inline=True)
					embed_image = discord.Embed(description="That's all.", colour=self.get_server_colour(guild.id))
					image = self.data["servers"][str(guild.id)]["rules"]["image link"]
					if image != None:
						if image[:6] == "https:":
							embed_image.set_image(url=self.data["servers"][str(guild.id)]["rules"]["image link"])
						else:
							logger.debug("Image link doesn't start with https for " + str(message.guild.id))  # Event log
					else:
						logger.debug("Image link not found for " + str(message.guild.id))  # Event log

					# Send the embeds
					await message.channel.send(embed=embed_welcome)
					await message.channel.send(embed=embed_rules)
					await message.channel.send(embed=embed_image)

				# If the rules haven't been set up
				else:
					logger.debug("Rules have not been set up for " + str(message.guild.id))  # Event log
					await message.channel.send("Uh oh, you haven't set up any rules! Get a server admin to set them up at https://www.lingscars.com/")

			# Role buttons command
			if message.content == "roles":
				# If the roles functionality is enabled
				if "roles" in self.data["servers"][str(message.guild.id)]:
					# try:

					# Creates and sends the roles messages
					await message.channel.send("# 🗒️ Role selection\nClick the button to get a role, click again to remove it.")
					for category in self.data["servers"][str(message.guild.id)]["roles"]["categories"]:
						buttons = []
						for role in self.data["servers"][str(message.guild.id)]["roles"]["categories"][category]["list"]:
							buttons.append(create_button(style=ButtonStyle.blue, emoji=await self.get_formatted_emoji(self.data["servers"][str(message.guild.id)]["roles"]["categories"][category]["list"][role]["emoji"], guild), label=self.data["servers"][str(message.guild.id)]["roles"]["categories"][category]["list"][role]["name"], custom_id=role))
						components = populate_actionrows(buttons) # Puts buttons in to rows of 5 or less
						category_message = await message.channel.send(content="## " + category + "\n" + "Select the roles for this category!", components=components)

						# Updates the category's message id
						self.data["servers"][str(message.guild.id)]["roles"]["categories"][category]["message id"] = category_message.id

					# Write the updated data
					self.update_data()

				# except Exception as exception:
				#	logger.error("Failed to send roles message in " + message.guild.name + " (" + str(message.guild.id) + "). Exception: " + str(exception))

				# If the roles functionality is disabled
				else:
					await message.channel.send("Uh oh, you haven't set up any roles! Get a server admin to set them up at https://www.lingscars.com/")

			# Roles command
			if message.content == "react roles":

				logger.info("`roles` called by " + message.author.name)  # Event log

				# If the roles have been set up
				if len(self.data["servers"][str(guild.id)]["roles"]["categories"]) != 0:

					# Delete the command message
					await message.delete()

					# Send one roles message per category
					await message.channel.send("🗒️ **Role selection**\nClick to get a role, click again to remove it.")
					for category in self.data["servers"][str(guild.id)]["roles"]["categories"]:  # For category in roles
						roles = []
						for role in self.data["servers"][str(guild.id)]["roles"]["categories"][category]["list"]:  # For role in category
							roles.append(self.data["servers"][str(guild.id)]["roles"]["categories"][category]["list"][role]["emoji"] + " - " + self.data["servers"][str(guild.id)]["roles"]["categories"][category]["list"][role]["name"] + "\n")
						category_message = await message.channel.send("**" + category + "**\n\n" + "".join(roles))

						# Add reactions to the roles message
						for role in self.data["servers"][str(guild.id)]["roles"]["categories"][category]["list"]:
							await category_message.add_reaction(self.data["servers"][str(guild.id)]["roles"]["categories"][category]["list"][role]["emoji"])

						# Update the category's message id variable
						self.data["servers"][str(guild.id)]["roles"]["categories"][category]["message id"] = category_message.id

					# Write the updated data
					self.update_data()

				# If the roles haven't been set up
				else:
					logger.debug("Roles have not been set up for " + str(message.guild.id))  # Event log
					await message.channel.send("Uh oh, you haven't set up any roles! Get a server admin to set them up at https://www.lingscars.com/")

			# Stats command
			if message.content.startswith("stats"):

				logger.info("`stats` called by " + message.author.name)  # Event log

				argument = message.content[len("stats "):]
				csv = False
				if argument == "csv":  # Changes to csv mode where the stats are saved to a csv file instead
					csv = True
					logger.debug("Using csv mode")

				try:
					# Generate statistics
					if csv:
						waiting_message = await message.channel.send("Processing stats for csv\nThis may take some time...")
					else:
						waiting_message = await message.channel.send("Processing stats to display\nThis may take some time...")

					members = {}
					channel_statistics = [''] * (len(guild.text_channels))
					total_messages = 0

					# Channel statistics info gathered
					channel_count = 0
					for channel in guild.text_channels:
						channel_count += 1
						message_count = 0
						async for message_sent in channel.history(limit=None):
							message_count += 1
							if message_sent.author.bot is False:  # Don't count messages from bots
								if message_sent.author not in members:
									members[message_sent.author] = 1
								else:
									members[message_sent.author] += 1
						total_messages += message_count
						if csv:
							channel_statistics[channel_count // 10] += channel.name + "," + str(message_count) + "\n"
						else:
							channel_statistics[channel_count // 10] += channel.mention + ": " + str(message_count) + "\n"

					# Member statistics gathered from the data obtained when processing channel statistics
					member_statistics = [''] * (len(members))
					member_count = 0
					for member in members:
						member_count += 1
						if csv:
							member_statistics[member_count // 10] += member.name + "," + str(members[member]) + "\n"
						else:
							member_statistics[member_count // 10] += member.mention + ": " + str(members[member]) + "\n"
					logger.debug("Successfully generated statistics")  # Event log

					if csv:
						with open("channel_statistics.csv", "w", encoding="UTF-8") as csv:
							channel_string = ""
							for channel in channel_statistics:
								channel_string += channel
							csv.write(str(channel_string))
						await message.channel.send(file=discord.File("channel_statistics.csv", filename=guild.name + " channel_statistics.csv"))

						with open("member_statistics.csv", "w", encoding="UTF-8") as csv:
							member_string = ""
							for member in member_statistics:
								member_string += member
							csv.write(str(member_string))
						await message.channel.send(file=discord.File("member_statistics.csv", filename=guild.name + " member_statistics.csv"))
					else:
						# Create and send general statistics embed
						embed_general = discord.Embed(title="📈 General Statistics for " + guild.name, colour=self.get_server_colour(guild.id))
						embed_general.add_field(name="Total Members", value=len([m for m in guild.members if not m.bot]))
						embed_general.add_field(name="Total Bots", value=len([m for m in guild.members if m.bot]))
						embed_general.add_field(name="Total Channels", value=len(guild.text_channels))
						birth = guild.created_at
						embed_general.add_field(name="Server Birth", value=str(birth.day) + "." + str(birth.month) + "." + str(birth.year))
						embed_general.add_field(name="Total Messages", value=total_messages)
						embed_general.set_footer(text="Statistics updated • " + date.today().strftime("%d/%m/%Y"),  icon_url=guild.icon)
						await message.channel.send(embed=embed_general)

						# Create and send channel statistics embed
						embed_channel = discord.Embed(title="📈 Channel Statistics for " + guild.name, colour=self.get_server_colour(guild.id))
						for x in range(len(channel_statistics) // 10 + 1):
							# print("------\nChannels in set:\n" + str(channel_statistics[x]))
							logger.debug("------\nChannels in set:\n" + str(channel_statistics[x]))
							embed_channel.add_field(name="Channels", value=str(channel_statistics[x]))
							embed_channel.set_footer(text="Statistics updated • " + date.today().strftime("%d/%m/%Y"),  icon_url=guild.icon)
						await message.channel.send(embed=embed_channel)

						# Create and send members statistics embed
						embed_member = discord.Embed(title="📈 Member Statistics for " + guild.name, colour=self.get_server_colour(guild.id))
						for x in range(len(member_statistics) // 10 + 1):
							embed_member.add_field(name="Members", value=str(member_statistics[x]))
							embed_member.set_footer(text="Statistics updated • " + date.today().strftime("%d/%m/%Y"),  icon_url=guild.icon)
						await message.channel.send(embed=embed_member)

				except discord.errors.HTTPException as exception:
					logger.error("Error to send statistics. Exception: " + str(exception))  # Event log
					"""await message.channel.send("Error: Something went wrong on our side...")
					await message.channel.send("Trying alternative")
					embed_channel_stats = discord.Embed(title="📈 Channel statistics for " + guild.name, colour=0xffc000)
					if len(channel_statistics) <= 1024:
						embed_channel_stats.add_field(name="Channels", value=str(channel_statistics))
					else:
						for x in range(len(channel_statistics)//1024):
							embed_channel_stats.add_field(name="Channel stats prt " + str(x + 1), value=channel_statistics[0][x*1024:(x + 1)*1024])
							i = x
						embed_channel_stats.add_field(name="Channel stats prt " + str(i + 1), value=channel_statistics[0][(i + 1)*1024:])
					print(channel_statistics)
					await message.channel.send(embed=embed_channel_stats)

					embed_member_stats = discord.Embed(title="📈 Member statistics for " + guild.name, colour=0xffc000)
					if len(member_statistics) <= 1024:
						embed_member_stats.add_field(name="Members", value=str(member_statistics))
					else:
						for x in range(len(member_statistics) // 1024):
							embed_member_stats.add_field(name="Member stats prt " + str(x + 1), value=member_statistics[0][x:(x + 1) * 1024])
							i = x
						embed_member_stats.add_field(name="Member stats prt " + str(i + 1), value=member_statistics[0][(i + 1) * 1024:])
					print(member_statistics)
					await message.channel.send(embed=embed_member_stats)"""

				except Exception as exception:
					logger.error("Failed to generate or send statistics. Exception: " + str(exception))  # Event log
					await message.channel.send("Error: Something went wrong on our side...")
				await waiting_message.delete()

			# Purge Command
			if message.content.startswith("purge"):
				logger.info("`purge` called by " + message.author.name)  # Event log
				argument = message.content[len("purge "):]
				number = int(argument)

				purge_message = await message.channel.send("React with 👍 to confirm")
				self.purge_messages[purge_message.id] = number

			# Poll command
			if message.content.startswith("poll"):
				"""ERRORS TO TEST FOR: DONE
				- Duplicate emojis
				- Custom emojis
				- Duplicate custom emojis
				THINGS TO FIX:
				- Standardise datetime format - REMOVED INSTEAD
				- Remove regex secretly. IGNORE THIS!
				- Trailing newlines at the end of embed - SEEMS TO BE FIXED
				"""

				logger.info("`poll` called by " + message.author.name)  # Event log

				# Delete the command message
				await message.delete()

				# !!! Clunky and breakable
				argument_string = message.content[len("poll "):]
				if len(argument_string) < 2:
					logger.debug("Poll command had no viable arguments - cancelled")
					return
				arguments = re.split("\,\s|\,", argument_string)  # Replace with arguments = argument.split(", ")
				candidates = {}  # Dictionary of candidates that can be voted for
				candidates_string = ""

				# Embed
				title = discord.Embed.Empty
				colour = self.get_server_colour(guild.id)

				# Config
				winner = "highest"
				anonymous = False

				try:
					# Analyse argument
					for argument in arguments:
						argument = argument.strip()
						argument = argument.split("=")
						# print("Argument 0, 1:", argument[0], argument[1])
						poll_time = str(datetime.now())
						if argument[0] == "title":
							title = argument[1]
						elif argument[0] == "colour":
							try:
								colour = int(argument[1][-6:], 16)
							except ValueError:
								if argument[1] in colours:
									colour = colours[argument[1]]
						elif argument[0] == "winner":
							winner = argument[1]
						elif argument[0] == "anonymous" or argument[0] == "anon":
							if argument[1].lower() == "true":
								anonymous = True
						else:
							emoji = argument[1].rstrip()
							if not (emoji in candidates):
								candidates[emoji] = argument[0]
								candidates_string += argument[1] + " - " + argument[0] + "\n"
							else:
								logger.debug("Duplicate emoji in poll detected")
								await message.channel.send("Please only use an emoji once per poll")
				except Exception as exception:
					logger.error(f"Failed to read poll command. Exception \"{type(exception).__name__}\" : {exception.args[0]}\n")
					await message.channel.send("The poll command could not be read. Please format as `\"title\" = question, \"option\" = emoji, (\"anonymous\" = True/False)`")

				# Create and send poll embed
				embed_poll = discord.Embed(title=title, description=candidates_string, colour=colour)
				if anonymous:  # Makes embed with buttons for anonymous voting
					# Adds buttons
					buttons = []
					for candidate in candidates:
						buttons.append(create_button(style=ButtonStyle.blue, label=candidates[candidate], emoji=candidate, custom_id="poll:" + candidate))
					components = populate_actionrows(buttons) # Puts buttons in to rows of 5 or less
					poll_message = await message.channel.send(embed=embed_poll, components=components)

					# Setup candidates dict for recording votes so people can't vote multiple times
					#for candidate in candidates:
					#	candidates[candidate] = {"name": candidates[candidate], "voters": []}
					candidates = {}

				else:  # Makes embed with reactions for open voting
					poll_message = await message.channel.send(embed=embed_poll)
					# Adds reactions
					for candidate in candidates:
						# print("Candidate: " + str(candidate))
						try:
							await poll_message.add_reaction(candidate)
						except discord.errors.HTTPException:
							await poll_message.channel.send("Please format as `title = question, \"option\" = emoji, (anonymous = True/False)`")
							await poll_message.delete()

				self.poll[str(message.guild.id)].update(
					{
						str(poll_message.id): {
							"title": title,
							"voters": candidates,
							"config":
								{
									"winner": winner,
									"anonymous": anonymous,
									"multi": True
								}
						}
					}
				)

				logger.debug(f"New poll:{self.poll[str(message.guild.id)]}")

			# Review confessions command
			if message.content == "review confessions" or message.content == "confessions":
				logger.info("`review confessions` called by " + message.author.name)  # Event log
				if "confessions" in self.data["servers"][str(guild.id)]:
					for confession in client.data["servers"][str(guild.id)]["confessions"]["messages"]:
						confession_message = client.data["servers"][str(guild.id)]["confessions"]["messages"][confession]
						image_url = re.match("^[https:\/\/|http:\/\/].*[gif|png|jpg|jpeg|webp]$",confession_message)

						confession_embed = discord.Embed(title="Review Confession No." + confession, description="> " + confession_message, colour=0XF57E3D)
						if image_url != None:
							confession_embed.set_image(url=image_url.string)
						confession_embed.set_footer(text="This message is here to be reviewed. Please say if the content is inappropriate!", icon_url=guild.icon)
						button = (create_button(style=ButtonStyle.red, label="Remove", custom_id="confession:" + confession))
						components = [create_actionrow(*[button])]
						await message.channel.send(embed=confession_embed, components=components)
					if len(client.data["servers"][str(guild.id)]["confessions"]["messages"]) != 0:
						return
				await message.channel.send("No confessions to review")

			# Post confessions command
			if message.content == "post confessions":
				logger.info("`post confessions` called by " + message.author.name)  # Event log
				if "confessions" in self.data["servers"][str(guild.id)]:
					for confession in client.data["servers"][str(guild.id)]["confessions"]["messages"]:
						if confession == "1024":
							con_number = "-1023"
							con_start = ">"
						else:
							con_number = confession
							con_start = "> "

						confession_message = client.data["servers"][str(guild.id)]["confessions"]["messages"][confession]
						image_url = re.match("^[https:\/\/|http:\/\/].*[gif|png|jpg|jpeg|webp]$", confession_message)

						confession_embed = discord.Embed(title="Confession No." + con_number, description= con_start + client.data["servers"][str(guild.id)]["confessions"]["messages"][confession], colour=self.get_server_colour(guild.id))
						if image_url != None:
							confession_embed.set_image(url=image_url.string)
						confession_embed.set_footer(text="/confess to submit your anonymous confession",  icon_url=guild.icon)
						await message.channel.send(embed=confession_embed)

					self.data["servers"][str(guild.id)]["confessions"]["messages"] = {}
					self.update_data()
					await message.delete()

			# Settings command
			if message.content == "settings":
				logger.info("`settings` called by " + message.author.name)  # Event log
				await message.channel.send(content="**Settings**")
				channel_options = []
				if len(guild.text_channels) > 25:
					channels = guild.text_channels[:25]
				else:
					channels = guild.text_channels

				# Announcement channel selection
				# Run for 25 channel blocks
				for x in range(len(guild.text_channels)//25):
					channel_options = []
					for channel in guild.text_channels[x*25:(x+1)*25]:
						if channel.id == self.data["servers"][str(guild.id)]["config"]["announcements channel id"]:
							channel_options.append(create_select_option(label=channel.name, value=str(channel.id), default=True))
						else:
							channel_options.append(create_select_option(label=channel.name, value=str(channel.id)))
					announcement_channel_select = create_select(channel_options, custom_id="settings:announcements channel id")
					components = [create_actionrow(*[announcement_channel_select])]
					await message.channel.send(content="Announcement Channel:", components=components)

				# Final run
				channel_options = []
				for channel in guild.text_channels[-(len(guild.text_channels)%25):]:
					if channel.id == self.data["servers"][str(guild.id)]["config"]["announcements channel id"]:
						channel_options.append(
							create_select_option(label=channel.name, value=str(channel.id), default=True))
					else:
						channel_options.append(create_select_option(label=channel.name, value=str(channel.id)))
				announcement_channel_select = create_select(channel_options,custom_id="settings:announcements channel id")
				components = [create_actionrow(*[announcement_channel_select])]
				await message.channel.send(content="Announcement Channel:", components=components)

				no_announcement_button = create_button(style=ButtonStyle.red, label="Turn off announcements", emoji="❎", custom_id="settings:announcements channel id")
				components = [create_actionrow(*[no_announcement_button])]
				await message.channel.send(content="Announcement Channel:", components=components)

				# Colour theme selection
				colour_options = []
				for colour in colours:
					colour_options.append(create_select_option(label=colour, value=str(colours[colour])))
				colour_select = create_select(colour_options, custom_id="settings:colour theme")
				components = [create_actionrow(*[colour_select])]
				await message.channel.send(content="Server Colour Theme:", components=components)

				# Delete logging
				dlogging_options = []
				dlogging_options.append(create_select_option(label="Off", value=0))
				dlogging_options.append(create_select_option(label="Own messages", value=1))
				dlogging_options.append(create_select_option(label="All messages (as if I would do this)", value=2))
				dlogging_select = create_select(dlogging_options, custom_id="settings:delete_logging")
				components = [create_actionrow(*[dlogging_select])]
				await message.channel.send(content="Delete logging options:", components=components)

				toggle_role_archiving = create_button(style=ButtonStyle.blue, label="Toggle role archiving", emoji="❎", custom_id="settings:role archiving")
				components = [create_actionrow(*[toggle_role_archiving])]
				await message.channel.send(content="Role Archiving:", components=components)

		# If the message was sent by the developers
		if message.author.id in DEVELOPERS:

			# Announce command
			if message.content.startswith("announce"):
				logger.info("`announce` called by " + message.author.name)  # Event log
				if len(message.content) > len("announce "):
					argument = message.content[len("announce "):]
					await self.announce(argument)
				else:
					logger.error("No announce argument supplied")  # Event log

			# Report command
			if message.content.startswith("report"):
				logger.info("`report` called by " + message.author.name)  # Event log

				if len(message.content) > len("report "):
					argument = message.content[len("report "):]
					try:
						if self.data["bot settings"]["safety"]:
							logger.debug("safety protected against report command")
						else:
							# Searches for illegal terms in query to stop exposing sensitive data or crashing the bot
							illegal = ["token", "config", "self.run", "vars", "help"]
							for term in illegal:
								if term in argument.lower():
									logger.info("ILLEGAL QUERY: " + argument + " is requested to be reported to " + guild.name + " ID:" + str(guild.id) + " to " + message.channel.name + " channel ID:" + str(message.channel.id))
									await message.channel.send("This variable is private and should never be shared. Manual access will be required instead.\n**The request of this variable has been logged!**")
									await self.get_channel(REPORT_CHANNEL).send(f"Report of `{argument}` used in {guild.name} by {message.author.mention}")
									return

							logger.info("LEGAL QUERY: " + argument + " is requested to be reported to " + guild.name + " ID:" + str(guild.id) + " to " + message.channel.name + " channel ID:" + str(message.channel.id))
							answer = str(eval(argument))
							# Checks answer
							if "token" in answer.lower():
								logger.info("ILLEGAL ANSWER: " + argument + " is requested with an illegal answer to be reported to " + guild.name + " ID:" + str(guild.id) + " to " + message.channel.name + " channel ID:" + str(message.channel.id))
								await message.channel.send("This variable is private and should never be shared. Manual access will be required instead.\n**The request of this variable has been logged!**")
							else:
								await message.channel.send(f"`{answer}`")
					except Exception as e:
						await message.channel.send("Something went wrong when trying to get the value of " + argument)
						# TODO make this have a safety level
						await message.channel.send(e)
				else:
					logger.error("Nothing specified to report")  # Event log
				dev_mentions = ""
				# for dev in DEVELOPERS:
				#	dev_mentions += self.get_user(dev).mention
				await self.announce(dev_mentions + f"Report of `{argument}` used in {guild.name} by {message.author.mention}","alert")

			# Config command
			if message.content == "config":
				logger.info("`config` called by " + message.author.name)  # Event log
				await message.channel.send(content="**Config**")
				if "add info" in self.data["bot settings"] and self.data["bot settings"]["add info"]:
					additional_info = f"\nLatency: {str(int(client.latency // 1))}.{str(client.latency % 1)[2:5]}s\nUptime: {self.get_uptime()}.\nLast disconnect: {str(self.last_disconnect)[0:16]}"
					locate_embed = discord.Embed(title="Additional Info:", description=additional_info,colour=int(self.get_server_colour(message.guild.id)))
					locate_embed.set_footer(text=f"Command called by {message.author.name}",icon_url=guild.icon)
					await message.channel.send(content=f"This instance of {VERSION} is being run on **{hostname}**, IP address **{socket.gethostbyname(hostname)}**",embed=locate_embed)

				joke_button = create_button(style=ButtonStyle.blue, label="Jokes", emoji="😂", custom_id="config:jokes")
				components = [create_actionrow(*[joke_button])]
				await message.channel.send(content="Jokes: " + str(self.data["bot settings"]["jokes"]), components=components)

				safety_button = create_button(style=ButtonStyle.blue, label="safety", emoji="🦺", custom_id="config:safety")
				components = [create_actionrow(*[safety_button])]
				await message.channel.send(content="safety: " + str(self.data["bot settings"]["safety"]), components=components)

				add_info_button = create_button(style=ButtonStyle.blue, label="Show Additional Info", emoji="🩺",custom_id="config:add info")
				components = [create_actionrow(*[add_info_button])]
				if "add info" in self.data["bot settings"]:
					await message.channel.send(content="Add info: " + str(self.data["bot settings"]["add info"]),components=components)
				else:
					await message.channel.send(content="Add info: False", components=components)

				upload_data_button = create_button(style=ButtonStyle.grey, label="Data", emoji="🔡", custom_id="config:send:data.json")
				upload_log_button = create_button(style=ButtonStyle.grey, label="Log", emoji="📄", custom_id="config:send:log_file.log")
				components = [create_actionrow(*[upload_data_button, upload_log_button])]
				await message.channel.send(content="Files: ", components=components)

				kill_button = create_button(style=ButtonStyle.red, label="Kill", emoji="🔪",custom_id="config:kill")
				components = [create_actionrow(*[kill_button])]
				await message.channel.send(content="Control: ", components=components)

				#activity_button = create_button(style=ButtonStyle.green, label="Activity", emoji="🏃‍♀️", custom_id="config:modal:activity")
				#components = [create_actionrow(*[activity_button])]
				#await message.channel.send(content="Activity: ", components=components)


			# Locate command
			if message.content == "locate":
				logger.info("`locate` called by " + message.author.name)  # Event log

				main_info = f"This instance of {VERSION} is being run on **{hostname}**, IP address **{socket.gethostbyname(hostname)}**"
				if "add info" in self.data["bot settings"] and self.data["bot settings"]["add info"]:
					additional_info = f"\nLatency: {str(int(client.latency // 1)) }.{str(client.latency % 1)[2:5] }s\nUptime: {self.get_uptime() }.\nLast disconnect: {str(self.last_disconnect)[0:16]}"
					locate_embed = discord.Embed(title="Additional Info:", description=additional_info, colour=int(self.get_server_colour(message.guild.id)))
					locate_embed.set_footer(text=f"Command called by {message.author.name}", icon_url=guild.icon.with_size(128))
					await message.channel.send(content=main_info,embed=locate_embed)
				else:
					await message.channel.send(content=main_info)

			# Kill command
			if message.content.startswith("kill"):
				logger.info("`kill` called by " + message.author.name)  # Event log
				if self.data["bot settings"]["jokes"] is True:
					await message.channel.send("Doggie down")

				reason = message.content[len("kill"):]
				death_note = "**" + self.user.name + " offline**\nReason for shutdown: " + reason

				# Send kill announcement
				await self.announce(death_note, announcement_type="kill")

				await message.channel.send(death_note + "\n" + "Uptime: " + self.get_uptime() + ".")
				await client.close()




	async def on_message_delete(self, message):
		if message.author.id == self.user.id:
			async for entry in message.guild.audit_logs(limit=3):
				if entry.target.id == self.user.id and entry.user.id != self.user.id:
					if str(entry.action) == "AuditLogAction.message_delete":
						logger.info(entry.user.name+" deleted my message: "+message.content)
						config = client.data["servers"][str(message.guild.id)]["config"]
						if "delete_logging" in config:
							if config["delete_logging"] >= 1: # To allow for different level in the future
								try:
									await message.channel.send(entry.user.name+" deleted my message: |"+message.content+"|")
								except Exception as exception:
									logger.debug("Deleted message couldn't be logged in channel " + ". Exception: " + str(exception))  # Event log
					break

	async def on_member_join(self, member):
		"""Runs when a member joins.
		Sends the member a message welcome message."""

		logger.debug("Member " + member.name + " joined guild " + member.guild.name)  # Event log
		# Checks if user has roles archived
		config = client.data["servers"][str(member.guild.id)]["config"]
		if "member archive" in self.data["servers"][str(member.guild.id)] and config["role archiving"] == True:
			if str(member.id) in self.data["servers"][str(member.guild.id)]["member archive"]:
				# Returning member
				try:
					await member.create_dm()
					await member.dm_channel.send(f"Welcome back to {member.guild.name}, {member.name}. You should get all your old roles back!")
					logger.debug("Sent welcome message for " + member.guild.name + " to " + member.name)  # Event log
					rolesList = self.data["servers"][str(member.guild.id)]["member archive"][str(member.id)]
					logger.debug(f"Adding {len(rolesList)} roles to {member.name} that were saved on {member.guild.name}")
					for r in rolesList:
						role = member.guild.get_role(r)
						await member.add_roles(role)
					del self.data["servers"][str(member.guild.id)]["member archive"][str(member.id)]  # Removes archived data now that the user has rejoined
					self.update_data()
				except Exception as exception:
					# If user has impeded direct messages
					logger.debug("Failed to send welcome message for " + member.guild.name + " to " + member.name + ". Exception: " + str(exception))  # Event log
				return
		else:
			logger.debug(f"{member.name} will not be given back any roles they may have had previously due to settings or lack of their existence")
		# Default no-role archiving response
		try:
			await member.create_dm()
			await member.dm_channel.send("Welcome to " + member.guild.name + ", " + member.name + ".")
			logger.debug("Sent welcome message for " + member.guild.name + " to " + member.name)  # Event log
		except Exception as exception:
			# If user has impeded direct messages
			logger.debug(
				"Failed to send welcome message for " + member.guild.name + " to " + member.name + ". Exception: " + str(
					exception))  # Event log

	async def on_member_remove(self, member):
		"""Runs when a member leaves.
		Sends the member a goodbye message."""

		logger.debug("Member " + member.name + " left guild " + member.guild.name)  # Event log
		try:

			config = client.data["servers"][str(member.guild.id)]["config"]
			if config["role archiving"] == True:
				await member.create_dm()
				await member.dm_channel.send(f"Goodbye. We'll try and save your roles on {member.guild.name} in case you return ;)")
				logger.debug("Sent goodbye message for " + member.guild.name + " to " + member.name)  # Event log
				# Saves the leaving user's roles in data.json
				roleList = member.roles
				if "member archive" not in self.data["servers"][str(member.guild.id)]:
					self.data["servers"][str(member.guild.id)]["member archive"] = {}
				formattedRoleList = []
				for role in roleList:
					if role.name != "@everyone":
						formattedRoleList.append(role.id)
				self.data["servers"][str(member.guild.id)]["member archive"][str(member.id)] = formattedRoleList
				self.update_data()
			else:
				await member.create_dm()
				await member.dm_channel.send(f"Goodbye {member.guild.name} ;)")
				logger.debug("Sent goodbye message for " + member.guild.name + " to " + member.name)  # Event log

		except Exception as exception:
			# If the user has impeded direct messages
			logger.debug("Failed to send goodbye message for " + member.guild.name + " to " + member.name)  # Event log

	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		"""Gives a role based on a reaction emoji."""

		guild = self.get_guild(payload.guild_id)
		# Make sure that the message the user is reacting to is the one we care about. Would be removed because dumb but you've integrated the whole thing way too much. This is not very modular at all!
		reaction_usage = "none"

		# Role reaction check
		for category in self.data["servers"][str(guild.id)]["roles"]["categories"]:
			if payload.message_id == self.data["servers"][str(payload.guild_id)]["roles"]["categories"][category]["message id"]:  # How does this work? Surely you should say "in", not ==. Yeah, think so but why wasn't this tested
				reaction_usage = "roles"
				logger.debug("Role message reacted to")
				break
		if reaction_usage == "none":  # No functionality found yet, keep checking
			# Poll reaction check
			try:
				for message in self.poll[str(guild.id)]:
					if str(payload.message_id) == message:
						if not self.poll[str(guild.id)][message]["config"]["anonymous"]:  # Anonymous messages don't use reactions
							reaction_usage = "polls"
							logger.debug("Poll message reacted to")
							break
			except KeyError:
				logger.debug("Couldn't find some data in polls")

			if reaction_usage == "none":  # No functionality found yet, keep checking
				# Purge reaction check
				if payload.message_id in self.purge_messages:  # Did a slightly different system that's doubly efficient than your weird check system
					logger.debug("Purge message reacted to")
					if guild.get_member(payload.user_id).guild_permissions.administrator:  # If has admin perms
						logger.debug("Purge confirmed by admin")
						if str(payload.emoji) == "👍":
							try:
								await client.get_channel(payload.channel_id).purge(limit=self.purge_messages[payload.message_id])
								logger.info("Purge complete in " + client.get_channel(payload.channel_id).name + " < " + client.get_guild(payload.guild_id).name)
								await client.get_channel(payload.channel_id).send("Channel purged " + str(self.purge_messages[payload.message_id]) + " messages")
								self.purge_messages.pop(payload.message_id)
							except Exception as e:
								await client.get_channel(payload.channel_id).send("Channel failed the purge. There were possibly too many messages.")

		if reaction_usage == "none":
			return
		# Make sure the user isn't the bot.
		if payload.member.id == self.user.id:  # was payload.author
			return

		# Check if we're still in the guild and it's cached.
		if guild is None:
			return

		if reaction_usage == "roles":
			# If the emoji isn't the one we care about then delete it and exit as well.
			# Checks payload for role reaction and then end poll reaction
			role_id = -1
			for category in self.data["servers"][str(guild.id)]["roles"]["categories"]:  # For category in list
				for role in self.data["servers"][str(guild.id)]["roles"]["categories"][category]["list"]:  # For role in category
					if self.data["servers"][str(guild.id)]["roles"]["categories"][category]["list"][role]["emoji"] == str(payload.emoji):
						role_id = int(role)
						try:
							verify_role = self.data["servers"][str(guild.id)]["roles"]["verify role"]
							if verify_role != 0:
								role = guild.get_role(verify_role)
								await payload.member.add_roles(role)
								logger.debug("Verified " + payload.member.name + " on " + guild.name)
						except KeyError:
							logger.debug("No verification role found in " + guild.name)
						break

			# The deleter
			if role_id == -1:
				# Not very efficient... comes from (https://stackoverflow.com/questions/63418818/python-discord-bot-python-clear-reaction-clears-all-reactions-instead-of-a-s)
				channel = await self.fetch_channel(payload.channel_id)
				message = await channel.fetch_message(payload.message_id)
				reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
				await reaction.remove(payload.member)

				return

			# Make sure the role still exists and is valid.
			role = guild.get_role(role_id)
			if role is None:
				return

			# Finally, add the role.
			try:
				await payload.member.add_roles(role)
				logger.info(f"Role `{role.name}` added to {payload.member.name}")  # Event log
			# If we want to do something in case of errors we'd do it here
			except Exception as exception:
				logger.error("Failed to add role " + role.name + " to " + payload.member.name + ". Exception: " + str(exception))  # Event log

		if reaction_usage == "polls":
			if str(payload.emoji) == "🔚":

				logger.debug("Poll ending")
				logger.debug("Poll identified for termination")
				channel = await self.fetch_channel(payload.channel_id)
				message = await channel.fetch_message(payload.message_id)
				reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
				await reaction.remove(payload.member)  # Removes end emoji
				await self.terminate_poll(message)
			else:
				valid_emoji = False
				for message in self.poll[str(payload.guild_id)]:
					if str(payload.emoji) in self.poll[str(payload.guild_id)][message]["voters"]:  # Deletes emojis not related to poll options
						valid_emoji = True
				if not valid_emoji:
					logger.debug("Unwanted emoji on poll found")
					channel = await self.fetch_channel(payload.channel_id)
					message = await channel.fetch_message(payload.message_id)
					await message.remove_reaction(payload.emoji, payload.member)
				else:
					logger.debug("Wanted emoji on poll found")

	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		"""Runs when a reaction is removed.
		If the message and emoji are relevant, removes a role based on the reaction emoji."""

		guild = self.get_guild(payload.guild_id)

		# If the roles have been set up
		if len(self.data["servers"][str(guild.id)]["roles"]["categories"]) != 0:

			# Make sure that the message the user is reacting to is the one we care about
			message_relevant = False
			for category in self.data["servers"][str(guild.id)]["roles"]["categories"]:
				if payload.message_id == self.data["servers"][str(payload.guild_id)]["roles"]["categories"][category]["message id"]:
					message_relevant = True
					logger.debug("Relevant message reacted to")
					break
			if message_relevant is False:
				return

			# The payload for `on_raw_reaction_remove` does not provide `.member`
			# so we must get the member ourselves from the payload's `.user_id`

			# Make sure the member still exists and is valid
			member = guild.get_member(payload.user_id)
			if member is None:
				return

			# Make sure the user isn't the bot
			if member.id == self.user.id:
				return

			# Check if we're still in the guild and it's cached
			if guild is None:
				return

			# If the emoji isn't the one we care about then exit as well
			role_id = -1
			for category in self.data["servers"][str(guild.id)]["roles"]["categories"]:  # For category in list
				for role in self.data["servers"][str(guild.id)]["roles"]["categories"][category]["list"]:  # For role in category
					if self.data["servers"][str(guild.id)]["roles"]["categories"][category]["list"][role]["emoji"] == str(payload.emoji):
						role_id = int(role)
						break
			if role_id == -1:
				return

			# Make sure the role still exists and is valid
			role = guild.get_role(role_id)
			if role is None:
				return

			# Finally, remove the role
			try:
				await member.remove_roles(role)
				logger.info("Role `" + role.name + "` removed from " + member.name)  # Event log
			# If we want to do something in case of errors we'd do it here
			except Exception as exception:
				logger.error("Failed to remove role " + role.name + " from " + payload.member.name + ". Exception: " + str(exception))  # Event log

		# If the roles haven't been set up
		else:
			logger.debug("Roles have not been set up for " + str(payload.guild.id))  # Event log
			# Send an error message
			await payload.channel.send("Uh oh, you haven't set up any roles! Get a server admin to set them up at https://www.lingscars.com/")


# Main body
if __name__ == "__main__":

	try:
		setup_config()
		intents = discord.Intents.all()
		intents.members = True
		client = MyClient(intents=intents, application_id=844950029369737238)
		# slash = SlashCommand(client, sync_commands=True)

		guild_ids = []
		for guild in client.guilds:
			guild_ids += guild.id

		@tree.command(
			name="ping2",
			description=f"Ping the bot to obtain latency."
		)
		async def _ping(interaction):
			logger.debug("`/ping` called by " + interaction.author.name)
			await interaction.response.send_message(content=str(int(client.latency // 1)) + "." + str(client.latency % 1)[2:5]+"s")
		# @client.event
		# async def on_ready():
		# 	await tree.sync()
		# 	print("Ready!")
		# @slash.slash(
		# 	name="ping",
		# 	description="Ping the bot to obtain latency.",
		# 	guild_ids=guild_ids
		# )
		# async def _ping(ctx):
		# 	"""Runs on the ping slash command."""
		#
		# 	logger.debug("`/ping` called by " + ctx.author.name)
		#
		# 	try:
		# 		await ctx.send(content=str(int(client.latency // 1)) + "." + str(client.latency % 1)[2:5]+"s")
		# 	except Exception as exception:
		# 		logger.error("Failed to run `/ping` in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception))
		#
		#
		# @slash.slash(
		# 	name="confess",
		# 	description="Use the command to send an anonymous message to be posted later",
		# 	options=[
		# 		create_option(
		# 			name="confession",
		# 			description="Your message",
		# 			option_type=3,
		# 			required=True
		# 		)
		# 	],
		# 	guild_ids=guild_ids
		# )
		# async def _confess(ctx, confession, image=None):
		# 	"""Runs on the confession slash command."""
		#
		# 	logger.debug("`/confess` called anonymously")
		#
		# 	#try:
		# 	server_data = client.data["servers"][str(ctx.guild.id)]  # Used for easy reference
		#
		# 	if "confessions" not in server_data:
		# 		server_data.update({"confessions": {"metadata": {"count": 0}, "messages": {}}})
		#
		# 	confession_count = str(server_data["confessions"]["metadata"]["count"])
		# 	# Checks for spam of same confession
		# 	flag_spam = False
		# 	if confession_count in server_data["confessions"]["messages"] and confession == server_data["confessions"]["messages"][confession_count]:
		# 		if str(int(confession_count)-1) in server_data["confessions"]["messages"] and confession == server_data["confessions"]["messages"][str(int(confession_count)-1)]:
		# 			await ctx.send(content="Repeated spam confessions identified automatically. Please refrain from making any further attempts.",hidden=False)
		# 			return
		# 		else:
		# 			flag_spam = True
		#
		# 	server_data["confessions"]["metadata"]["count"] += 1
		# 	confession_data = {str(server_data["confessions"]["metadata"]["count"]): confession}
		# 	server_data["confessions"]["messages"].update(confession_data)
		#
		# 	client.data["servers"][str(ctx.guild.id)] = server_data
		# 	client.update_data()
		#
		# 	await ctx.defer(hidden=True)
		# 	if flag_spam:
		# 		await ctx.send(content="This confession has been automatically identified as spam. Further attempts to spam confessions will result in your username being reported to admins.",hidden=True)
		# 	else:
		# 		await ctx.send(content="Thank you for your confession. The content may be reviewed before posting but will remain anonymous.", hidden=True)
		#
		# 	#except Exception as exception:
		# 	#	logger.error("Failed to run `/confess` in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception.args[0]))
		#
		#
		# @slash.slash(
		# 	name="question",
		# 	description="Ask Sirius a question",
		# 	options=[
		# 		create_option(
		# 			name="question",
		# 			description="Your question",
		# 			option_type=3,
		# 			required=True
		# 		)
		# 	],
		# 	guild_ids=guild_ids
		# )
		# async def _question(ctx, question):
		# 	"""Runs on the question slash command."""
		#
		# 	logger.debug("`/question` called by " + ctx.author.name)
		#
		# 	try:
		# 		reply = "**" + ctx.author.name + "**: *" + question + "*\n\n"
		# 		await ctx.send(content=reply + AI.question(question))
		#
		# 	except Exception as exception:
		# 		logger.error("Failed to run `/question` message in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception))
		#
		#
		# @slash.slash(
		# 	name="anonymous",
		# 	description="Say something in the channel anonymously",
		# 	options=[
		# 		create_option(
		# 			name="message",
		# 			description="Your message",
		# 			option_type=3,
		# 			required=True
		# 		)
		# 	],
		# 	guild_ids=guild_ids
		# )
		# async def _anonymous(ctx, message):
		# 	"""Runs on the anonymous message slash command."""
		#
		# 	logger.debug("`/anonymous` called by " + ctx.author.name)
		#
		# 	try:
		#
		# 		blacklist = ["@","nigger","nigga"]
		# 		if (any (word in message for word in blacklist)):
		# 			await ctx.send(content="Your message will not be sent due to its contents", hidden=True)
		# 		else:
		# 			await ctx.send(content="Your message will be sent anonymously", hidden=True)
		# 			await client.create_thread_message(ctx.channel_id,"**Anonymous**: *" + message + "*")
		#
		# 	except Exception as exception:
		# 		logger.error("Failed to run `/anonymous` message in " + ctx.guild.name + " (" + str(ctx.guild.id) + "). Exception: " + str(exception))
		#
		#
		# # admin_roles = [role for role in ctx.guild.roles if role.permissions.administrator]
		# @slash.slash(
		# 	name="purge",
		# 	description="Purge messages from the channel",
		# 	options=[
		# 		create_option(
		# 			name="count",
		# 			description="How many messages",
		# 			option_type=4,
		# 			required=True
		# 		)
		# 	],
		# 	guild_ids=guild_ids
		# )
		# async def _purge(ctx, count):
		# 	"""Runs on the purge slash command."""
		#
		# 	logger.debug("`/purge` called by " + ctx.author.name)
		#
		# 	if ctx.author.guild_permissions.administrator:
		# 		purge_button = create_button(style=ButtonStyle.danger, label="Purge " + str(count) + " messages?", custom_id="purge:" + str(count))
		# 		components = [create_actionrow(*[purge_button])]
		# 		await ctx.send(content="Purge " + str(count) + " messages?", components=components)
		# 	else:
		# 		await ctx.send("You do not have permissions to run this command", hidden=True)
		#
		# @slash.slash(
		# 	name="poll",
		# 	description="Create anonymous poll",
		# 	options=[
		# 		create_option(
		# 			name="question",
		# 			description="The poll's question",
		# 			option_type=3,
		# 			required=True
		# 		),
		# 		create_option(
		# 			name="option1",
		# 			description="...",
		# 			option_type=3,
		# 			required=True
		# 		),
		# 		create_option(
		# 			name="option2",
		# 			description="...",
		# 			option_type=3,
		# 			required=True
		# 		),
		# 		create_option(
		# 			name="option3",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option4",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option5",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option6",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option7",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option8",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option9",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		)
		# 	],
		# 	guild_ids=guild_ids
		# )
		# async def _poll(ctx, question, option1, option2, option3=None, option4=None, option5=None, option6=None,option7=None, option8=None, option9=None):
		# 	"""Poll command."""
		#
		# 	logger.debug(f"`/poll` called by {ctx.author.name}")
		# 	try:
		# 		embed = discord.Embed(title=f"> {question}", description="Select or unselect an option below:",colour=int(client.get_server_colour(ctx.guild.id)))
		# 		options = list(
		# 			filter(None, [option1, option2, option3, option4, option5, option6, option7, option8, option9]))
		# 		buttons = []
		# 		for option in options:
		# 			buttons.append(create_button(style=ButtonStyle.blue, label=option, custom_id="poll:" + option))
		# 		components = populate_actionrows(buttons)
		# 		poll_message = await ctx.send(embed=embed, components=components)
		#
		# 		# Setup candidates dict for recording votes so people can't vote multiple times
		# 		candidates = {} # Options dictionary
		# 		for option in options:
		# 			candidates[option] = {"name": option, "voters": []}
		#
		# 		client.poll[str(ctx.guild.id)].update(
		# 			{
		# 				str(poll_message.id): {
		# 					"title": question,
		# 					"voters": {},
		# 					"config":
		# 						{
		# 							"winner": "highest",
		# 							"anonymous": True,
		# 							"multi": False
		# 						}
		# 				}
		# 			}
		# 		)
		# 		logger.debug(f"New poll:{client.poll[str(ctx.guild.id)]}")
		#
		# 	except Exception as exception:
		# 		logger.error(f"Failed to run `/poll` in {ctx.guild.name} ({ctx.guild.id}). Exception: {exception}")
		# 		await ctx.send("Failed to create poll. Check there are no duplicate values!",hidden=True)
		#
		# @slash.slash(
		# 	name="multi_poll",
		# 	description="Create anonymous multi poll. (Users can vote for multiple options)",
		# 	options=[
		# 		create_option(
		# 			name="question",
		# 			description="The poll's question",
		# 			option_type=3,
		# 			required=True
		# 		),
		# 		create_option(
		# 			name="option1",
		# 			description="...",
		# 			option_type=3,
		# 			required=True
		# 		),
		# 		create_option(
		# 			name="option2",
		# 			description="...",
		# 			option_type=3,
		# 			required=True
		# 		),
		# 		create_option(
		# 			name="option3",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option4",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option5",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option6",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option7",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option8",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		),
		# 		create_option(
		# 			name="option9",
		# 			description="...",
		# 			option_type=3,
		# 			required=False
		# 		)
		# 	],
		# 	guild_ids=guild_ids
		# )
		# async def _multi_poll(ctx, question, option1, option2, option3=None, option4=None, option5=None, option6=None,option7=None, option8=None, option9=None):
		# 	"""Poll command."""
		#
		# 	logger.debug(f"`/multi_poll` called by {ctx.author.name}")
		# 	try:
		# 		embed = discord.Embed(title=f"> {question}", description="Select or unselect an option below:",colour=int(client.get_server_colour(ctx.guild.id)))
		# 		options = list(
		# 			filter(None, [option1, option2, option3, option4, option5, option6, option7, option8, option9]))
		# 		buttons = []
		# 		for option in options:
		# 			buttons.append(create_button(style=ButtonStyle.blue, label=option, custom_id="poll:" + option))
		# 		components = populate_actionrows(buttons)
		# 		poll_message = await ctx.send(embed=embed, components=components)
		#
		# 		# Setup candidates dict for recording votes so people can't vote multiple times
		# 		candidates = {} # Options dictionary
		# 		for option in options:
		# 			candidates[option] = {"name": option, "voters": []}
		#
		# 		client.poll[str(ctx.guild.id)].update(
		# 			{
		# 				str(poll_message.id): {
		# 					"title": question,
		# 					"voters": {},
		# 					"config":
		# 						{
		# 							"winner": "highest",
		# 							"anonymous": True,
		# 							"multi": True
		# 						}
		# 				}
		# 			}
		# 		)
		# 		logger.debug(f"New poll:{client.poll[str(ctx.guild.id)]}")
		#
		# 	except Exception as exception:
		# 		logger.error(f"Failed to run `/multi_poll` in {ctx.guild.name} ({ctx.guild.id}). Exception: {exception}")
		# 		await ctx.send("Failed to create multi poll. Check there are no duplicate values!",hidden=True)
		#
		#
		# @slash.context_menu(
		# 	target=ContextMenuType.MESSAGE,
		# 	name="Close Poll",
		# 	guild_ids=guild_ids
		# )
		# async def _close_poll(ctx: MenuContext):
		# 	if str(ctx.target_id) in client.poll[str(ctx.target_message.guild.id)]: # Checks message is in self.poll
		# 		poll = client.poll[str(ctx.guild.id)][str(ctx.target_id)]
		# 		counts = []
		# 		highest_option = ""
		# 		highest_count = 0
		# 		results_dict = {}
		# 		# Compiles results for each option
		# 		for voter in poll["voters"]:
		# 			if poll["config"]["multi"]:
		# 				selected_options = poll["voters"][voter]  # Option(s) selected by voter
		# 			else:
		# 				selected_options = [poll["voters"][voter]]  # Makes option into list
		# 			for selected_option in selected_options:
		# 				if selected_option not in results_dict:
		# 					results_dict[selected_option] = 0
		# 				results_dict[selected_option] += 1
		#
		# 		# Uses results dict to find highest scorer
		# 		for option in results_dict:
		# 			count = results_dict[option]
		# 			counts.append(str(count))
		# 			if count > highest_count:
		# 				highest_count = count
		# 				highest_option = option
		#
		# 		title = str(poll["title"])
		# 		if title == "Embed.Empty":
		# 			title = ""
		# 		embed_results = discord.Embed(title=f"Results of: \"{title}\"",colour=client.get_server_colour(ctx.guild_id))
		# 		embed_results.add_field(name="Options", value="\n".join(results_dict.keys()), inline=True)
		# 		embed_results.add_field(name="Count", value="\n".join(counts), inline=True)
		# 		if poll["config"]["winner"] == "highest":  # Winner is shown as the highest scoring candidate
		# 			embed_results.add_field(name="Winner", value=(highest_option + " Score: " + str(highest_count)), inline=False)
		# 		client.poll[str(ctx.guild.id)].pop(str(ctx.target_id))  # Removes poll entry from dictionary
		# 		await ctx.send(embeds=[embed_results])  # Sends the results embed
		# 	else:
		# 		await ctx.send(content="This is not a poll", hidden=True)
		#
		#
		# # Buttons...
		# # The following must be tested:
		# #     - Bots cannot press buttons
		# #     - What happens when the bot isn't in the guild or the guild isn't cached (see
		# #       on_raw_reaction_add for details)
		# @client.event
		# async def on_component(ctx):
		# 	"""Runs on component use."""
		# 	logger.debug("Component used by " + ctx.author.name)
		#
		# 	guild = ctx.origin_message.guild
		#
		# 	if ctx.custom_id.startswith("poll"):
		#
		# 		logger.debug(f"Anonymous poll vote by {ctx.author.name}")
		# 		option = ctx.custom_id[len("poll:"):]
		#
		# 		if str(ctx.origin_message.id) in client.poll[str(guild.id)]:
		# 			poll = client.poll[str(guild.id)][str(ctx.origin_message.id)]
		# 		else:
		# 			await ctx.send(content=f"This poll is closed", hidden=True)
		# 			return
		#
		# 		# If the user hasn't voted before
		# 		if ctx.author.id not in poll["voters"]:
		# 			if poll["config"]["multi"]:
		# 				poll["voters"][ctx.author.id] = [option]
		# 				await ctx.send(content=f"Gave a vote to {option}", hidden=True)
		# 			else:
		# 				poll["voters"][ctx.author.id] = option
		# 				await ctx.send(content=f"Gave your vote to {option}", hidden=True)
		# 		else:
		# 			if poll["config"]["multi"]:
		# 				if option in poll["voters"][ctx.author.id]:
		# 					poll["voters"][ctx.author.id].remove(option)
		# 					await ctx.send(content=f"Removed your vote for {option}", hidden=True)
		# 				else:
		# 					poll["voters"][ctx.author.id].append(option)
		# 					await ctx.send(content=f"Gave a vote to {option}", hidden=True)
		# 			else:
		# 				# If the user is changing their vote
		# 				if poll["voters"][ctx.author.id] != option:
		# 					poll["voters"][ctx.author.id] = option
		# 					await ctx.send(content=f"Changed your vote to {option}", hidden=True)
		# 				# If the user is removing their vote
		# 				else:
		# 					del poll["voters"][ctx.author.id]
		# 					await ctx.send(content=f"Removed your vote for {option}", hidden=True)
		#
		#
		# 	elif ctx.custom_id.startswith("confession"):
		# 		id = ctx.custom_id[len("confession:"):]
		# 		# Placeholder for other buttons functionality. Do not remove without consulting Pablo's forboding psionic foresight
		# 		if "confessions" in client.data["servers"][str(guild.id)]:
		# 			if ctx.author.guild_permissions.administrator:
		# 				logger.debug("Checking confessions about button press")
		# 				if id in client.data["servers"][str(guild.id)]["confessions"]["messages"]:  # Checks the button relates to a post stored in data
		# 					del client.data["servers"][str(guild.id)]["confessions"]["messages"][id]  # Removes the confession
		# 					logger.info("Confession No." + id + " removed from guild " + guild.name + " by " + ctx.author.name)
		# 					client.update_data()
		# 					await ctx.edit_origin(content="**This message has been removed by " + ctx.author.name + "**")
		# 				else:
		# 					await ctx.reply(content="This confession is not in data so has likely already been posted!")
		# 			else:
		# 				await ctx.edit_origin(content="**" + ctx.author.name + " **tried to remove this message without permissions!")
		#
		# 	elif ctx.custom_id.startswith("purge"):
		# 		if ctx.author.guild_permissions.administrator:
		# 			count = int(ctx.custom_id[len("purge:"):])
		# 			await ctx.channel.purge(limit=count)
		# 			logger.info("Purge complete in " + ctx.channel.name + " < " + ctx.guild.name)
		# 			await ctx.channel.send("Channel purged " + str(count) + " messages")
		# 		else:
		# 			await ctx.send("You do not have permissions to press this button", hidden=True)
		# 			logger.info(ctx.author.name + " tried to purge messages")
		#
		# 	elif ctx.custom_id.startswith("settings"):
		# 		config = client.data["servers"][str(guild.id)]["config"]
		# 		setting = ctx.custom_id[len("settings:"):]
		# 		logger.debug("Server setting '" + setting + "' of '" + guild.name + "' changed by " + ctx.author.name)
		# 		if ctx.author.guild_permissions.administrator:
		# 			if ctx.values == None:
		# 				if setting == "announcements channel id":
		# 					config[setting] = None
		# 				else: # Defaults to boolean toggle
		# 					if setting not in config:
		# 						config[setting] = False
		# 					config[setting] = not config[setting]  # Toggles boolean value
		# 					logger.info(f"Settings: {setting} changed to {str(config[setting])}")
		# 			else:
		# 				config[setting] = int(ctx.values[0])
		# 			await ctx.edit_origin(content=setting[0].upper() + setting[1:] + ": " + str(config[setting]))  # Makes first character capital of setting and shows the new setting
		# 			client.data["servers"][str(guild.id)]["config"] = config
		# 			client.update_data()
		# 			return
		#
		# 	elif ctx.custom_id.startswith("config"):
		# 		setting = ctx.custom_id[len("config:"):]
		# 		logger.debug("A config button pressed by " + ctx.author.name)
		# 		if ctx.author.id in DEVELOPERS:
		# 			if setting.startswith("send:"):  # All send file buttons dealt with here
		# 				setting = setting[len("send:"):]
		# 				await ctx.reply(content="File: " + setting, file=discord.File(r'' + setting))
		# 			if setting.startswith("modal:"):
		# 				print("there")
		# 				setting = setting[len("modal:"):]
		# 				class activity_modal(discord.ui.Modal):
		# 					def __init__(self, title, custom_id, current_activity):
		# 						super().__init__(title, custom_id)
		# 						self.add_item(discord.ui.InputText(label="Activity", value=current_activity.name))
		#
		# 					async def callback(self, ctx):
		# 						await ctx.reply("Activity updated", hidden=True)
		# 				print("here")
		# 				activity_modal = activity_modal(client.user.name + "'s Activity", "config:activity", client.activity)
		# 				await ctx.interaction.send_modal(activity_modal)
		# 			elif setting == "kill":
		# 				logger.info("`kill` called by " + ctx.author.name)  # Event log
		# 				if client.data["bot settings"]["jokes"] is True:
		# 					await ctx.channel.send("Doggie down")
		#
		# 				reason = "Killed from config panel"
		# 				death_note = "**" + client.user.name + " offline**\nReason for shutdown: " + reason
		#
		# 				# Send kill announcement
		# 				await client.announce(death_note, announcement_type="kill")
		#
		# 				await ctx.send(death_note + "\n" + "Uptime: " + client.get_uptime() + ".")
		# 				await client.close()
		# 			else:  # Toggle boolean commands here
		# 				bot_settings = client.data["bot settings"]
		# 				if setting not in bot_settings:
		# 					bot_settings[setting] = False
		# 				bot_settings[setting] = not bot_settings[setting]  # Toggles boolean value
		# 				logger.info("Config:" + setting + " changed to " + str(bot_settings[setting]))
		# 				client.update_data()
		# 				await ctx.edit_origin(content=setting[0].upper() + setting[1:] + ": " + str(bot_settings[setting]))  # Makes first character capital of setting and shows the new setting
		# 		else:
		# 			await ctx.send("You do not have permissions to press this button", hidden=True)
		# 			logger.info(ctx.author.name + " tried to change config")
		# 			return
		#
		# 	# If the roles functionality is enabled. THIS IS FUCKING BROKEN PABLO. WHY ARE YOU RETURNING WHEN IT COULD NOT BE ROLES!!!
		# 	elif "roles" in client.data["servers"][str(guild.id)]:
		# 		try:
		#
		# 			# Checks if the message is one of the server's roles messages
		# 			message_relevant = False
		# 			for category in client.data["servers"][str(guild.id)]["roles"]["categories"]:
		# 				if ctx.origin_message_id == client.data["servers"][str(guild.id)]["roles"]["categories"][category]["message id"]:
		# 					message_relevant = True
		# 					break
		#
		# 			# Checks if the role ID is one of the server's roles
		# 			role_id_found = False
		# 			for category in client.data["servers"][str(guild.id)]["roles"]["categories"]:
		# 				if ctx.custom_id in client.data["servers"][str(guild.id)]["roles"]["categories"][category]["list"]:
		# 					role_id_found = True
		# 					break
		# 			if role_id_found is False:
		# 				return
		#
		# 			# Checks if the role exists and is valid
		# 			role = guild.get_role(int(ctx.custom_id))
		# 			if role is None:
		# 				logger.debug("Could not get role with id: " + ctx.custom_id)
		# 				return
		#
		# 			# Adds the role if the user doesn't have it
		# 			if role not in ctx.author.roles:
		# 				await ctx.author.add_roles(role)
		# 				logger.debug(f"Added role `{role.name}` added to {ctx.author.name}")
		# 				await ctx.send(content="Added role: " + role.name, hidden=True)
		#
		# 			# Removes the role if the user already has it
		# 			else:
		# 				await ctx.author.remove_roles(role)
		# 				logger.debug(f"Removed role `{role.name}` from {ctx.author.name}")
		# 				await ctx.send(content="Removed role: " + role.name, hidden=True)
		#
		# 			""""# Send Pong response. Incipit Helminth...
		# 			with open("config.json") as file:
		# 				url = "https://discordapp.com/api/channels/{}/messages".format(ctx.origin_message.channel.id)
		# 				headers = {
		# 					"Authorization": "Bot {}".format(file.read()["token"]),
		# 					"Content-Type": "application/json"
		# 				}
		# 				JSON = {
		# 					"type": 1
		# 				}
		# 				r = requests.post(url, headers=headers, data=json.dumps(JSON))
		# 			logger.debug(r.status_code, r.reason)"""
		# 			return
		#
		# 		except Exception as exception:
		# 			logger.error("Failed to add role " + role.name + " to " + ctx.author.name + ". Exception: " + str(exception))  # Error: this may run even if the intention of the button press isn't to add a role
		# 		finally:
		# 			try:
		# 				verify_role = client.data["servers"][str(guild.id)]["roles"]["verify role"]
		# 				if verify_role != 0:
		# 					role = guild.get_role(verify_role)
		# 					await ctx.author.add_roles(role)
		# 					logger.debug("Verified " + ctx.author.name + " on " + guild.name)
		# 			except KeyError:
		# 				logger.debug("No verification role found in " + guild.name)
		# 			except Exception as exception:
		# 				logger.error("Verification failed: " + str(exception))
		# 			return

		client.run(TOKEN)

	except Exception as exception:
		logger.error(f"Exception \"{type(exception).__name__}\" : {exception.args[0]}\n")  # Event log