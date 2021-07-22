# Imports
from random import randint
from datetime import date, datetime
import discord
import socket
import re  # Remove this later lol

# Home imports
from log_handling import *
from imaging import generate_rank_card


async def on_message(PREFIX, self, message):
	"""Runs on message."""

	logger.debug("Message sent by " + message.author.name)  # Event log

	# Don't respond to yourself
	if message.author.id == self.user.id:
		return

	# Don't respond to other bots
	if message.author.bot is True:  # !!! Needs to be tested
		return

	# Set guild of origin
	guild = self.get_guild(message.guild.id)

	# Update the user's experience
	if (message.author.id not in self.cache[str(guild.id)]) or ((datetime.now() - self.cache[str(guild.id)][
		message.author.id]).seconds // 3600 > 0):  # This is the longest like of code I've ever seen survive a scrutinised and picky merge from me. Well played.

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
	if message.content.startswith(PREFIX + "get rank"):

		logger.info("`get rank` called by " + message.author.name)  # Event log

		# Generate the rank card
		if str(message.author.id) in self.data["servers"][str(guild.id)]["ranks"]:
			rank = int((self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] ** 0.5) // 1)
			percentage = int(round((self.data["servers"][str(guild.id)]["ranks"][str(message.author.id)] - (
					rank ** 2)) / (((rank + 1) ** 2) - (rank ** 2)) * 100))
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

	# If the message was sent by the admins
	if guild.get_role(self.data["servers"][str(message.guild.id)]["config"][
		                  "admin role id"]) in guild.get_member(message.author.id).roles:

		# Rules command
		if message.content == PREFIX + "rules":

			logger.info("`rules` called by " + message.author.name)  # Event log

			# Delete the command message
			await message.channel.purge(limit=1)

			# Create the welcome embed !!! This is messy. Decide embed format and what should be customisable
			embed_welcome = discord.Embed(title="👋 Welcome to " + message.guild.name + ".", description="[Discord community server description]\n\nTake a moment to familiarise yourself with the rules below.\nChannel <#831953098800889896> is for this, and <#610595467444879421> is for that.", color=0xffc000)

			# Create the rules embed
			embed_rules = discord.Embed(title=self.data["servers"][str(guild.id)]["rules"]["title"], description=
			self.data["servers"][str(guild.id)]["rules"]["description"], color=0xffc000, inline=False)
			embed_rules.set_footer(text="Rules updated: • " + date.today().strftime("%d/%m/%Y"), icon_url=guild.icon_url)
			embed_rules.add_field(name="Rules", value="\n".join(
				self.data["servers"][str(guild.id)]["rules"]["list"]), inline=True)

			embed_image = discord.Embed(description="That's all.", color=0xffc000)
			image = self.data["servers"][str(guild.id)]["rules"]["image link"]
			try:
				embed_image.set_image(url=self.data["servers"][str(guild.id)]["rules"]["image link"])
			except:
				logger.debug("Image link non-existant for " + str(message.guild.id))  # Event log

			# Send the embeds
			await message.channel.send(embed=embed_welcome)
			await message.channel.send(embed=embed_rules)
			await message.channel.send(embed=embed_image)

		# Roles command
		if message.content == PREFIX + "roles":

			logger.info("`roles` called by " + message.author.name)  # Event log

			# Delete the command message
			await message.channel.purge(limit=1)

			# Send one roles message per category
			await message.channel.send("🗒️ **Role selection**\nReact to get a role, unreact to remove it.")
			for category in self.data["servers"][str(guild.id)]["roles"]["category list"]:  # For category in roles list
				roles = []
				for role in self.data["servers"][str(guild.id)]["roles"]["category list"][category][
					"role list"]:  # For role in category
					roles.append(
						self.data["servers"][str(guild.id)]["roles"]["category list"][category]["role list"][role][
							"emoji"] + " - " +
						self.data["servers"][str(guild.id)]["roles"]["category list"][category]["role list"][role][
							"name"] + "\n")
				category_message = await message.channel.send("**" + category + "**\n\n" + "".join(roles))

				# Add reactions to the roles message
				for role in self.data["servers"][str(guild.id)]["roles"]["category list"][category]["role list"]:
					await category_message.add_reaction(
						self.data["servers"][str(guild.id)]["roles"]["category list"][category]["role list"][role][
							"emoji"])

				# Update the category's message id variable
				self.data["servers"][str(guild.id)]["roles"]["category list"][category][
					"message id"] = category_message.id

			# Write the updated data
			self.update_data()

		# Stats command
		if message.content == PREFIX + "stats":
			"""THINGS TO FIX:

			- Trailing newlines at the end of embed"""

			logger.info("`stats` called by " + message.author.name)  # Event log

			# Generate statistics
			try:
				members = {}
				channel_statistics = ""
				member_statistics = ""
				for channel in guild.text_channels:
					message_count = 0
					async for message_sent in channel.history(limit=None):
						message_count += 1
						# Don't count bot messages
						if message_sent.author.bot is False:
							if message_sent.author not in members:
								members[message_sent.author] = 1
							else:
								members[message_sent.author] += 1
					channel_statistics += channel.name + ": " + str(message_count) + "\n"
				for member in members:
					member_statistics += member.name + ": " + str(members[member]) + "\n"
				logger.debug("Successfully generated statistics")
			except UnicodeEncodeError:
				logger.error("Username " + message_sent.author.name + " was too advanced to handle")
			except Exception as exception:
				logger.error("Failed to generate statistics. Exception: " + str(exception))

			# Create and send statistics embed
			embed_stats = discord.Embed(title="📈 Statistics for " + guild.name, color=0xba5245)
			embed_stats.add_field(name="Channels", value=channel_statistics)
			embed_stats.add_field(name="Members", value=member_statistics)
			embed_stats.set_footer(text="Statistics updated • " + date.today().strftime("%d/%m/%Y"), icon_url=guild.icon_url)
			await message.channel.send(embed=embed_stats)

		# Poll command
		if message.content.startswith(PREFIX + "poll"):
			"""ERRORS TO TEST FOR:

			- Duplicate emojis
			- Custom emojis
			- Duplicate custom emojis

			THINGS TO FIX:

			- Standardise datetime format
			- Remove regex secretly
			- Trailing newlines at the end of embed
			"""

			logger.info("`poll` called by " + message.author.name)  # Event log

			# Delete the command message
			await message.channel.purge(limit=1)

			# !!! Clunky and breakable
			argument_string = message.content[len(PREFIX + "poll "):]
			arguments = re.split("\,\s|\,", argument_string)  # Replace with arguments = argument.split(", ")
			candidates = {}  # Dictionary of candidates that can be voted for
			candidates_string = ""

			# Embed
			title = discord.Embed.Empty
			colour = 0xffc000

			# Config
			winner = "none"

			# Analyse argument
			for argument in arguments:
				argument = argument.split("=")
				#print("Argument 0, 1:", argument[0], argument[1])
				poll_time = str(datetime.now())
				if argument[0] == "title":
					title = argument[1]
				elif argument[0] == "time":
					# Arun's time machine
					time_list = argument[1].split("/")
					hour = 12
					minute = 00
					if ":" in time_list[2]:
						last_time_arg = time_list[2].split(" ")
						time_list[2] = last_time_arg[0]
						hour = last_time_arg[1].split(":")[0]
						minute = last_time_arg[1].split(":")[1]
					poll_time = str(datetime(day=int(time_list[0]), month=int(time_list[1]), year=int(time_list[2]), hour=int(hour), minute=int(minute)))  # Accommodate for American convention. Or don't.
				elif argument[0] == "colour":
					if argument[0].startswith("0x"):
						colour = int(argument[1][2:],16)
					elif argument[0].startswith("#"):
						colour = int(argument[1][1:],16)
					else:
						colour = int(argument[1],16)
					print(colour)
				elif argument[0] == "winner":
					winner = argument[1]
				else:
					candidates[argument[1].rstrip()] = argument[0]
					candidates_string += argument[1] + " - " + argument[0] + "\n"

			# Create and send poll embed
			embed_poll = discord.Embed(title=title, description=candidates_string, color=colour)
			embed_poll.set_footer(text="Poll ending • " + poll_time)
			poll_message = await message.channel.send(embed=embed_poll)

			self.poll[str(message.guild.id)].update({str(poll_message.id): {
				"title": title,
				"time": str(poll_time),
				"options": candidates,
				"config":
					{
						"winner": winner
					}
			}
			})

			print(self.poll[str(message.guild.id)])

			# Add reactions to the poll embed
			for candidate in candidates:
				#print("Candidate: " + str(candidate))
				await poll_message.add_reaction(candidate)

	# If the message was sent by the developers
	if message.author.id in self.data["config"]["developers"]:

		# Locate command
		if message.content == PREFIX + "locate":
			logger.info("`locate` called by " + message.author.name)  # Event log
			hostname = socket.gethostname()
			await message.channel.send("This instance is being run on **" + hostname + "**, IP address **" + socket.gethostbyname(hostname) + "**.\nUptime: " + self.get_uptime() + ".")

		# Kill command
		if message.content.startswith(PREFIX + "kill"):

			logger.info("`kill` called by " + message.author.name)  # Event log

			# !!! Clunky and breakable?
			argument = message.content[len(PREFIX + "kill "):]
			if self.data["config"]["jokes"] is True:
				await message.channel.send("Doggie down")
			await message.channel.send(self.user.name + " shutting down.\nUptime: " + self.get_uptime() + ".\n" + argument)
			await client.close()

	# Joke functionality
	if self.data["config"]["jokes"] is True:

		# Shut up Arun
		if message.author.id == 258284765776576512:

			logger.debug("Arun sighted. Locking on")  # Event log

			if randint(1, 10) == 1:
				await message.channel.send("shut up arun")
				logger.debug("Arun down.")  # Event log
			else:
				logger.debug("Mission failed, RTB")  # Event log

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
			await message.channel.send("85 commits in and haha bot print funny is still your sense of humour.")

		# Token command
		if message.content == PREFIX + "token":
			logger.debug("`token` called by " + message.author.name)  # Event log
			await message.channel.send("IdrOppED ThE TokEN gUYS!!!!")

		# Summon lizzie command
		if message.content == PREFIX + "summon_lizzie":
			logger.debug("`summon_lizzie` called by " + message.author.name)  # Event log
			for x in range(100):
				await message.channel.send(guild.get_member(692684372247314445).mention)

		# Summon leo command
		if message.content == PREFIX + "summon_leo":
			logger.debug("`summon_leo` called by " + message.author.name)  # Event log
			for x in range(100):
				await message.channel.send(guild.get_member(242790351524462603).mention)

		# Teaching bitches how to swim
		if message.content == PREFIX + "swim":
			logger.debug("`swim` called by " + message.author.name)  # Event log
			await message.channel.send("/play https://youtu.be/uoZgZT4DGSY")
			await message.channel.send("No swimming lessons today ):")

		# Overlay Israel (Warning: DEFCON 1)
		if message.content == PREFIX + "israeli_defcon_1":
			logger.debug("`israeli_defcon_1` called by " + message.author.name)  # Event log
			await message.channel.send("preemptive apologies...")
			while True:
				await message.channel.send(".overlay israel")
	return self
