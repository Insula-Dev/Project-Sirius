# Imports
from random import randint
import json
import socket
import discord
import re # Needed for propper regex

# Home imports
from log_handling import *


#Variables
with open("token.txt") as file:
	DISCORD_TOKEN = file.read()


# Definitions
class MyClient(discord.Client):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.data = {}

	async def on_ready(self):

		# Event log
		print(self.user, "is ready.")
		self.load_data(printed=True)

	def load_data(self,printed=False):
		logger.info(self.user.name + " is ready")  # Event log
		if self.guilds != []:
			logger.info(self.user.name + " is connected to the following guilds:")  # Event log
			for guild in self.guilds:
				logger.info(guild.name + " (ID: " + str(guild.id) + ")")  # Event log

		# Load the file data into the data variable
		try:
			with open("data.json", encoding='utf-8') as file:
				self.data = json.load(file)
			logger.info("Loaded data.json")  # Event log
		except:
			logger.critical("Could not load data.json")  # Event log

	async def on_guild_join(self, guild):
		print(self.user, "has joined the guild: " + guild.name + " with id:", guild.id)  # Event log
		# Read the data from the file
		with open("data.json") as data_file:
			data = json.load(data_file)
		servers_data = data["servers"]
		print(servers_data)

		# Checks if the server has already been joined in the past
		try:
			if servers_data[str(guild.id)] != None:
				print("Data for " + guild.name + " already stored.")
		except KeyError:
			print(guild.name + " identified as a new server. First time setup starting.")

			# Create the data for the new server
			new_guild = {"rules":
						{
						"title": "Rules for "+guild.name,
						"description": "[Description]",
						"thumbnail link": "none",
						"list": ["No low quality porn"]
						},
						"roles message id":"none",
						"roles":{}
			}
			servers_data.update({str(guild.id):new_guild})

			data["servers"] = servers_data
			# Write the updated data to the file
			with open("data.json", "w") as data_file:
				json.dump(data, data_file, indent=4)

		#await guild.channels[0].send("Please setup the rules and roles for this bot")

	async def on_message(self, message):

		#logger.debug("Message sent by " + message.author.name)  # Event log

		# Don't respond to yourself
		if message.author.id == self.user.id:
			return

		# Set guild of origin
		guild = self.get_guild(message.guild.id)

		# Rules command
		if message.content == "!rules":

			logger.info("`!rules` called by " + message.author.name)  # Event log

			# Create and send rules embed
			embed_rules = discord.Embed(title=self.data["servers"][str(guild.id)]["rules"]["title"], description="\n".join(self.data["servers"][str(guild.id)]["rules"]["list"]), color=0x4f7bc5, inline=False)
			embed_rules.set_author(name=guild.name, icon_url=guild.icon_url)
			if self.data["servers"][str(guild.id)]["rules"]["thumbnail link"] != "none":
				try:
					embed_rules.set_image(url=self.data["servers"][str(guild.id)]["rules"]["thumbnail link"])
				except discord.erros.HTTPException:
					print("Image broken for "+message.guild.name)
			else:
				print("No thumbnail set")
			await message.channel.send(embed=embed_rules)

		# Roles command
		if message.content == "!roles":

			logger.info("`!roles` called by " + message.author.name)  # Event log

			# Create and send roled embed
			embed_roles = discord.Embed(title="Role selection", description="React to get a role, unreact to remove it.", color=0x4f7bc5)
			roles = []
			for role in self.data["servers"][str(guild.id)]["roles"]:
				roles.append(self.data["servers"][str(guild.id)]["roles"][role]["emoji"] + " " + self.data["servers"][str(guild.id)]["roles"][role]["name"])
			embed_roles.add_field(name="[Games]", value="\n".join(roles))
			roles_message = await message.channel.send(embed=embed_roles)

			# Add emojis to the roles message
			for role in self.data["servers"][str(guild.id)]["roles"]:
				await roles_message.add_reaction(self.data["servers"][str(guild.id)]["roles"][role]["emoji"])

			# Read the data from the file
			with open("data.json") as data_file:
				data = json.load(data_file)
			roles_message_data = data["servers"][str(message.guild.id)]["rules"]
			print(roles_message_data)

			# Creates new data for server
			new_message_data = roles_message.id
			print("Old role message: " + str(roles_message_data))
			print("New role message: " + str(new_message_data))
			rules_data = new_message_data

			data["servers"][str(message.guild.id)]["roles message id"] = rules_data
			# Write the updated data to the file
			with open("data.json", "w") as data_file:
				json.dump(data, data_file, indent=4)

			self.load_data()

		# Add Role
		if message.content.startswith("!add role"):
			parameter = message.content[len("!add role "):] # Sets parameter to everything after the command
			print("Parameter: "+parameter)
			# Alters rules using the parameters given

			role_name = ""
			role_id = 0
			role_emoji = ""
			parameters = parameter.split(",") # Splits parameter string into a list
			for param in parameters:
				print("Checking: "+param)
				if param.startswith("name="):
					print("name")
					role_name = param[len("name="):]
					# Find role id for role with name
					print("Roles are:\n"+str(message.guild.roles))
					for role in message.guild.roles:
						print("Role "+role.name)
						if role.name == role_name:
							role_id = role.id
							break
					if role_id == 0:
						print("Role \""+role_name+"\"was not identified")
				elif param.startswith("emoji="):
					print("emoji")
					role_emoji_name = param[len("emoji="):]
					print(message.guild.emojis)
					for emoji in message.guild.emojis:
						print("Emoji "+emoji.name)
						if emoji.name == role_emoji_name:
							role_emoji = "<:"+role_emoji_name+":"+str(emoji.id)+">"
							break
					if role_emoji == "":
						print("Emoji \""+role_emoji_name+"\"was not identified")


			# Read the data from the file
			with open("data.json") as data_file:
				data = json.load(data_file)
			roles_data = data["servers"][str(message.guild.id)]["roles"]
			print(roles_data)

			# Creates new data for server
			new_roles = {
				role_id :{
					"name":role_name,
					"emoji":role_emoji
					}
				}
			print("Old roles: "+str(roles_data))
			print("New roles: "+str(new_roles))

			# Merges old and new versions, adding new ones and updating existing ones
			for old_role in roles_data:
				if old_role == new_roles.keys():
					roles_data[old_role.key()] = new_roles
					new_roles.pop(new_roles.keys())

			roles_data.update(new_roles)
			print("Updated roles: "+str(roles_data))

			data["servers"][str(message.guild.id)]["roles"] = roles_data
			# Write the updated data to the file
			with open("data.json", "w") as data_file:
				json.dump(data, data_file, indent=4)

			self.load_data()

			# Set Rules
			if message.content.startswith("!set rules"):
				parameter = message.content[len("!set rules "):]  # Sets parameter to everything after the command

				if parameter == "default":  # Resets rules back to default

					title = "Title"
					description = "Description"
					thumbnail = "none"
					rules = "Rule 1.Rule 2. Rule 3"

				else:  # Alters rules using the parameters given

					parameters = parameter.split(",")  # Splits parameter string into a list
					title = self.data["servers"][str(guild.id)]["rules"]["title"]
					description = self.data["servers"][str(guild.id)]["rules"]["description"]
					thumbnail = self.data["servers"][str(guild.id)]["rules"]["thumbnail link"]
					rules = self.data["servers"][str(guild.id)]["rules"]["list"]
					for param in parameters:
						if param.startswith("title="):
							title = param[len("title="):]
						elif param.startswith("description="):
							description = param[len("description="):]
						elif param.startswith("thumbnail="):
							thumbnail = param[len("thumbnail="):]
						elif param.startswith("rules="):
							rules = re.split("\.\s|\.", param[len(
								"rules="):])  # Splits the rules after every full stop or, preferably, a full stop followed by a space

				# Read the data from the file
				with open("data.json") as data_file:
					data = json.load(data_file)
				rules_data = data["servers"][str(message.guild.id)]["rules"]
				print(rules_data)

				# Creates new data for server
				new_rules = {
					"title": title,
					"description": description,
					"thumbnail link": thumbnail,
					"list": rules
				}
				print("Old rules: " + str(rules_data))
				print("New rules: " + str(new_rules))
				rules_data = new_rules

				data["servers"][str(message.guild.id)]["rules"] = rules_data
				# Write the updated data to the file
				with open("data.json", "w") as data_file:
					json.dump(data, data_file, indent=4)

				self.load_data()

		# Joke functionality, shut up Arun
		# Core functionality (do not alter)
		if message.author.id == 258284765776576512:

			logger.info("Arun sighted. Locking on")  # Event log

			if randint(1, 10) == 1:
				await message.channel.send("shut up arun")
				logger.info("Arun down.")  # Event log
			else:
				logger.info("Mission failed, RTB")  # Event log

		# Joke functionality: Gameboy mention
		if "gameboy" in message.content.lower():
			logger.info("`gameboy` mentioned by " + message.author.name)  # Event log
			await message.channel.send("Gameboys are worthless (apart from micro. micro is cool)")

		# Joke functionality: Raspberry mention
		if "raspberries" in message.content or "raspberry" in message.content:
			logger.info("`raspberry racers` mentioned by " + message.author.name)  # Event log
			await message.channel.send("The Raspberry Racers are a team which debuted in the 2018 Winter Marble League. Their 2018 season was seen as the second-best rookie team of the year, behind only the Hazers. In the 2018 off-season, they won the A-Maze-ing Marble Race, making them one of the potential title contenders for the Marble League. They eventually did go on to win Marble League 2019.")

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

		# Locate command
		if message.content == "!locate":
			logger.info("`!locate` called by " + message.author.name)  # Event log
			hostname = socket.gethostname()
			await message.channel.send("This instance is being run on **" + hostname + "**, IP address **" + socket.gethostbyname(hostname) + "**.")

		# Kill command
		if message.content == "!kill":
			logger.info("`!kill` called by " + message.author.name)  # Event log
			await message.channel.send("Doggie down")
			await client.close()

	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		"""Gives a role based on a reaction emoji."""

		# Make sure that the message the user is reacting to is the one we care about.
		if payload.message_id != self.data["servers"][str(payload.guild_id)]["roles message id"]:
			return
		print(1)

		# Check if we're still in the guild and it's cached.
		guild = self.get_guild(payload.guild_id)
		if guild is None:
			return
		print(2)

		# If the emoji isn't the one we care about then exit as well.
		role_id = -1
		for id_counter in self.data["servers"][str(guild.id)]["roles"]:
			if self.data["servers"][str(guild.id)]["roles"][id_counter]["emoji"] == str(payload.emoji):
				role_id = int(id_counter)
				break
		if role_id == -1:
			return
		print(3)

		# Make sure the role still exists and is valid.
		role = guild.get_role(role_id)
		if role is None:
			return
		print(4)

		# Finally, add the role.
		try:
			print("Try to Role `" + role.name + "` added to", payload.member.name)
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

		# Check if we're still in the guild and it's cached.
		guild = self.get_guild(payload.guild_id)
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

		# The payload for `on_raw_reaction_remove` does not provide `.member`
		# so we must get the member ourselves from the payload's `.user_id`.

		# Make sure the member still exists and is valid.
		member = guild.get_member(payload.user_id)
		if member is None:
			return

		# Finally, remove the role.
		try:
			await member.remove_roles(role)
			logger.info("Role `" + role.name + "` removed from " + member.name)  # Event log

		# If we want to do something in case of errors we'd do it here.
		except discord.HTTPException:
			logger.error("Exception: discord.HTTPException. Could not remove role " + role.name + " from ", member.name)  # Event log


# Main body
intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)

logger.info("That's all\n")  # Event log
