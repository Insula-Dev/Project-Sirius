# Imports
import math
import time
from datetime import date
from random import randint
import json
import socket
import discord
import re  # Needed for proper regex
import imaging
import requests


# Home imports
from log_handling import *


# Variables
with open("token.txt") as file:
	DISCORD_TOKEN = file.read()


# Definitions
def updateRankImage(user,xp): # Might be able to skip this and go straight to imaging lib
	#current_rank = xp/10
	#percent_to_next = xp%10
	try:
		current_rank = math.sqrt(xp-10/1.8)
	except ValueError: # If value is too low (can't square root negative) it defaults to zero
		current_rank = 0
	percent_to_rank = (xp%(1.8*((current_rank)**2)+10))
	logger.debug("Current rank: " + str(current_rank) + " xp: " + str(xp) + " next rank xp: " + str((1.8 * ((current_rank) ** 2) + 10)))
	imaging.makeRankCard(user.avatar_url,(current_rank),percent_to_rank,name=user.name)

class MyClient(discord.Client):

	def __init__(self, debug=False, *args, **kwargs):

		super().__init__(*args, **kwargs)
		self.data = {}
		if debug is True:
			# Print logs to the console too (for debugging)
			logger.addHandler(logging.StreamHandler())

	async def update_data(self):
		"""Writes the data variable into the file."""

		try:
			with open("data.json", "w", encoding='utf-8') as data_file:
				json.dump(self.data, data_file, indent=4)
			logger.info("Updated data.json")  # Event log
		except:
			logger.critical("Could not update data.json")  # Event log

	def initialise_guild(self, guild):
		"""Creates data for a new guild."""

		try:
			self.data["servers"][str(guild.id)] = {
				"rules": {
					"title": "Server rules",
					"description": "",
					"rules list": [],
					"image link": None
				},
				"roles message id": None,
				"roles": {},
				"ranks": {}
			}

			# Write the updated data
			self.update_data()
			logger.info("Initialised guild: " + guild.name + " (ID: " + str(guild.id) + ")")  # Event log
		except:
			logger.critical("Failed to initialise guild: " + guild.name + " (ID: " + str(guild.id) + ")")  # Event log

	def resetCache(self):
		self.cache = {}
		for server in self.guilds:
			self.cache.update({server.name:{}})

	def getGuildRanks(self,guild):
		# XP
		try:
			ranks = self.data["servers"][str(guild.id)]["ranks"]
		except KeyError:
			self.data["servers"][str(guild.id)].update(
				{"ranks": {}})  # Adds ranks section to data to upgrade the server's data
			ranks = self.data["servers"][str(guild.id)]["ranks"]
		return ranks

	async def addXP(self,author,guild):
		logger.debug("Adding xp to "+author.name)
		ranks = self.getGuildRanks(guild)
		try:  # Adds xp to user
			authorID = str(author.id)
			ranks[authorID] = ranks[authorID] + 1
		except KeyError:
			logger.info("New member " + author.name + " sent first registered message in " + guild.name)
			ranks.update({authorID: 0})  # Adds person to ranks list
		self.data["servers"][str(guild.id)]["ranks"] = ranks
		await self.update_data()

	async def on_ready(self):
		logger.info(self.user.name + " is starting (commencing on_ready)")  # Event log
		if self.guilds != []:
			logger.info(self.user.name + " is connected to the following guilds:")  # Event log
			for guild in self.guilds:
				logger.info("    " + guild.name + " (ID: " + str(guild.id) + ")")  # Event log

		# Load the file data into the data variable.
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

		# Creates cache
		self.resetCache()

		logger.info(self.user.name + " is ready (finished on_ready). Finished in "+str(time.time() - startTime)+" seconds")  # Event log

	async def on_guild_join(self, guild):
		""""Runs on joining a guild."""

		logger.info(self.user.name + " has joined the guild: " + guild.name + " with id: " + str(guild.id))  # Event log

		# Check if server data already exists
		if str(guild.id) not in self.data["servers"]:

			# Initialise guild
			self.initialise_guild(guild)

			#await guild.channels[0].send("Please set up your server at https://")  # !!! New server setup message + channel[0]?

	async def on_message(self, message):
		"""Runs on message."""

		logger.debug("Message sent by " + message.author.name)  # Event log

		# Set author of origin
		author = message.author

		# Don't respond to yourself
		if author.id == self.user.id:
			return

		# Set guild of origin
		guild = message.guild

		# Refresh cache
		if author.name in self.cache[guild.name]:
			if time.time() - self.cache[guild.name][author.name] > 60: # After 60 seconds, guild-user cache reset
				self.cache[guild.name][author.name] = time.time()
				await self.addXP(author,guild) # Adds xp to author
			else: # Already sent message during time
				pass
				logger.debug("Time left on cooldown: "+str(round((time.time() - self.cache[guild.name][author.name])*10)/10)+" seconds")
		else:
			self.cache[guild.name].update({author.name:time.time()}) # Creates new cache for author on guild
			await self.addXP(author, guild) # Adds xp to author


		if self.data["config"]["secure"] is True:

			# Rules command
			if message.content == "!rules":

				# Create and send rules embed
				# !!! Decide what should be customisable (influences JSON format) (consider making)
				logger.info("`!rules` called by " + message.author.name)  # Event log
				embed_rules = discord.Embed(title=self.data["servers"][str(guild.id)]["rules"]["title"], description="\n".join(self.data["servers"][str(guild.id)]["rules"]["rules list"]), color=0x4f7bc5)
				embed_rules.set_author(name=guild.name, icon_url=guild.icon_url)
				image = self.data["servers"][str(guild.id)]["rules"]["image link"]
				if str(image).startswith("https:"):
					embed_rules.set_image(url=image)
				else:
					logger.debug("Image link non-existant for " + str(guild.id))  # Event log
				await message.channel.send(embed=embed_rules)

				# Delete the command message
				await message.channel.purge(limit=1)

			if message.content == "!roles":
				logger.info("`!roles` called by " + message.author.name)  # Event log

				# Create and send roled embed
				# !!! JSON here also
				embed_roles = discord.Embed(title="Role selection", description="React to get a role, unreact to remove it.", color=0x4f7bc5)
				roles = []
				for role in self.data["servers"][str(guild.id)]["roles"]:
					roles.append(self.data["servers"][str(guild.id)]["roles"][role]["emoji"] + " " + self.data["servers"][str(guild.id)]["roles"][role]["name"])
				embed_roles.add_field(name="Roles", value="\n".join(roles))
				roles_message = await message.channel.send(embed=embed_roles)

				# Add emojis to the roles message
				for role in self.data["servers"][str(guild.id)]["roles"]:
					await roles_message.add_reaction(self.data["servers"][str(guild.id)]["roles"][role]["emoji"])

				# Update the roles message id variable
				self.data["servers"][str(guild.id)]["roles message id"] = roles_message.id

				# Write the updated data
				self.update_data()

				# Delete the command message
				await message.channel.purge(limit=1)

			# Add Role (Arun too smart)
			if message.content.startswith("!add role"):
				parameter = message.content[len("!add role "):]  # Sets parameter to everything after the command
				logger.debug("Parameter: " + parameter)
				# Alters rules using the parameters given

				role_name = ""
				role_id = 0
				role_emoji = ""
				parameters = parameter.split(",")  # Splits parameter string into a list
				for param in parameters:
					logger.debug("Checking: " + param)
					if param.startswith("name="):
						role_name = param[len("name="):]
						# Find role id for role with name
						logger.debug("Roles are:\n" + str(guild.roles))
						for role in guild.roles:
							logger.debug("Role " + role.name)
							if role.name == role_name:
								role_id = role.id
								break
						if role_id == 0:
							logger.error("Role \"" + role_name + "\"was not identified")
					elif param.startswith("emoji="):
						role_emoji_name = param[len("emoji="):]
						for emoji in guild.emojis:
							if emoji.name == role_emoji_name:
								role_emoji = "<:" + role_emoji_name + ":" + str(emoji.id) + ">"
								break
						if role_emoji == "":
							logger.error("Emoji \"" + role_emoji_name + "\"was not identified")

				# Read the data from the file
				with open("data.json", encoding='utf-8') as data_file:
					data = json.load(data_file)
				roles_data = data["servers"][str(guild.id)]["roles"]
				logger.debug(roles_data)

				# Creates new data for server
				new_roles = {
					role_id: {
						"name": role_name,
						"emoji": role_emoji
										}
								}
				logger.debug("Old roles: " + str(roles_data))
				logger.debug("New roles: " + str(new_roles))

				# Merges old and new versions, adding new ones and updating existing ones
				for old_role in roles_data:
					if old_role == new_roles.keys():
						roles_data[old_role.key()] = new_roles
						new_roles.pop(new_roles.keys())

				roles_data.update(new_roles)
				logger.info("Updated roles for "+guild+": " + str(roles_data))

				data["servers"][str(guild.id)]["roles"] = roles_data
				# Write the updated data to the file
				with open("data.json", "w", encoding='utf-8') as data_file:
					json.dump(data, data_file, indent=4)

				self.load_data()

			# Set Rules (Arun too smart)
			if message.content.startswith("!set rules"):
				parameter = message.content[len("!set rules "):]  # Sets parameter to everything after the command

				if parameter == "default":  # Resets rules back to default

					title = "Title"
					#description = "Description"
					image = "none"
					rules = "Rule 1.Rule 2. Rule 3"

				else:  # Alters rules using the parameters given

					parameters = parameter.split(",")  # Splits parameter string into a list
					title = self.data["servers"][str(guild.id)]["rules"]["title"]
					#description = self.data["servers"][str(guild.id)]["rules"]["description"]
					image = self.data["servers"][str(guild.id)]["rules"]["image link"]
					rules = self.data["servers"][str(guild.id)]["rules"]["rules list"]
					for param in parameters:
						if param.startswith("title="):
							title = param[len("title="):]
						#elif param.startswith("description="):
						#	description = param[len("description="):]
						elif param.startswith("image="):
							image = param[len("image="):]
						elif param.startswith("rules="):
							rules = re.split("\.\s|\.", param[len(
								"rules="):])  # Splits the rules after every full stop or, preferably, a full stop followed by a space

				# Read the data from the file
				with open("data.json", encoding='utf-8') as data_file:
					data = json.load(data_file)
				rules_data = data["servers"][str(guild.id)]["rules"]

				# Creates new data for server
				new_rules = {
					"title": title,
					#"description": description,
					"image link": image,
					"rules list": rules
				}
				logger.debug("Old rules: " + str(rules_data))
				logger.debug("New rules: " + str(new_rules))
				rules_data = new_rules

				data["servers"][str(guild.id)]["rules"] = rules_data
				# Write the updated data to the file
				with open("data.json", "w", encoding='utf-8') as data_file:
					json.dump(data, data_file, indent=4)

			if message.content == "!server stats":
				channelsDict = {}
				membersDict = {}

				for channel in guild.text_channels:
					logger.debug("Checking channel: " + channel.name)
					try:
						count = 0
						messages = channel.history(oldest_first=True,limit=None)
						async for x in messages:
							count += 1

						channelsDict.update({channel.name: count})
					except:
						logger.error("Error occurred when scanning channel: "+channel.name+" in server "+guild.name)

				logger.debug("Finished getting messages per channel for "+guild.name)
				for channel in guild.text_channels:
					logger.debug("Checking channel: " + channel.name)
					messages = channel.history(oldest_first=True, limit=None)
					async for message in messages:
						try:
							membersDict[message.author] = membersDict[message.author] + 1  # Increases message count for member in dicitonary
						except KeyError:  # Adds new member to dictionary if they haven't been added before
							try:
								membersDict.update({message.author: 1})
								logger.debug("New member " + str(message.author) + " added to stats dict")
							except UnicodeEncodeError:
								logger.error("A username was too advanced for little Sirius to handle.")

				channelsString = ""
				for key in channelsDict:
					channelsString += "\n"+str(key)+": "+str(channelsDict[key])+"⠀⠀⠀⠀⠀"
				membersString = ""
				for key in membersDict:
					membersString += "\n" + str(key) + ": " + str(membersDict[key])

				embed_stats = discord.Embed(title="Message breakdown for this server", color=0xba5245)
				embed_stats.add_field(name="Channels",value=channelsString,inline=True)
				embed_stats.add_field(name="Members",value=membersString,inline=True)
				embed_stats.set_author(name=guild.name, icon_url=guild.icon_url)
				await message.channel.send(embed=embed_stats)
				logger.info("Server stats for "+guild.name+" compiled and sent!")

			# Sends user rank card image
			if message.content.startswith("!get rank"):
				ranks = self.getGuildRanks(guild)
				updateRankImage(author,ranks[str(author.id)])
				embed_rank = discord.Embed()
				file = discord.File("card.png")
				embed_rank.set_image(url="attachment://card.png")
				await message.channel.send(file=file)
				#await message.channel.send(file=file,embed=embed_rank)

			# Locate command
			if message.content == "!locate":
				logger.info("`!locate` called by " + message.author.name)  # Event log
				hostname = socket.gethostname()
				await message.channel.send(
					"This instance is being run on **" + hostname + "**, IP address **" + socket.gethostbyname(
						hostname) + "**.\n"+str(round((time.time()-startTime)*100)/100)+" seconds uptime")

			# Kill command
			if message.content.startswith("!kill"):
				params = message.content[len("!kill "):]
				# Delete the command message
				await message.channel.purge(limit=1)
				logger.info("`!kill` called by " + message.author.name +params)  # Event log
				if self.data["config"]["jokes"] is True:
					await message.channel.send("Doggie down")
				await message.channel.send(self.user.name+" shutting down after "+str(round((time.time()-startTime)*100)/100)+" seconds uptime\n"+params)
				await client.close()

		if self.data["config"]["jokes"] is True:
			# Joke functionality: Shut up Arun
			if message.author.id == 258284765776576512:

				#logger.info("Arun sighted. Locking on")  # Event log

				if randint(1, 10) == 1:
					if randint(1, 2) == 1:
						await message.channel.send("shut up arun")
					else:
						await message.channel.send("arun, why are you still talking")
					#logger.info("Arun down.")  # Event log
				else:
					pass
					#logger.info("Mission failed, RTB")  # Event log

			# Joke functionality: Shut up Pablo
			if message.author.id == 241772848564142080:

				logger.info("Pablo sighted. Locking on")  # Event log

				if randint(1, 10) == 1:
					logger.info("Revenge protocol ready: affirmative")
					if randint(1, 2) == 1:
						await message.channel.send("shut up pablo")
					else:
						await message.channel.send("pablo, put that big brain back on sleep mode")
					logger.info("Pablo down.")  # Event log
				else:
					logger.info("Mission failed, RTB")  # Event log

			# Joke functionality: Gameboy mention
			if "gameboy" in message.content.lower():
				logger.info("`gameboy` mentioned by " + message.author.name)  # Event log
				await message.channel.send("Gameboys are worthless (apart from micro. micro is cool)")

			# Joke functionality: Raspberry mention
			if "raspberries" in message.content.lower() or "raspberry" in message.content.lower():
				logger.info("`raspberry racers` mentioned by " + message.author.name)  # Event log
				await message.channel.send("The Raspberry Racers are a team which debuted in the 2018 Winter Marble League. Their 2018 season was seen as the second-best rookie team of the year, behind only the Hazers. In the 2018 off-season, they won the A-Maze-ing Marble Race, making them one of the potential title contenders for the Marble League. They eventually did go on to win Marble League 2019.")

			# Joke functionality: Pycharm mention
			if "pycharm" in message.content.lower():
				logger.info("`pycharm` mentioned by " + message.author.name)  # Event log
				await message.channel.send("Pycharm enthusiasts vs Sublime Text enjoyers: https://youtu.be/HrkNwjruz5k")
				await message.channel.send("85 commits in and haha bot print funny is still your sense of humour.")

			# Joke functionality: Token command
			if message.content == "!token":
				logger.info("`!token` called by " + message.author.name)  # Event log
				await message.channel.send("IdrOppED ThE TokEN gUYS!!!!")

			# Joke functionality: Summon lizzie command
			if message.content == "!summon_lizzie":
				logger.info("`!summon_lizzie` called by " + message.author.name)  # Event log
				for x in range(100):
					await message.channel.send(guild.get_member(692684372247314445).mention)

			# Joke functionality: Teaching bitches how to swim
			if message.content == "!swim":
				logger.info("`!swim` called by " + message.author.name)  # Event log
				await message.channel.send("/play https://youtu.be/uoZgZT4DGSY")
				await message.channel.send("No swimming lessons today ):")

			# Joke functionality: Overlay Israel (Warning: DEFCON 1)
			if message.content == "!israeli_defcon_1":
				logger.info("`!israeli_defcon_1` called by " + message.author.name)  # Event log
				await message.channel.send("preemptive apologies...")
				while True:
					await message.channel.send(".overlay israel")



	async def on_member_join(self, member):
		"""Sends a welcome message directly to the user."""

		logger.debug("Member " + member.name + " joined guild [GUILD_NAME]")
		try:
			await member.create_dm()
			await member.dm_channel.send("Welcome to the server, " + member.name + ".")
			logger.debug("Sent welcome message to " + member.name)  # Event log
		except:
			# If user has impeded direct messages
			logger.debug("Failed to send welcome message to " + member.name)  # Event log

	async def on_member_remove(self, member):
		"""Sends a goodbye message directly to the user."""

		logger.debug("Member " + member.name + " left guild [GUILD_NAME]")
		#try:
		await member.create_dm()
		await member.dm_channel.send("Goodbye ;)")
		logger.debug("Sent goodbye message to " + member.name)  # Event log
		#except:
			# If the user has impeded direct messages
		#	logger.debug("Failed to send goodbye message to " + member.name)  # Event log

	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		"""Gives a role based on a reaction emoji."""

		# Make sure that the message the user is reacting to is the one we care about.
		if payload.message_id != self.data["servers"][str(payload.guild_id)]["roles message id"]:
			return

		# Make sure the user isn't the bot.
		if payload.member.id == self.user.id:  # was payload.author
			return

		# Check if we're still in the guild and it's cached.
		guild = self.get_guild(payload.guild_id)
		if guild is None:
			return

		# If the emoji isn't the one we care about then delete it and exit as well.
		role_id = -1
		for id_counter in self.data["servers"][str(guild.id)]["roles"]:
			if self.data["servers"][str(guild.id)]["roles"][id_counter]["emoji"] == str(payload.emoji):
				role_id = int(id_counter)
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

		# Make sure that the message the user is reacting to is the one we care about.
		if payload.message_id != self.data["servers"][str(payload.guild_id)]["roles message id"]:
			return

		# The payload for `on_raw_reaction_remove` does not provide `.member`
		# so we must get the member ourselves from the payload's `.user_id`.

		# Make sure the member still exists and is valid.
		guild = self.get_guild(payload.guild_id)
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
		for id_counter in self.data["servers"][str(guild.id)]["roles"]:
			if self.data["servers"][str(guild.id)]["roles"][id_counter]["emoji"] == str(payload.emoji):
				role_id = int(id_counter)
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
startTime = time.time()
try:
	intents = discord.Intents.default()
	intents.members = True

	client = MyClient(intents=intents, debug=True)
	client.run(DISCORD_TOKEN)

	logger.info("That's all\n")  # Event log
except:

	# This is intended to catch all unexpected shutdowns and put a newline in the log file, since otherwise it becomes concatenated and horrible... Does on_kill exist?
	logger.error("Unexpected exception... Say that ten times fast\n")  # Event log
