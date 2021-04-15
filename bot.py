#Imports
from random import randint
import discord


#Variables
DISCORD_TOKEN = "ODMxOTQ0NTIyNzQ4NTI2Njg0.YHcmtw.f6d4WtNBu73btYi2Lx_LW0564WE"
GUILD_NAME = "The Hat Shop"

role_emojis = ["🔔", "🦴"]

embedRules = discord.Embed(title="Rules", description="The rules innit", color=0x4f7bc5)
embedRules.add_field(name="Server-wide rules", value="1. Keep spam to a minimum\n\n2. NSFW in appropriate channels\n\n3. Use appropriate text / voice channels depending on your activity\n\n4. Keep fighting and arguing to a minimum, keep it to a DM or another server\n\n5. No pictures of other people even with said persons permission\n\n6. No posting other peoples or your personal details\n\n7. No advertising of any kind including other discord servers\n\n8. No impersonating other people\n\n9. Do not ask for Staff\n\n10. No unnecessary pings\n\n11. Do not bot abuse\n\n12. Do not music bot abuse (E . G Earrape, Repeating songs, Ultra Long 'songs')", inline=False)
embedRules.add_field(name="Banned list", value="1. Lindsey#2249", inline=False)

embedRoles = discord.Embed(title="Role selection", description="React to get a role, unreact to remove it.", color=0x4f7bc5)
embedRoles.add_field(name="Server", value="🔔 Ping", inline=False)
embedRoles.add_field(name="Games", value="Destiny 2\nRisk of Rain 2\nMinecraft\nJackbox", inline=False)


#Definitions
class MyClient(discord.Client):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.role_message_id = 832335885470662717  # ID of the message that can be reacted to to add/remove a role.
		self.emoji_to_role = {
			discord.PartialEmoji(name='🔔'): 831945402265239562,  # ID of the role associated with unicode emoji '🔔'.
			discord.PartialEmoji(name='🦴'): 832309999908421702,  # ID of the role associated with unicode emoji '🦴'.
			discord.PartialEmoji(name='jamesracist', id=0): 0,  # ID of the role associated with a partial emoji's ID.
		}

	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		"""Gives a role based on a reaction emoji."""

		#Make sure that the message the user is reacting to is the one we care about.
		if payload.message_id != self.role_message_id:
			return

		#Check if we're still in the guild and it's cached.
		guild = self.get_guild(payload.guild_id)
		if guild is None:
			return

		#If the emoji isn't the one we care about then exit as well.
		try:
			role_id = self.emoji_to_role[payload.emoji]
		except KeyError:
			return

		#Make sure the role still exists and is valid.
		role = guild.get_role(role_id)
		if role is None:
			return

		#Finally, add the role.
		try:
			await payload.member.add_roles(role)
			print("Role added to", payload.member.name)  # Event log

		#If we want to do something in case of errors we'd do it here.
		except discord.HTTPException:
			pass

	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		"""Removes a role based on a reaction emoji."""

		#Make sure that the message the user is reacting to is the one we care about.
		if payload.message_id != self.role_message_id:
			return

		#Check if we're still in the guild and it's cached.
		guild = self.get_guild(payload.guild_id)
		if guild is None:
			return

		#If the emoji isn't the one we care about then exit as well.
		try:
			role_id = self.emoji_to_role[payload.emoji]
		except KeyError:
			return

		#Make sure the role still exists and is valid.
		role = guild.get_role(role_id)
		if role is None:
			return

		#The payload for `on_raw_reaction_remove` does not provide `.member`
		#so we must get the member ourselves from the payload's `.user_id`.

		#Make sure the member still exists and is valid.
		member = guild.get_member(payload.user_id)
		if member is None:
			return

		#Finally, remove the role.
		try:
			await member.remove_roles(role)
			print("Role removed from", member.name)  # Event log

		#If we want to do something in case of errors we'd do it here.
		except discord.HTTPException:
			pass

	async def on_ready(self):

		for guild in self.guilds:
			if guild.name == GUILD_NAME:
				break

		# Event log
		print(self.user, "is connected to the following guild:")
		print(guild.name, "(id:", {guild.id})
		print()
		print(self.user.name)
		print(self.user.id)
		print('------')

	async def on_message(self, message):

		#Don't respond to yourself
		if message.author.id == self.user.id:
			return

		#Rules
		if message.content.startswith("!rules"):
			print("`!rules` called by", message.author)  # Event log
			await message.channel.send(embed=embedRules)

		#Roles
		if message.content.startswith("!roles"):
			print("`!roles` called by", message.author)  # Event log
			await message.channel.send(embed=embedRoles)
			for emoji in role_emojis:
				await message.add_reaction(emoji)

		#Core functionality (do not alter)
		if message.author.id == 258284765776576512:
			print("Arun sighted. Locking on.")  # Event log
			if randint(1, 10) == 1:
				await message.channel.send("shut up arun")
				print("Doggie down.")  # Event log
			else:
				print("Mission failed, RTB.")  # Event log

		if message.content.startswith("!kill"):
			print("You sick bastard.")
			await message.channel.send("https://cdn.discordapp.com/attachments/832293063803142235/832340900587110450/dogdeadinnit.mp3")
			exit()  # THIS IS A HORRIBLE HEURISTIC


#Main body
intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
