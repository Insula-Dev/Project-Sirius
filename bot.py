# Imports
from random import randint
import json
import socket
import discord

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

		logger.info(self.user.name + " is ready.")  # Event log
		if self.guilds != []:
			logger.info(self.user.name + " is connected to the following guilds:")  # Event log
			for guild in self.guilds:
				logger.info(guild.name + " (ID: " + str(guild.id) + ")")  # Event log

		# Load the file data into the data variable
		try:
			with open("data.json", encoding='utf-8') as file:
				self.data = json.load(file)
			logger.info("Loaded data.json.")  # Event log
		except:
			logger.critical("Could not load data.json.")  # Event log

	async def on_message(self, message):

		logger.debug("Message sent by " + message.author.name)  # Event log

		# Don't respond to yourself
		if message.author.id == self.user.id:
			return

		# Set guild of origin
		guild = self.get_guild(message.guild.id)

		# Rules command
		if message.content == "!rules":

			logger.info("`!rules` called by " + message.author.name)  # Event log

			# Create and send rules embed
			embed_rules = discord.Embed(title=self.data["servers"][str(guild.id)]["rules"]["title"], description="\n".join(self.data["servers"][str(guild.id)]["rules"]["rules list"]), color=0x4f7bc5)
			embed_rules.set_author(name=guild.name, icon_url=guild.icon_url)
			embed_rules.set_image(url=self.data["servers"][str(guild.id)]["rules"]["image link"])
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

		# Joke functionality: Shut up Arun
		if message.author.id == 258284765776576512:

			logger.info("Arun sighted. Locking on.")  # Event log

			if randint(1, 10) == 1:
				await message.channel.send("shut up arun")
				logger.info("Arun down.")  # Event log
			else:
				logger.info("Mission failed, RTB.")  # Event log

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

		# Finally, add the role.
		try:
			await payload.member.add_roles(role)
			logger.info("Role `" + role.name + "` added to " + payload.member.name)  # Event log

		# If we want to do something in case of errors we'd do it here.
		except discord.HTTPException:
			logger.error("Exception: discord.HTTPException. Could not add role " + role.name + "to" + payload.member.name)  # Event log

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
			logger.error("Exception: discord.HTTPException. Could not remove role " + role.name + "from", member.name)  # Event log


# Main body
intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)

logger.info("That's all.\n")  # Event log
