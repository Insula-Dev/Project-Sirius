#Imports
from random import randint
import discord


#Variables
DISCORD_TOKEN = "ODMxOTQ0NTIyNzQ4NTI2Njg0.YHcmtw.HdYMiGOB9aCX1d_CGUYC8Cqkdew"
GUILD = "The Hat Shop"


#Definitions
class MyClient(discord.Client):

	async def on_ready(self):

		for guild in self.guilds:
			if guild.name == GUILD:
				break

		print(self.user, "is connected to the following guild:")
		print(guild.name, "(id:", {guild.id})
		print()
		print(self.user.name)
		print(self.user.id)
		print('------')

	async def on_message(self, message):

		if message.author.id == self.user.id:
			return

		if message.content.startswith('!rules'):
			print("!rules called by", message.author)
			await message.channel.send('!rules')

		if message.author.id == 258284765776576512:
			print("Arun sighted. Locking on.")
			if randint(1, 10) == 10:
				await message.channel.send("shut up Arun")
				print("Doggie down.")
			else:
				print("RTB.")


#Main body
client = MyClient()
client.run(DISCORD_TOKEN)
