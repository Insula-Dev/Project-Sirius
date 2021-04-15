#Imports
from random import randint
import discord


#Variables
DISCORD_TOKEN = "ODMxOTQ0NTIyNzQ4NTI2Njg0.YHcmtw.f6d4WtNBu73btYi2Lx_LW0564WE"
GUILD = "The Hat Shop"

embedRules = discord.Embed(title="[Rules embed]", description="Desc", color=0x4f7bc5)
embedRules.add_field(name="Line1", value="1. No british people, will be banned on sight", inline=False)
embedRules.add_field(name="Line2", value="2. People from Michigan will be banned on sight", inline=False)
embedRules.add_field(name="Line3", value="3. transgenders boost or ban", inline=False)

embedRoles = discord.Embed(title="Role selection", description="React to get a role, unreact to remove it.", color=0x4f7bc5)
embedRoles.add_field(name="[name]", value="[value]", inline=False)
embedRoles.add_field(name="Server", value="🔔 Ping", inline=False)
embedRoles.add_field(name="Games", value="Risk of Rain 2\nDestiny 2\nMinecraft\nJackbox", inline=False)


#Definitions
class MyClient(discord.Client):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.role_message_id = 832331088323543110  # ID of the message that can be reacted to to add/remove a role.
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
			print("Role added to", payload.member.name)

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
			print("Role removed from", member.name)

		#If we want to do something in case of errors we'd do it here.
		except discord.HTTPException:
			pass

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

		#Rules
		if message.content.startswith("!rules"):
			print("`!rules` called by", message.author)
			await message.channel.send(embed=embedRules)

		#Roles
		if message.content.startswith("!roles"):
			print("`!roles` called by", message.author)
			await message.channel.send(embed=embedRoles)

		#Core functionality (do not alter)
		if message.author.id == 258284765776576512:
			print("Arun sighted. Locking on.")
			if randint(1, 10) == 1:
				await message.channel.send("shut up Arun")
				print("Doggie down.")
			else:
				print("Mission failed, RTB.")


#Main body
intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
