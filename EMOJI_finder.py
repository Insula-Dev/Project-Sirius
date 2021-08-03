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

	async def on_message(self, message):

		if not message.author.bot:
			print(message.content)
			await message.channel.send(message.content)

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