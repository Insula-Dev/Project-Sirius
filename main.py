# Imports
from random import randint
from datetime import date, datetime
import json
import socket
import discord
import re  # Delete this later


# Local imports
from log_handling import *
from imaging import generate_rank_card


# Variables
PREFIX = "-"
with open("token.txt") as file:
	DISCORD_TOKEN = file.read()
server_structure = {
	"config": {
		"rank system": False,
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
		"categories": {
			"Server": {
				"message id": 0,
				"roles": {}
			}
		}
	},
	"ranks": {}
}


# Definitions
class MyClient(discord.Client):

	def __init__(self, debug=False, level="DEBUG", *args, **kwargs):
		"""Constructor."""

		super().__init__(*args, **kwargs)
		self.connected = False
		self.start_time = datetime.now()
		self.data = {}
		self.cache = {}
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

	async def on_ready(self):
		"""Runs when the client is ready."""

		self.connected = True

		# Load the data file into the data variable
		try:
			with open("data.json", encoding='utf-8') as file:
				self.data = json.load(file)
			logger.debug("Loaded data.json")  # Event log
		except Exception as exception:
			logger.critical("Failed to load data.json. Exception: " + exception)  # Event log


		# Check if the bot has been added to a guild while offline
		for guild in self.guilds:
			if str(guild.id) not in self.data["servers"]:
				logger.warning("The bot is in " + guild.name + " but has no data for it")  # Event log

				# Initialise guild
				self.initialise_guild(guild)

		# Initialise cache for servers
		for guild in self.guilds:
			self.cache[str(guild.id)] = {}

		logger.info(self.user.name + " is ready (finished on_ready)")  # Event log

		# Log on_ready messages
		logger.info(self.user.name + " is ready (commencing on_ready)")  # Event log
		if self.guilds != []:
			logger.info(self.user.name + " is connected to the following guilds:")  # Event log
			for guild in self.guilds:
				logger.info("    " + guild.name + " (ID: " + str(guild.id) + ")")  # Event log

				# Send on_ready announcement
				announcement_sent = False
				for channel in guild.text_channels:
					if channel.id == self.data["servers"][str(guild.id)]["config"]["announcements channel id"]:
						logger.debug("Sending on_ready announcement to " + guild.name + " in " + channel.name)  # Event log
						announcement_sent = True
						await channel.send("**" + self.user.name + " online**\nVersion: " + self.data["config"]["version"])
						break
				if announcement_sent is False:
					logger.debug("Failed to send on_ready announcement. Announcement channel not found in " + guild.name)  # Event log

	async def on_disconnect(self):
		if self.connected == True: # Stops code being ran every time discord realises its still disconnected since the last minute or so
			logger.info("Bot disconnected")
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

		# Get rank command
		if message.content == PREFIX + "get rank":

			logger.info("`get rank` called by " + message.author.name)  # Event log

			# Generate the rank card
			if str(message.author.id) in self.data["servers"][str(guild.id)]["ranks"]:
				rank = int((self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] ** 0.5) // 1)
				percentage = int(round((self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] - (rank ** 2)) / (((rank + 1) ** 2) - (rank ** 2)) * 100))
			else:
				rank = 0
				percentage = 0
			generate_rank_card(message.author.avatar_url, message.author.name, rank, percentage)

			# Create the rank embed
			embed_rank = discord.Embed()
			file = discord.File("card.png")
			embed_rank.set_image(url="attachment://card.png")

			# Send the embed
			await message.channel.send(file=file)

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
				embed = discord.Embed(title=title, description=description, color=colour)
				embed.set_author(name=message.author.name,url=discord.Embed.Empty, icon_url=message.author.avatar_url)
				for field in fields:
					embed.add_field(name=list(field.keys())[0],value=field[list(field.keys())[0]])

				await message.channel.send(embed=embed)
			except Exception as exception:
				logger.error("Failed understand embed command. Exception: " + str(exception))
				await message.channel.send("Embed Failed: Check you put something to embed and that it's under 1024 character.\n"+str(exception))

		# Help command
		if message.content == PREFIX + "help":

			logger.info("`help` called by " + message.author.name)  # Event log

			# Create and send the help embed
			embed_help = discord.Embed(title="🤔 Need help?", description="Here's a list of " + self.user.name + "'s commands!", color=0xffc000)
			embed_help.add_field(name=str(PREFIX + "get rank"), value="Creates your rank card, showing your current rank and progress to the next rank.")
			embed_help.add_field(name=str(PREFIX + "embed"), value="Creates an embed. Arguments: title=,description=,[name of field]= or just write and it'll be put in the description by deafult")
			embed_help.add_field(name=str(PREFIX + "help"), value="Creates the bot's help embed, listing the bot's commands.")
			embed_help.add_field(name=str(PREFIX + "rules"), value="Creates the server's rules embed.\nAdmin only feature.")
			embed_help.add_field(name=str(PREFIX + "roles"), value="Creates the server's roles embed.\nAdmin only feature.")
			embed_help.add_field(name=str(PREFIX + "stats"), value="Creates the server's stats embed.\nAdmin only feature.")
			embed_help.add_field(name=str(PREFIX + "locate"), value="Locates the instance of " + self.user.name + ".\nDev only feature.")
			embed_help.add_field(name=str(PREFIX + "kill"), value="Ends the instance of " + self.user.name + ".\nDev only feature.")
			await message.channel.send(embed=embed_help)

		# If the message was sent by the admins
		if guild.get_role(self.data["servers"][str(message.guild.id)]["config"]["admin role id"]) in guild.get_member(message.author.id).roles:

			# Rules command
			if message.content == PREFIX + "rules":

				logger.info("`rules` called by " + message.author.name)  # Event log

				# If the rules have been set up
				if len(self.data["servers"][str(guild.id)]["rules"]["list"]) != 0:

					# Delete the command message
					await message.delete()

					# Create the welcome embed !!! This is messy. Decide embed format and what should be customisable
					embed_welcome = discord.Embed(title="👋 Welcome to " + message.guild.name + ".", description="[Discord community server description]\n\nTake a moment to familiarise yourself with the rules below.\nChannel <#000000000000000000> is for this, and <#000000000000000001> is for that.", color=0xffc000)

					# Create the rules embed
					embed_rules = discord.Embed(title=self.data["servers"][str(guild.id)]["rules"]["title"], description=self.data["servers"][str(guild.id)]["rules"]["description"], color=0xffc000, inline=False)
					embed_rules.set_footer(text="Rules updated • " + date.today().strftime("%d/%m/%Y"), icon_url=guild.icon_url)
					embed_rules.add_field(name="Rules", value="\n".join(self.data["servers"][str(guild.id)]["rules"]["list"]), inline=True)
					embed_image = discord.Embed(description="That's all.", color=0xffc000)
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

			# Roles command
			if message.content == PREFIX + "roles":

				logger.info("`roles` called by " + message.author.name)  # Event log

				# If the roles have been set up
				if len(self.data["servers"][str(guild.id)]["roles"]["categories"]) != 0:

					# Delete the command message
					await message.delete()

					# Send one roles message per category
					await message.channel.send("🗒️ **Role selection**\nReact to get a role, unreact to remove it.")
					for category in self.data["servers"][str(guild.id)]["roles"]["categories"]:  # For category in roles
						roles = []
						for role in self.data["servers"][str(guild.id)]["roles"]["categories"][category]["roles"]:  # For role in category
							roles.append(self.data["servers"][str(guild.id)]["roles"]["categories"][category]["roles"][role]["emoji"] + " - " + self.data["servers"][str(guild.id)]["roles"]["categories"][category]["roles"][role]["name"] + "\n")
						category_message = await message.channel.send("**" + category + "**\n\n" + "".join(roles))

						# Add reactions to the roles message
						for role in self.data["servers"][str(guild.id)]["roles"]["categories"][category]["roles"]:
							await category_message.add_reaction(self.data["servers"][str(guild.id)]["roles"]["categories"][category]["roles"][role]["emoji"])

						# Update the category's message id variable
						self.data["servers"][str(guild.id)]["roles"]["categories"][category]["message id"] = category_message.id

					# Write the updated data
					self.update_data()

				# If the roles haven't been set up
				else:
					logger.debug("Roles have not been set up for " + str(message.guild.id))  # Event log
					await message.channel.send("Uh oh, you haven't set up any roles! Get a server admin to set them up at https://www.lingscars.com/")

			# Stats command
			if message.content == PREFIX + "stats":
				"""THINGS TO FIX:
				- Trailing newlines at the end of embed"""

				logger.info("`stats` called by " + message.author.name)  # Event log

				# Generate statistics
				try:
					waiting_message = await message.channel.send("This may take some time...")
					members = {}
					channel_statistics = ""
					member_statistics = ""
					for channel in guild.text_channels:
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
					logger.debug("Successfully generated statistics")  # Event log

					# Create and send statistics embed
					embed_stats = discord.Embed(title="📈 Statistics for " + guild.name, color=0xffc000)
					embed_stats.add_field(name="Channels", value=channel_statistics)
					embed_stats.add_field(name="Members", value=member_statistics)
					embed_stats.set_footer(text="Statistics updated • " + date.today().strftime("%d/%m/%Y"), icon_url=guild.icon_url)
					await message.channel.send(embed=embed_stats)
					await waiting_message.delete()
				except Exception as exception:
					logger.error("Failed to generate or send statistics. Exception: " + str(exception))  # Event log
					await message.channel.send("Error: Something went wrong on our side...")

			# Purge Command
			if message.content.startswith(PREFIX + "purge"):
				logger.info("`purge` called by " + message.author.name)  # Event log
				argument = message.content[len(PREFIX + "purge "):]
				number = int(argument)

				purge_message = await message.channel.send("React with 👍 to confirm")
				self.purge_messages[purge_message.id] = number

		# If the message was sent by the developers
		if message.author.id in self.data["config"]["developers"]:

			# Announcement command
			if message.content.startswith(PREFIX + "announcement"):
				logger.info("`announcement` called by " + message.author.name)  # Event log
				if len(message.content) > len(PREFIX + "announcement "):
					argument = message.content[len(PREFIX + "announcement "):]
					for guild in self.guilds:
						announcement_sent = False
						for channel in guild.text_channels:
							if channel.id == self.data["servers"][str(guild.id)]["config"]["announcements channel id"]:
								logger.debug("Sent announcement to " + guild.name + " in " + channel.name)  # Event log
								announcement_sent = True
								await channel.send("**Announcement** (testing)\n" + argument)
								break
						if announcement_sent is False:
							logger.debug("Announcement channel not found in " + guild.name)  # Event log
				else:
					logger.error("No announcement argument supplied")  # Event log

			# Locate command
			if message.content == PREFIX + "locate":
				logger.info("`locate` called by " + message.author.name)  # Event log
				hostname = socket.gethostname()
				await message.channel.send("This instance is being run on **" + hostname + "**, IP address **" + socket.gethostbyname(hostname) + "** (**" + str(round(self.latency)) + "**ms)" + "\nUptime: " + self.get_uptime() + ".")

			# Kill command
			if message.content.startswith(PREFIX + "kill"):
				logger.info("`kill` called by " + message.author.name)  # Event log
				if self.data["config"]["jokes"] is True:
					await message.channel.send("Doggie down")

				reason = message.content[len(PREFIX + "kill"):]
				death_note = "**" + self.user.name + " offline**\nReason for shutdown: "+reason

				# Send kill announcement
				for guild in self.guilds:
					announcement_sent = False
					for channel in guild.text_channels:
						if channel.id == self.data["servers"][str(guild.id)]["config"]["announcements channel id"]:
							logger.debug("Sending kill announcement to " + guild.name + " in " + channel.name)  # Event log
							announcement_sent = True
							await channel.send(death_note)
							break
					if announcement_sent is False:
						logger.debug("Failed to send kill announcement. Announcement channel not found in " + guild.name)  # Event log

				await message.channel.send(death_note+"\n"+"Uptime: " + self.get_uptime() + ".")
				await client.close()

		# Joke functionality
		if self.data["config"]["jokes"] is True:

			# Shut up Arun
			if message.author.id == 258284765776576512:
				if randint(1, 19) == 1:
					logger.debug("Shut up Arun triggered by " + message.author.name)  # Event log
					if randint(1, 2) == 1:
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
		"""Runs when a reaction is added.
		If the message and reaction are relevant, adds a role based on the reaction emoji."""

		guild = self.get_guild(payload.guild_id)

		# Check if the roles have been set up
		if len(self.data["servers"][str(guild.id)]["roles"]["categories"]) != 0:

			# Make sure that the message the user is reacting to is the one we care about
			message_relevant = False
			for category in self.data["servers"][str(guild.id)]["roles"]["categories"]:
				if payload.message_id == self.data["servers"][str(payload.guild_id)]["roles"]["categories"][category]["message id"]:
					message_relevant = True
					break

			if payload.message_id in self.purge_messages: # Did a slightly different system that's doubly efficient than your weird check system
				logger.debug("Purge message reacted to")
				if guild.get_role(self.data["servers"][str(payload.guild_id)]["config"]["admin role id"]) in guild.get_member(payload.user_id).roles:
					logger.debug("Purge confirmed by admin")
					if str(payload.emoji) =="👍":
						try:
							await client.get_channel(payload.channel_id).purge(limit=self.purge_messages[payload.message_id])
							logger.info("Purge complete in "+client.get_channel(payload.channel_id).name + " < " +client.get_guild(payload.guild_id).name)
							await client.get_channel(payload.channel_id).send("Channel purged "+str(self.purge_messages[payload.message_id]) + " messages")
							self.purge_messages.pop(payload.message_id)
						except Exception as e:
							await client.get_channel(payload.channel_id).send("Channel failed the purge. There were possibly too many messages.")


			if message_relevant is False:
				return

			# Make sure the user isn't the bot
			if payload.member.id == self.user.id:
				return

			# Check if we're still in the guild and it's cached
			if guild is None:
				return

			# If the emoji isn't the one we care about then delete it and exit as well
			role_id = -1
			for category in self.data["servers"][str(guild.id)]["roles"]["categories"]:  # For category in list
				for role in self.data["servers"][str(guild.id)]["roles"]["categories"][category]["roles"]:  # For role in category
					if self.data["servers"][str(guild.id)]["roles"]["categories"][category]["roles"][role]["emoji"] == str(payload.emoji):
						role_id = int(role)
						break
			if role_id == -1:
				channel = await self.fetch_channel(payload.channel_id)
				message = await channel.fetch_message(payload.message_id)
				if payload.emoji.is_custom_emoji() is False:  # If the emoji is a custom emoji
					reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
				else:  # If the emoji is not a custom emoji
					reaction = discord.utils.get(message.reactions, emoji=payload.emoji)
				await reaction.remove(payload.member)
				logger.debug("Removed irrelevant emoji.")  # Event log
				return

			# Make sure the role still exists and is valid
			role = guild.get_role(role_id)
			if role is None:
				return

			# Finally, add the role
			try:
				await payload.member.add_roles(role)
				logger.info("Role `" + role.name + "` added to " + payload.member.name)  # Event log
			# If we want to do something in case of errors we'd do it here
			except Exception as exception:
				logger.error("Failed to add role " + role.name + " to " + payload.member.name + ". Exception: " + exception)  # Event log

		# If the roles haven't been set up
		else:
			logger.debug("Roles have not been set up for " + str(message.guild.id))  # Event log
			# Send an error message
			await message.channel.send("Uh oh, you haven't set up any roles! Get a server admin to set them up at https://www.lingscars.com/")

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
				for role in self.data["servers"][str(guild.id)]["roles"]["categories"][category]["roles"]:  # For role in category
					if self.data["servers"][str(guild.id)]["roles"]["categories"][category]["roles"][role]["emoji"] == str(payload.emoji):
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
			logger.debug("Roles have not been set up for " + str(message.guild.id))  # Event log
			# Send an error message
			await message.channel.send("Uh oh, you haven't set up any roles! Get a server admin to set them up at https://www.lingscars.com/")


# Main body
if __name__ == "__main__":
	try:
		intents = discord.Intents.default()
		intents.members = True
		client = MyClient(intents=intents, debug=True, level="DEBUG")
		client.run(DISCORD_TOKEN)
	except Exception as exception:
		logger.error("Exception: " + exception + "\n")  # Event log
