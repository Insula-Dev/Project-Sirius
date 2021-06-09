# Imports
from random import randint
from datetime import date, datetime
import json
import socket
import discord
import re  # Remove this later lol


# Home imports
from log_handling import *
from imaging import generate_rank_card
from upgrade_json import server_structure
import on_message


# Variables
PREFIX = "-"
with open("token.txt") as file:
	DISCORD_TOKEN = file.read()


# Definitions
class MyClient(discord.Client):

	def __init__(self, debug=False, *args, **kwargs):

		super().__init__(*args, **kwargs)
		self.start_time = datetime.now()
		self.data = {}
		self.cache = {}
		self.activity = discord.Activity(type=discord.ActivityType.listening, name="the rain")

		# Print logs to the console too (for debugging)
		if debug is True:
			logger.addHandler(logging.StreamHandler())

	def update_data(self):
		"""Writes the data attribute to the file."""

		try:
			with open("data.json", "w", encoding='utf-8') as file:
				json.dump(self.data, file, indent=4)
			logger.debug("Updated data.json")  # Event log
		except:
			logger.critical("Failed to update data.json")  # Event log

	def initialise_guild(self, guild):
		"""Creates data for a new guild."""

		try:
			self.data["servers"][str(guild.id)] = server_structure

			# Write the updated data
			self.update_data()
			logger.info("Initialised guild: " + guild.name + " (ID: " + str(guild.id) + ")")  # Event log
		except:
			logger.critical("Failed to initialise guild: " + guild.name + " (ID: " + str(guild.id) + ")")  # Event log

	def get_uptime(self):
		"""Returns client uptime as a string."""

		try:
			seconds = (datetime.now() - self.start_time).seconds
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
		except:
			logger.error("Failed to calculate uptime")  # Event log
			return None

	async def on_ready(self):
		"""Runs when the client is ready."""

		logger.info(self.user.name + " is ready (commencing on_ready)")  # Event log
		if self.guilds != []:
			logger.info(self.user.name + " is connected to the following guilds:")  # Event log
			for guild in self.guilds:
				logger.info("    " + guild.name + " (ID: " + str(guild.id) + ")")  # Event log

		# Load the data file into the data variable
		try:
			with open("data.json", encoding='utf-8') as file:
				self.data = json.load(file)
			logger.debug("Loaded data.json")  # Event log
		except:
			logger.critical("Could not load data.json")  # Event log

		# Check if Sirius has been added to a guild while offline
		for guild in self.guilds:
			if str(guild.id) not in self.data["servers"]:
				logger.warning("Sirius is in " + guild.name + " but has no data for it")  # Event log

				# Initialise guild
				self.initialise_guild(guild)

		# Initialise cache for servers
		for guild in self.guilds:
			self.cache[str(guild.id)] = {}

		logger.info(self.user.name + " is ready (finished on_ready)")  # Event log

	async def on_guild_join(self, guild):
		"""Runs on joining a guild."""

		logger.info(self.user.name + " has joined the guild: " + guild.name + " with id: " + str(guild.id))  # Event log

		# Check if server data already exists
		if str(guild.id) not in self.data["servers"]:

			# Initialise guild
			self.initialise_guild(guild)

	async def on_message(self, message):
		await on_message.on_message(PREFIX,self,message)

	async def on_member_join(self, member):
		"""Runs when a member joins."""

		logger.debug("Member " + member.name + " joined guild [GUILD_NAME]")
		try:
			await member.create_dm()
			await member.dm_channel.send("Welcome to the server, " + member.name + ".")
			logger.debug("Sent welcome message to " + member.name)  # Event log
		except:
			# If user has impeded direct messages
			logger.debug("Failed to send welcome message to " + member.name)  # Event log

	async def on_member_remove(self, member):
		"""Runs when a member leaves."""

		logger.debug("Member " + member.name + " left guild [GUILD_NAME]")
		try:
			await member.create_dm()
			await member.dm_channel.send("Goodbye ;)")
			logger.debug("Sent goodbye message to " + member.name)  # Event log
		except:
			# If the user has impeded direct messages
			logger.debug("Failed to send goodbye message to " + member.name)  # Event log

	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		"""Gives a role based on a reaction emoji."""

		guild = self.get_guild(payload.guild_id)

		# Make sure that the message the user is reacting to is the one we care about.
		message_relevant = False
		for category in self.data["servers"][str(guild.id)]["roles"]["category list"]:
			if payload.message_id == self.data["servers"][str(payload.guild_id)]["roles"]["category list"][category]["message id"]:
				message_relevant = True
				break
		if message_relevant is False:
			return

		# Make sure the user isn't the bot.
		if payload.member.id == self.user.id:  # was payload.author
			return

		# Check if we're still in the guild and it's cached.
		if guild is None:
			return

		# If the emoji isn't the one we care about then delete it and exit as well.
		role_id = -1
		for category in self.data["servers"][str(guild.id)]["roles"]["category list"]:  # For category in list
			for role in self.data["servers"][str(guild.id)]["roles"]["category list"][category]["role list"]:  # For role in category
				if self.data["servers"][str(guild.id)]["roles"]["category list"][category]["role list"][role]["emoji"] == str(payload.emoji):
					role_id = int(role)
					break
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

		# If we want to do something in case of errors we'd do it here.
		except discord.HTTPException:
			logger.error("Exception: discord.HTTPException. Could not add role " + role.name + " to " + payload.member.name)  # Event log

	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		"""Removes a role based on a reaction emoji."""

		guild = self.get_guild(payload.guild_id)

		# Make sure that the message the user is reacting to is the one we care about.
		message_relevant = False
		for category in self.data["servers"][str(guild.id)]["roles"]["category list"]:
			if payload.message_id == self.data["servers"][str(payload.guild_id)]["roles"]["category list"][category]["message id"]:
				message_relevant = True
				break
		if message_relevant is False:
			return

		# The payload for `on_raw_reaction_remove` does not provide `.member`
		# so we must get the member ourselves from the payload's `.user_id`.

		# Make sure the member still exists and is valid.
		member = guild.get_member(payload.user_id)
		if member is None:
			return

		# Make sure the user isn't the bot.
		if member.id == self.user.id:
			return

		# Check if we're still in the guild and it's cached.
		if guild is None:
			return

		# If the emoji isn't the one we care about then exit as well.
		role_id = -1
		for category in self.data["servers"][str(guild.id)]["roles"]["category list"]:  # For category in list
			for role in self.data["servers"][str(guild.id)]["roles"]["category list"][category]["role list"]:  # For role in category
				if self.data["servers"][str(guild.id)]["roles"]["category list"][category]["role list"][role]["emoji"] == str(payload.emoji):
					role_id = int(role)
					break
		if role_id == -1:
			return

		# Make sure the role still exists and is valid.
		role = guild.get_role(role_id)
		if role is None:
			return

		# Finally, remove the role.
		try:
			await member.remove_roles(role)
			logger.info("Role `" + role.name + "` removed from " + member.name)  # Event log

		# If we want to do something in case of errors we'd do it here.
		except discord.HTTPException:
			logger.error("Exception: discord.HTTPException. Could not remove role " + role.name + " from ", member.name)  # Event log


# Main body
try:
	intents = discord.Intents.default()
	intents.members = True

	client = MyClient(intents=intents, debug=True)
	client.run(DISCORD_TOKEN)

	logger.info("That's all\n")  # Event log
except:

	# This is intended to catch all unexpected shutdowns and put a newline in the log file, since otherwise it becomes concatenated and horrible... Does on_kill exist?
	logger.error("Unexpected exception... Say that ten times fast\n")  # Event log
