# Imports
from random import randint
import json
import discord
# Variables
with open("token.txt") as token_file:
	DISCORD_TOKEN = token_file.read()
#GUILD_NAME = "The Hat Shop"

data = {}
# Definitions
class MyClient(discord.Client):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_ready(self):

		# Maintenance problem with translation between JSON string-keys and Python int-keys below
		if self.guilds != []:
			with open("data.json") as data_file:
				for guild in self.guilds:
					guild_data = json.load(data_file)["servers"][str(guild.id)] # Loads server's dictionary

					# New fancy thing Arun made to make guild_data["roles"] correct for python
					guild_data_roles = guild_data["roles"].copy()
					for role in guild_data["roles"]:
						guild_data_roles[int(role)] = guild_data_roles[role]
						del guild_data_roles[role]
					guild_data["roles"] = guild_data_roles

					data.update({int(guild.id):guild_data})

	async def on_message(self, message):


		# Bot kill command
		if message.content.startswith("!kill"):
			await message.channel.send("Killed emoji finder")

			await client.close()
			exit()  # This isn't a good heuristic. Find discord.py way of getting this done.

	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		"""Gives a role based on a reaction emoji."""

		print(payload.emoji)




# Main body
intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
