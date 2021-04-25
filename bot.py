#Imports
from random import randint
import json
import discord


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
		if self.guilds != []:
			print(self.user, "is connected to the following guilds:")
			for guild in self.guilds:
				print(guild.name + " (ID: " + str(guild.id) + ")")

		# Load the file data into the data variable
		with open("data.json", encoding='utf-8') as file:
			self.data = json.load(file)

		print("------")  # Event log

	async def on_message(self, message):

		print("Message sent by", message.author)  # Event log

		# Don't respond to yourself
		if message.author.id == self.user.id:
			return

		# Set guild of origin
		guild = self.get_guild(message.guild.id)

		# Rules command
		if message.content == "!rules":

			# Create and send rules embed
			embed_rules = discord.Embed(title=self.data["servers"][str(guild.id)]["rules"]["title"], description="\n".join(self.data["servers"][str(guild.id)]["rules"]["rules list"]), color=0x4f7bc5)
			embed_rules.set_author(name=guild.name, icon_url=guild.icon_url)
			embed_rules.set_image(url=self.data["servers"][str(guild.id)]["rules"]["image link"])
			await message.channel.send(embed=embed_rules)

		# Roles command
		if message.content == "!roles":
			print("`!roles` called by", message.author)  # Event log

			# Create and send roled embed
			embed_roles = discord.Embed(title="Role selection", description="React to get a role, unreact to remove it.", color=0x4f7bc5)
			roles = []
			for role in self.data["servers"][str(guild.id)]["roles"]:
				roles.append(self.data["servers"][str(guild.id)]["roles"][role]["emoji"] + " " + self.data["servers"][str(guild.id)]["roles"][role]["name"])
			embed_roles.add_field(name="[Games]", value="\n".join(roles))
			roles_message = await message.channel.send(embed=embed_roles)

			# Add emojis to the roles message
			for role in self.data["servers"][str(guild.id)]["roles"]:
				print(role, self.data["servers"][str(guild.id)]["roles"][role]["emoji"])
				await roles_message.add_reaction(self.data["servers"][str(guild.id)]["roles"][role]["emoji"])

		# Joke functionality: Shut up Arun
		if message.author.id == 258284765776576512:
			print("Arun sighted. Locking on.")  # Event log
			if randint(1, 10) == 1:
				print("Arun down.")  # Event log
				await message.channel.send("shut up arun")
			else:
				print("Mission failed, RTB.")  # Event log

		# Joke functionality: Gameboy mention
		if "gameboy" in message.content.lower():
			print("`gameboy` mentioned by", message.author)  # Event log
			await message.channel.send("Gameboys are worthless (apart from micro. micro is cool)")

		# Joke functionality: Raspberry mention
		if "raspberries" in message.content or "raspberry" in message.content:
			print("`raspberry racers` mentioned by", message.author)  # Event log
			await message.channel.send("The Raspberry Racers are a team which debuted in the 2018 Winter Marble League. Their 2018 season was seen as the second-best rookie team of the year, behind only the Hazers. In the 2018 off-season, they won the A-Maze-ing Marble Race, making them one of the potential title contenders for the Marble League. They eventually did go on to win Marble League 2019.")

		# Joke functionality: Token command
		if message.content == "!token":
			print("`!token` called by", message.author)  # Event log
			await message.channel.send("IdrOppED ThE TokEN gUYS!!!!")

		if message.content == "!summon_lizzie":
			print("`!summon_lizzie` called by", message.author)
			for x in range(100):
				await message.channel.send(guild.get_member(258284765776576512).mention)

		# Kill command
		if message.content == "!kill":
			print("`!kill` called by", message.author)  # Event log
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
			print("Role `" + role.name + "` added to", payload.member.name)  # Event log

		# If we want to do something in case of errors we'd do it here.
		except discord.HTTPException:
			print("Exception: discord.HTTPException. Could not add role", role.name, "to", payload.member.name)  # Event log

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
			if self.data["servers"][str(guild.id)]["roles"][id_counter]["emoji"] == str(payload.emoji):  # TYPE? AS ABOVE
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
			print("Role `" + role.name + "` removed from", member.name)  # Event log

		# If we want to do something in case of errors we'd do it here.
		except discord.HTTPException:
			print("Exception: discord.HTTPException. Could not remove role", role.name, "from", payload.member.name)  # Event log


# Main body
intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)

print("That's all.")
