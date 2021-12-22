# Imports
import asyncio
import math
import random
from random import randint
from datetime import date, datetime
import time
import json
import socket
import discord
import re  # Delete this later


# Local imports
import requests
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_permission, remove_all_commands
from discord_slash.utils.manage_components import create_button, create_actionrow, ButtonStyle
from discord_slash.model import SlashCommandPermissionType

import AI # Imports the AI library
from clear_slash_commands import clearCommands
from log_handling import *
from imaging import generate_level_card


# Variables
VERSION = "1.3.0"
with open("config.json", encoding='utf-8') as file:
	config = json.load(file)
	DISCORD_TOKEN = config["token"]
	PREFIX = config["prefix"]
server_structure = {
	"config": {
		"admin role id": 0,
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
		"categories": {
			"CATEGORY NAME": {
				"message id": 0,
				"list": {}
			}
		}
	},
	"ranks": {}
}

# Servers specified
TheHatShop = 489893521176920076


# Definitions
class MyClient(discord.Client):

	def __init__(self, debug=False, level="DEBUG", *args, **kwargs):
		"""Constructor."""

		super().__init__(*args, **kwargs)
		self.connected = True # Starts true so on first boot, it won't think its restarted
		self.start_time = datetime.now()
		self.last_disconnect = datetime.now()
		self.data = {}
		self.cache = {}
		self.poll = {}
		self.purge_messages = {}
		self.activity = discord.Activity(type=discord.ActivityType.listening, name="the rain of purple Gods")

		# Print logs to the console too, for debugging
		if debug is True:
			x = logging.StreamHandler()  # Create new handler
			x.setLevel(level)  # Set handler level
			logger.addHandler(x)  # Add handler to logger

	def update_data(self):
		"""Writes the data attribute to the file."""

		try:
			with open("data.json", "w", encoding='utf-8') as file:
				json.dump(self.data, file, indent=4)
			logger.debug("Updated data.json")  # Event log
		except Exception as exception:
			logger.critical("Failed to update data.json. Exception: " + exception)  # Event log

	def initialise_guild(self, guild):
		"""Creates data for a new guild."""

		try:
			self.data["servers"][str(guild.id)] = server_structure
			self.cache[str(guild.id)] = {}
			self.poll[str(guild.id)] = {}

			# Write the updated data
			self.update_data()
			logger.info("Initialised guild: " + guild.name + " (ID: " + str(guild.id) + ")")  # Event log
		except Exception as exception:
			logger.critical("Failed to initialise guild: " + guild.name + " (ID: " + str(guild.id) + "). Exception: " + exception)  # Event log

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
			logger.error("Failed to calculate uptime. Exception: " + exception)  # Event log
			return None

	async def terminatePoll(self, message):
		"""Closes poll"""
		reactions = message.reactions
		highest_count = 0
		emojis = []
		counts = []

		for reaction in reactions:
			emoji = reaction.emoji
			if emoji not in emojis:
				emojis.append(emoji)
			if str(emoji) != "🔚": # Doesn't count end emote
				counts.append(str(reaction.count - 1))
			if reaction.count > highest_count:
				highest_count = reaction.count
				highest_emoji = reaction.emoji
		highest_count -= 1  # Takes away the bots reaction

		poll = self.poll[str(message.guild.id)][str(message.id)]

		options = []
		#for option in poll["options"]:  # Makes list of options
		for emoji in emojis:
			if str(emoji) != "🔚":
				options.append(str(emoji) + " " + poll["options"][str(emoji)])

		title = str(poll["title"])
		if title == "Embed.Empty":
			title = ""
		embed_results = discord.Embed(title=title + " Results")
		embed_results.add_field(name="Candidates", value="\n".join(options), inline=True)
		embed_results.add_field(name="Count", value="\n".join(counts), inline=True)
		if poll["config"]["winner"] == "highest": # Winner is shown as the highest scoring candidate


			embed_results.add_field(name="Winner", value=(str(highest_emoji) + " " + poll["options"][str(highest_emoji)] + " Score: " + str(highest_count)), inline=False)

		await message.channel.send(embed=embed_results)
		self.poll[str(message.guild.id)].pop(str(message.id)) # Removes poll entry from dictionary

	async def get_formatted_emoji(self,emoji_reference,guild):
		"""Returns an emoji that discord should always be able to use"""
		if emoji_reference.startswith("<"):
			parts = emoji_reference.split(":")
			return discord.utils.get(guild.emojis, name=parts[1]) # Uses the name part to get the emoji
		else:
			return emoji_reference

	async def announce(self,announcement,announcement_type="generic"):
		for guild in self.guilds:
			if self.data["servers"][str(guild.id)]["config"]["announcements channel id"] != 0: # Only finds announcement channel if the guild has one set
				announcement_sent = False
				for channel in guild.text_channels:
					if channel.id == self.data["servers"][str(guild.id)]["config"]["announcements channel id"]:
						logger.debug("Sending "+announcement_type+" announcement to " + guild.name + " in " + channel.name)  # Event log
						announcement_sent = True
						await channel.send(announcement)
						break
				if announcement_sent is False:
					logger.debug("Failed to send "+announcement_type+" announcement. Announcement channel not found in " + guild.name)  # Event log

	async def on_ready(self):
		"""Runs when the client is ready."""
		global guild_ids
		logger.debug("Connected!")

		if self.connected == False:
			logger.info("Last disconnect was "+str(self.last_disconnect))
			await self.announce("**Reconnected**\nLast disconnect was "+str(self.last_disconnect),announcement_type="reconnection")
		self.connected = True

		# Load the data file into the data variable
		try:
			with open("data.json", encoding='utf-8') as file:
				self.data = json.load(file)
			logger.debug("Loaded data.json")  # Event log
		except Exception as exception:
			logger.critical("Failed to load data.json. Exception: " + str(exception))  # Event log


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
		await self.announce("**" + self.user.name + " online**\nVersion: " + VERSION,announcement_type="on_ready")
		guild_ids = []
		for guild in self.guilds:
			guild_ids.append(guild.id)

	async def on_disconnect(self):
		if self.connected == True: # Stops code being ran every time discord realises its still disconnected since the last minute or so
			logger.info("Bot disconnected")
			self.last_disconnect = datetime.now()
			self.connected = False

	async def on_guild_join(self, guild):
		"""Runs on joining a guild.
		The bot initialises the guild if it has no data on it."""

		logger.info(self.user.name + " has joined the guild: " + guild.name + " with id: " + str(guild.id))  # Event log

		# Check if server data already exists
		if str(guild.id) not in self.data["servers"]:

			# Initialise guild
			self.initialise_guild(guild)

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
		if (message.author.id not in self.cache[str(guild.id)]) or ((datetime.now() - self.cache[str(guild.id)][message.author.id]).seconds // 3600 > 0):  # This is the longest like of code I've ever seen survive a scrutinised and picky merge from me. Well played.

			logger.debug("Adding experience to " + message.author.name)  # Event log

			# Update the cache and increment the user's experience
			self.cache[str(guild.id)][message.author.id] = datetime.now()
			try:
				self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] += 1
			except KeyError:
				self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] = 1

			# Write the updated data
			self.update_data()
		else:
			logger.debug("Not adding experience to " + message.author.name)  # Event log

		# Get level command
		if message.content == PREFIX + "level":

			logger.info("`level` called by " + message.author.name)  # Event log

			# Generate the rank card
			if str(message.author.id) in self.data["servers"][str(guild.id)]["ranks"]:
				rank = int((self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] ** 0.5) // 1)
				percentage = int(round((self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] - (rank ** 2)) / (((rank + 1) ** 2) - (rank ** 2)) * 100))
			else:
				rank = 0
				percentage = 0
			generate_level_card(message.author.avatar_url, message.author.name, rank, percentage)

			# Create the rank embed
			embed_level = discord.Embed()
			file = discord.File("card.png")
			embed_level.set_image(url="attachment://card.png")

			# Send the embed
			await message.channel.send(file=file)

		# Level leaderboard command
		if message.content == PREFIX + "leaderboard":
			logger.info("`leaderboard` called by " + message.author.name)  # Event log

			leaderboard = reversed(sorted(self.data["servers"][str(guild.id)]["ranks"].items(), key=lambda item: item[1])) # Sorts rank dictionary into list
			logger.debug(leaderboard)
			lb_message = ""
			lb_count = ""
			lb_no = ""

			count = 1
			for item in leaderboard:
				try:
					name = self.get_user(int(item[0])).name
					lb_message += str(name)+"\n" # Reverse adds on higher scored names
					lb_count += str(item[1])+"\n" # Reverse adds on higher scores to separate string for separate embed field
					lb_no += str(count)+"\n"
					count += 1
				except AttributeError:
					logger.debug("Member not found in server")

			embed_leaderboard = discord.Embed(title="Leaderboard",colour=0xffc000)
			embed_leaderboard.add_field(name="No.", value=lb_no, inline=True)
			embed_leaderboard.add_field(name="User",value=lb_message,inline=True)
			embed_leaderboard.add_field(name="Count", value=lb_count, inline=True)
			await message.channel.send(embed=embed_leaderboard)

		# Embed command
		if message.content.startswith(PREFIX + "embed"):
			"""Allow users to embed what they want"""

			try:
				argument_string = message.content[len(PREFIX + "embed "):]
				arguments = re.split(",(?!\s)", argument_string)  # Splits arguments when there is not a space after the comma, if there is, it is assumed to be part of a sentance.
				title = discord.Embed.Empty
				description = discord.Embed.Empty
				colour = 0xffc000
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
							colour = int(argument[1][-6:], 16)
						else:
							fields.append({argument[0]:argument[1]})
					else:
						description = argument[0]

				# Create and send user's embed
				embed = discord.Embed(title=title, description=description, colour=colour)
				embed.set_author(name=message.author.name,url=discord.Embed.Empty, icon_url=message.author.avatar_url)
				for field in fields:
					embed.add_field(name=list(field.keys())[0],value=field[list(field.keys())[0]])

				await message.channel.send(embed=embed)
				await message.delete()
			except Exception as exception:
				logger.error("Failed understand embed command. Exception: " + str(exception))
				await message.channel.send("Embed Failed: Check you put something to embed and that it's under 1024 character.\n"+str(exception))

		# Help command
		if message.content == PREFIX + "help":

			logger.info("`help` called by " + message.author.name)  # Event log

			# Create and send the help embed
			embed_help = discord.Embed(title="🤔 Need help?", description="Here's a list of " + self.user.name + "'s commands!", colour=0xffc000)
			embed_help.add_field(name=str(PREFIX + "level"), value="Creates your level card, showing your current level and progress to the next level.")
			embed_help.add_field(name=str(PREFIX + "embed"), value="Creates an embed. Arguments: title=,description=,colour=[hex code],[name of field]= or just write and it'll be put in the description by deafult")
			embed_help.add_field(name=str(PREFIX + "poll"), value="Creates a poll embed. Arguments: title=,colour=[hex code],[name of candidate]=[emoji]. All paramaters are optional. Admins react with 🔚 (end) to end poll)")
			embed_help.add_field(name=str(PREFIX + "help"), value="Creates the bot's help embed, listing the bot's commands.")
			embed_help.add_field(name=str(PREFIX + "rules"), value="Creates the server's rules embed.\nAdmin only feature.")
			embed_help.add_field(name=str(PREFIX + "roles"), value="Creates the server's roles embed.\nAdmin only feature.")
			embed_help.add_field(name=str(PREFIX + "stats"), value="Creates the server's stats embed.\nAdmin only feature.")
			embed_help.add_field(name=str(PREFIX + "locate"), value="Locates the instance of " + self.user.name + ".\nDev only feature.")
			embed_help.add_field(name=str(PREFIX + "kill"), value="Ends the instance of " + self.user.name + ".\nDev only feature.")
			await message.channel.send(embed=embed_help)

		# If the message was sent by the admins
		if message.author.guild_permissions.administrator:

			# Rules command
			if message.content == PREFIX + "rules":

				logger.info("`rules` called by " + message.author.name)  # Event log

				# If the rules have been set up
				if len(self.data["servers"][str(guild.id)]["rules"]["list"]) != 0:

					# Delete the command message
					await message.delete()

					# Create the welcome embed !!! This is messy. Decide embed format and what should be customisable
					embed_welcome = discord.Embed(title="👋 Welcome to " + message.guild.name + ".", description="[Discord community server description]\n\nTake a moment to familiarise yourself with the rules below.\nChannel <#000000000000000000> is for this, and <#000000000000000001> is for that.", colour=0xffc000)

					# Create the rules embed
					embed_rules = discord.Embed(title=self.data["servers"][str(guild.id)]["rules"]["title"], description=self.data["servers"][str(guild.id)]["rules"]["description"], colour=0xffc000, inline=False)
					embed_rules.set_footer(text="Rules updated • " + date.today().strftime("%d/%m/%Y"), icon_url=guild.icon_url)
					embed_rules.add_field(name="Rules", value="\n".join(self.data["servers"][str(guild.id)]["rules"]["list"]), inline=True)
					embed_image = discord.Embed(description="That's all.", colour=0xffc000)
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
			if message.content == PREFIX + "roles":
				# If the roles functionality is enabled
				if "roles" in self.data["servers"][str(message.guild.id)]:
					# try:

					# Creates and sends the roles messages
					await message.channel.send("🗒️ **Role selection**\nReact to get a role, unreact to remove it.")
					for category in self.data["servers"][str(message.guild.id)]["roles"]["categories"]:
						buttons = []
						for role in self.data["servers"][str(message.guild.id)]["roles"]["categories"][category]["list"]:
							buttons.append(create_button(style=ButtonStyle.blue, emoji=await self.get_formatted_emoji(self.data["servers"][str(message.guild.id)]["roles"]["categories"][category]["list"][role]["emoji"],guild),label=self.data["servers"][str(message.guild.id)]["roles"]["categories"][category]["list"][role][
								"name"], custom_id=role))
						components = []
						for x in range(math.ceil(len(buttons) / 5)):
							if len(buttons[(5 * x):]) > 5:
								components.append(create_actionrow(*buttons[(5 * x):(5 * x) + 5]))
							else:
								components.append(create_actionrow(*buttons[(5 * x):]))
						category_message = await message.channel.send(content="**" + category + "**\n" + "Select the roles for this category!", components=components)

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
			if message.content == PREFIX + "react roles":

				logger.info("`roles` called by " + message.author.name)  # Event log

				# If the roles have been set up
				if len(self.data["servers"][str(guild.id)]["roles"]["categories"]) != 0:

					# Delete the command message
					await message.delete()

					# Send one roles message per category
					await message.channel.send("🗒️ **Role selection**\nReact to get a role, unreact to remove it.")
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
			if message.content.startswith(PREFIX + "stats"):

				logger.info("`stats` called by " + message.author.name)  # Event log

				argument = message.content[len(PREFIX + "stats "):]
				csv = False
				if argument == "csv": # Changes to csv mode where the stats are saved to a csv file instead
					csv = True
					logger.debug("Using csv mode")

				try:
					# Generate statistics
					waiting_message = await message.channel.send("This may take some time...")

					members = {}
					channel_statistics = [''] * (len(guild.text_channels))

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
						if csv:
							channel_statistics[channel_count//10] += channel.name + "," + str(message_count) + "\n"
						else:
							channel_statistics[channel_count//10] += channel.mention + ": " + str(message_count) + "\n"

					member_statistics = [''] * (len(members))
					member_count = 0
					for member in members:
						member_count += 1
						if csv:
							member_statistics[member_count // 10] += member.name + "," + str(members[member]) + "\n"
						else:
							member_statistics[member_count//10] += member.mention + ": " + str(members[member]) + "\n"
					logger.debug("Successfully generated statistics")  # Event log

					if csv:
						with open("channel_statistics.csv","w",encoding="UTF-8") as csv:
							channel_string = ""
							for channel in channel_statistics:
								channel_string += channel
							csv.write(str(channel_string))
						await message.channel.send(file=discord.File("channel_statistics.csv",filename=guild.name+" channel_statistics.csv"))

						with open("member_statistics.csv","w",encoding="UTF-8") as csv:
							member_string = ""
							for member in member_statistics:
								member_string += member
							csv.write(str(member_string))
						await message.channel.send(file=discord.File("member_statistics.csv",filename=guild.name+" member_statistics.csv"))
					else:
						# Create and send statistics embed
						embed_channel = discord.Embed(title="📈 Channel Statistics for " + guild.name, colour=0xffc000)
						for x in range(len(channel_statistics)//10+1):
							#print("------\nChannels in set:\n"+str(channel_statistics[x]))
							logger.debug("------\nChannels in set:\n"+str(channel_statistics[x]))
							embed_channel.add_field(name="Channels", value=str(channel_statistics[x]))
							embed_channel.set_footer(text="Statistics updated • " + date.today().strftime("%d/%m/%Y"), icon_url=guild.icon_url)
						await message.channel.send(embed=embed_channel)

						embed_member = discord.Embed(title="📈 Member Statistics for " + guild.name, colour=0xffc000)
						for x in range(len(member_statistics)//10+1):
							logger.debug("Member:" + str(member_statistics[x]))
							embed_member.add_field(name="Members", value=str(member_statistics[x]))
							embed_member.set_footer(text="Statistics updated • " + date.today().strftime("%d/%m/%Y"), icon_url=guild.icon_url)
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
							embed_channel_stats.add_field(name="Channel stats prt "+str(x+1),value=channel_statistics[0][x*1024:(x+1)*1024])
							i = x
						embed_channel_stats.add_field(name="Channel stats prt " + str(i+1), value=channel_statistics[0][(i+1)*1024:])
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
			if message.content.startswith(PREFIX + "purge"):
				logger.info("`purge` called by " + message.author.name)  # Event log
				argument = message.content[len(PREFIX + "purge "):]
				number = int(argument)

				purge_message = await message.channel.send("React with 👍 to confirm")
				self.purge_messages[purge_message.id] = number

			# Poll command
			if message.content.startswith(PREFIX + "poll"):
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
				await message.channel.purge(limit=1)

				# !!! Clunky and breakable
				argument_string = message.content[len(PREFIX + "poll "):]
				if len(argument_string) <2:
					logger.debug("Poll command had no viable arguments - cancelled")
					return
				arguments = re.split("\,\s|\,", argument_string)  # Replace with arguments = argument.split(", ")
				candidates = {}  # Dictionary of candidates that can be voted for
				candidates_string = ""

				# Embed
				title = discord.Embed.Empty
				colour = 0xffc000

				# Config
				winner = "highest"

				# Analyse argument
				for argument in arguments:
					argument = argument.split("=")
					# print("Argument 0, 1:", argument[0], argument[1])
					poll_time = str(datetime.now())
					if argument[0] == "title":
						title = argument[1]
					elif argument[0] == "colour":
						colour = int(argument[1][-6:],16) # Takes last 6 digits and converts to hex for colour
					elif argument[0] == "winner":
						winner = argument[1]
					else:
						emoji = argument[1].rstrip()
						if not(emoji in candidates):
							candidates[emoji] = argument[0]
							candidates_string += argument[1] + " - " + argument[0] + "\n"
						else:
							logger.debug("Duplicate emoji in poll detected")
							await message.channel.send("Please only use an emoji once per poll")

				# Create and send poll embed
				embed_poll = discord.Embed(title=title, description=candidates_string, colour=colour)
				poll_message = await message.channel.send(embed=embed_poll)

				self.poll[str(message.guild.id)].update({str(poll_message.id): {
					"title": title,
					"options": candidates,
					"config":
						{
							"winner": winner
						}
				}
				})

				logger.debug(self.poll[str(message.guild.id)])

				# Add reactions to the poll embed
				for candidate in candidates:
					# print("Candidate: " + str(candidate))
					await poll_message.add_reaction(candidate)

			# Review confessions command
			if message.content == PREFIX + "review confessions":
				logger.info("`review confessions` called by " + message.author.name)  # Event log
				if "confessions" in self.data["servers"][str(guild.id)]:
					for confession in client.data["servers"][str(guild.id)]["confessions"]["messages"]:
						confession_embed = discord.Embed(title="Review Confession No." + confession, description="> " + client.data["servers"][str(guild.id)]["confessions"]["messages"][confession], colour=0xFF0A00)
						confession_embed.set_footer(text="This message is here to be reviewed. Please say if the content is inappropriate!", icon_url=guild.icon_url)
						button = (create_button(style=ButtonStyle.red, label="remove", custom_id="confession"+confession))
						components = [create_actionrow(*[button])]
						await message.channel.send(embed=confession_embed,components=components)

			# Print confessions command
			if message.content == PREFIX + "print confessions":
				logger.info("`print confessions` called by " + message.author.name)  # Event log
				if "confessions" in self.data["servers"][str(guild.id)]:
					for confession in client.data["servers"][str(guild.id)]["confessions"]["messages"]:
						confession_embed = discord.Embed(title="Confession No." + confession, description="> " + client.data["servers"][str(guild.id)]["confessions"]["messages"][confession], colour=0xF0CCA7)
						confession_embed.set_footer(text="/confess to submit your anonymous confession", icon_url=self.user.avatar_url)
						await message.channel.send(embed=confession_embed)

					self.data["servers"][str(guild.id)]["confessions"]["messages"] = {}
					self.update_data()
					await message.delete()

		# If the message was sent by the developers
		if message.author.id in self.data["config"]["developers"]:

			# Announcement command
			if message.content.startswith(PREFIX + "announcement"):
				logger.info("`announcement` called by " + message.author.name)  # Event log
				if len(message.content) > len(PREFIX + "announcement "):
					argument = message.content[len(PREFIX + "announcement "):]
					await self.announce(argument)
				else:
					logger.error("No announcement argument supplied")  # Event log

			# Report command
			if message.content.startswith(PREFIX + "report"):
				logger.info("`report` called by " + message.author.name)  # Event log
				if len(message.content) > len(PREFIX + "report "):
					argument = message.content[len(PREFIX + "report "):]
					logger.info(argument+" is requested to be reported to "+guild.name+" ID:"+str(guild.id)+" to "+message.channel.name+" channel ID:"+str(message.channel.id))
					try:
						if argument == "DISCORD_TOKEN":
							await message.channel.send("This variable is private and should never be shared. Manual access will be required instead.\n**The request of this variable has been logged!**")
						else:
							await message.channel.send(eval(argument))
					except:
						await message.channel.send("Something went wrong when trying to get the value of "+argument)
				else:
					logger.error("Nothing specified to report")  # Event log
				dev_mentions = ""
				#for dev in self.data["config"]["developers"]:
				#	dev_mentions += self.get_user(dev).mention
				await self.get_channel(832293063803142235).send(dev_mentions+"Report used in "+guild.name+" by "+message.author.mention)

			# Locate command
			if message.content == PREFIX + "locate":
				logger.info("`locate` called by " + message.author.name)  # Event log
				hostname = socket.gethostname()
				await message.channel.send("This instance is being run on **" + hostname + "**, IP address **" + socket.gethostbyname(hostname) + "** (**" + str(round(self.latency)) + "**ms)" + "\nUptime: " + self.get_uptime() + "."+ "\nLast disconnect: " + str(self.last_disconnect) + ".")

			# Kill command
			if message.content.startswith(PREFIX + "kill"):
				logger.info("`kill` called by " + message.author.name)  # Event log
				if self.data["config"]["jokes"] is True:
					await message.channel.send("Doggie down")

				reason = message.content[len(PREFIX + "kill"):]
				death_note = "**" + self.user.name + " offline**\nReason for shutdown: "+reason

				# Send kill announcement
				await self.announce(death_note,announcement_type="kill")

				await message.channel.send(death_note+"\n"+"Uptime: " + self.get_uptime() + ".")
				await client.close()

		# Joke functionality
		if self.data["config"]["jokes"] is True:

			# Shut up Arun
			if message.author.id == 258284765776576512:
				if randint(1, 128) == 127:
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

			if guild.id == TheHatShop:
				# Gameboy mention
				if "gameboy" in message.content.lower():
					logger.debug("`gameboy` mentioned by " + message.author.name)  # Event log
					await message.channel.send("Gameboys are worthless (apart from micro. micro is cool)")

				# Raspberry mention
				if "raspberries" in message.content.lower() or "raspberry" in message.content.lower():
					logger.debug("`raspberry racers` mentioned by " + message.author.name)  # Event log
					await message.channel.send("The Raspberry Racers are a team which debuted in the 2018 Winter Marble League. Their 2018 season was seen as the second-best rookie team of the year, behind only the Hazers. In the 2018 off-season, they won the A-Maze-ing Marble Race, making them one of the potential title contenders for the Marble League. They eventually did go on to win Marble League 2019.")

				# Pycharm mention
				if "pycharm" in message.content.lower():
					logger.debug("`pycharm` mentioned by " + message.author.name)  # Event log
					await message.channel.send("Pycharm enthusiasts vs Sublime Text enjoyers: https://youtu.be/HrkNwjruz5k")
					await message.channel.send("85 commits in and haha bot print funny is still our sense of humour.")

			# Token command
			if message.content == PREFIX + "token":
				logger.debug("`token` called by " + message.author.name)  # Event log
				await message.channel.send("IdrOppED ThE TokEN gUYS!!!!")

			# Summon lizzie command
			if message.content == PREFIX + "summon lizzie":
				logger.debug("`summon_lizzie` called by " + message.author.name)  # Event log
				for x in range(100):
					await message.channel.send(guild.get_member(692684372247314445).mention)

			# Summon leo command
			if message.content == PREFIX + "summon leo":
				logger.debug("`summon_leo` called by " + message.author.name)  # Event log
				for x in range(100):
					await message.channel.send(guild.get_member(242790351524462603).mention)

			# Teaching bitches how to swim
			if message.content == PREFIX + "swim":
				logger.debug("`swim` called by " + message.author.name)  # Event log
				await message.channel.send("/play https://youtu.be/uoZgZT4DGSY")
				await message.channel.send("No swimming lessons today ):")

			# Overlay Israel (Warning: DEFCON 1)
			if message.content == PREFIX + "israeli defcon 1":
				logger.debug("`israeli_defcon_1` called by " + message.author.name)  # Event log
				await message.channel.send("apologies in advance...")
				while True:
					await message.channel.send(".overlay israel")

	async def on_member_join(self, member):
		"""Runs when a member joins.
		Sends the member a message welcome message."""

		logger.debug("Member " + member.name + " joined guild " + member.guild.name)  # Event log
		try:
			await member.create_dm()
			await member.dm_channel.send("Welcome to " + member.guild.name + ", " + member.name + ".")
			logger.debug("Sent welcome message for " + member.guild.name + " to " + member.name)  # Event log
		except Exception as exception:
			# If user has impeded direct messages
			logger.debug("Failed to send welcome message for " + member.guild.name +" to " + member.name + ". Exception: " + exception)  # Event log

	async def on_member_remove(self, member):
		"""Runs when a member leaves.
		Sends the member a goodbye message."""

		logger.debug("Member " + member.name + " left guild " + member.guild.name)  # Event log
		try:
			await member.create_dm()
			await member.dm_channel.send("Goodbye ;)")
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
		if reaction_usage == "none": # No functionality found yet, keep checking
			# Poll reaction check
			try:
				for message in self.poll[str(guild.id)]:
					if str(payload.message_id) == message:
						reaction_usage = "polls"
						logger.debug("Poll message reacted to")
						break
			except KeyError:
				pass

			if reaction_usage == "none": # No functionality found yet, keep checking
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
				logger.info("Role `" + role.name + "` added to " + payload.member.name)  # Event log
			# If we want to do something in case of errors we'd do it here
			except Exception as exception:
				logger.error("Failed to add role " + role.name + " to " + payload.member.name + ". Exception: " + exception)  # Event log


		if reaction_usage == "polls":
			if str(payload.emoji) == "🔚":

				logger.debug("Poll ending")
				logger.debug("Poll identified for termination")
				channel = await self.fetch_channel(payload.channel_id)
				message = await channel.fetch_message(payload.message_id)
				reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
				await reaction.remove(payload.member)  # Removes end emoji
				await self.terminatePoll(message)
			else:
				valid_emoji = False
				for message in self.poll[str(payload.guild_id)]:
					#print(str(payload.emoji)+"?"+str(self.poll[str(payload.guild_id)][message]["options"]))
					if str(payload.emoji) in self.poll[str(payload.guild_id)][message]["options"]: # Deletes emojis not related to poll options
						valid_emoji = True
				if not valid_emoji:
					logger.debug("Unwanted emoji on poll found")
					channel = await self.fetch_channel(payload.channel_id)
					message = await channel.fetch_message(payload.message_id)
					await message.remove_reaction(payload.emoji,payload.member)
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
				logger.error("Failed to remove role " + role.name + " from " + payload.member.name + ". Exception: " + exception)  # Event log

		# If the roles haven't been set up
		else:
			logger.debug("Roles have not been set up for " + str(payload.guild.id))  # Event log
			# Send an error message
			await payload.channel.send("Uh oh, you haven't set up any roles! Get a server admin to set them up at https://www.lingscars.com/")

# Main body
if __name__ == "__main__":
	try:
		intents = discord.Intents.all()
		intents.members = True
		client = MyClient(intents=intents, debug=True, level="DEBUG")
		slash = SlashCommand(client, sync_commands=True)

		guild_ids = []
		for guild in client.guilds:
			guild_ids += guild.id

		@slash.slash(name="confess", description="Use the command to send an anonymous message to be posted later",
					 options=[create_option(
						 name="confession",
						 description="Your message",
						 option_type=3,
						 required=True)],
					 guild_ids=guild_ids)
		async def _confess(ctx, confession):
			"""Runs on the confession slash command."""

			logger.debug("`/confess` called anonymously")

			try:
				server_data = client.data["servers"][str(ctx.guild.id)]  # Used for easy reference

				if "confessions" not in server_data:
					server_data.update({"confessions": {"metadata": {"count": 0}, "messages": {}}})
				server_data["confessions"]["metadata"]["count"] += 1
				confession_data = {str(server_data["confessions"]["metadata"]["count"]): confession}
				server_data["confessions"]["messages"].update(confession_data)

				client.data["servers"][str(ctx.guild.id)] = server_data
				client.update_data()

				await ctx.defer(hidden=True)
				await ctx.send(
					content="Thank you for your confession. The content may be reviewed before posting but will remain anonymous.",
					hidden=True)

			except Exception as exception:
				logger.error("Failed to run /confess in " + ctx.guild.name + " (" + str(
					ctx.guild.id) + "). Exception: " + str(exception))


		@slash.slash(name="question", description="Ask Sirius a question",
					 options=[create_option(
						 name="question",
						 description="Your question",
						 option_type=3,
						 required=True)],
					 guild_ids=guild_ids)
		async def _question(ctx, question):
			"""Runs on the question slash command."""

			logger.debug("`/question` called by " + ctx.author.name)

			try:
				reply = "**" + ctx.author.name + "**: *" + question + "*\n\n"
				await ctx.send(content=reply + AI.question(question))

			except Exception as exception:
				logger.error("Failed to run /question message in " + ctx.guild.name + " (" + str(
					ctx.guild.id) + "). Exception: " + str(exception))


		@slash.slash(name="anonymous", description="Say something in the channel anonymously",
					 options=[create_option(
						 name="message",
						 description="Your message",
						 option_type=3,
						 required=True)],
					 guild_ids=guild_ids)
		async def _anonymous(ctx, message):
			"""Runs on the anonymous message slash command."""

			logger.debug("`/anonymous` called by " + ctx.author.name)

			try:
				await ctx.send(content="**Anonymous**: *"+message+"*")

			except Exception as exception:
				logger.error("Failed to run /anonymous message in " + ctx.guild.name + " (" + str(
					ctx.guild.id) + "). Exception: " + str(exception))


		# admin_roles = [role for role in ctx.guild.roles if role.permissions.administrator]
		@slash.slash(name="purge", description="Purge messages from the channel",
					 options=[create_option(
						 name="count",
						 description="How many messages",
						 option_type=4,
						 required=True)],
					 guild_ids=guild_ids)
		async def _purge(ctx, count):
			"""Runs on the purge slash command."""

			logger.debug("`/purge` called by " + ctx.author.name)

			if ctx.author.guild_permissions.administrator:
				purge_button = create_button(style=ButtonStyle.danger, label="Purge " + str(count) + " messages?",
											 custom_id="purge:" + str(count))
				components = [create_actionrow(*[purge_button])]
				await ctx.send(content="Purge " + str(count) + " messages?", components=components)
			else:
				await ctx.send("You do not have permissions to run this command", hidden=True)


		# Buttons...
		# The following must be tested:
		#     - Bots cannot press buttons
		#     - What happens when the bot isn't in the guild or the guild isn't cached (see
		#       on_raw_reaction_add for details)
		@client.event
		async def on_component(ctx):
			"""Runs on button press."""

			logger.debug("Button pressed by " + ctx.author.name)

			guild = ctx.origin_message.guild
			if ctx.custom_id.startswith("confession"):
				id = ctx.custom_id[len("confession"):]
				# Placeholder for other buttons functionality. Do not remove without consulting Pablo's forboding psionic foresight
				if "confessions" in client.data["servers"][str(guild.id)]:
					if ctx.author.guild_permissions.administrator:
						logger.debug("Checking confessions about button press")
						if id in client.data["servers"][str(guild.id)]["confessions"]["messages"]:
							del client.data["servers"][str(guild.id)]["confessions"]["messages"][
								id]  # Removes the confession
							logger.info(
								"Confession No." + id + " removed from guild " + guild.name + " by " + ctx.author.name)
							client.update_data()
							await ctx.edit_origin(
								content="**This message has been removed by " + ctx.author.name + "**")
					else:
						await ctx.edit_origin(
							content="**" + ctx.author.name + " **tried to remove this message without permissions!")

			if ctx.custom_id.startswith("purge"):
				if ctx.author.guild_permissions.administrator:
					count = int(ctx.custom_id[len("purge:"):])
					await ctx.channel.purge(limit=count)
					logger.info("Purge complete in " + ctx.channel.name + " < " + ctx.guild.name)
					await ctx.channel.send("Channel purged " + str(count) + " messages")
				else:
					await ctx.send("You do not have permissions to press this button", hidden=True)
					logger.info(ctx.author.name + " tried to purge messages")

			# If the roles functionality is enabled. THIS IS FUCKING BROKEN PABLO. WHY ARE YOU RETURNING WHEN IT COULD NOT BE ROLES!!!
			if "roles" in client.data["servers"][str(guild.id)]:
				try:

					# Checks if the message is one of the server's roles messages
					message_relevant = False
					for category in client.data["servers"][str(guild.id)]["roles"]["categories"]:
						if ctx.origin_message_id == \
								client.data["servers"][str(guild.id)]["roles"]["categories"][category]["message id"]:
							message_relevant = True
							break

					# Checks if the role ID is one of the server's roles
					role_id_found = False
					for category in client.data["servers"][str(guild.id)]["roles"]["categories"]:
						if ctx.custom_id in client.data["servers"][str(guild.id)]["roles"]["categories"][category][
							"list"]:
							role_id_found = True
							break
					if role_id_found is False:
						return
					# Checks if the role exists and is valid
					role = guild.get_role(int(ctx.custom_id))
					if role is None:
						logger.debug("Could not get role with id: " + ctx.custom_id)
						return

					# Adds the role if the user doesn't have it
					if role not in ctx.author.roles:
						await ctx.author.add_roles(role)
						await ctx.edit_origin(content="")
						logger.debug("Added role " + role.name + " to " + ctx.author.name)

					# Removes the role if the user already has it
					else:
						await ctx.author.remove_roles(role)
						await ctx.edit_origin(content="")
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
					logger.debug(r.status_code, r.reason)
					return

				except Exception as exception:
					logger.error("Failed to add role " + role.name + " to " + ctx.author.name + ". Exception: " + str(
						exception))  # Error: this may run even if the intention of the button press isn't to add a role
				finally:
					try:
						verify_role = client.data["servers"][str(guild.id)]["roles"]["verify role"]
						if verify_role != 0:
							role = guild.get_role(verify_role)
							await ctx.author.add_roles(role)
							logger.debug("Verified " + ctx.author.name + " on " + guild.name)
					except KeyError:
						logger.debug("No verification role found in " + guild.name)
					except Exception as exception:
						logger.error("Verification failed: " + exception)
					return

		client.run(DISCORD_TOKEN)
	except Exception as exception:
		logger.error("Exception: " + str(exception) + "\n")  # Event log