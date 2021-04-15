#Imports
import discord


#Variables
DISCORD_TOKEN = "ODMxOTQ0NTIyNzQ4NTI2Njg0.YHcmtw.HdYMiGOB9aCX1d_CGUYC8Cqkdew"
GUILD = "The Hat Shop"


#Main body
client = discord.Client()

@client.event
async def on_ready():
	for guild in client.guilds:
		if guild.name == GUILD:
			break

	print(
		f'{client.user} is connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})\n'
	)

	members = '\n - '.join([member.name for member in guild.members])
	print(f'Guild Members:\n - {members}')

@client.event
async def on_member_join(member):
	await member.create_dm()
	await member.dm_channel.send(
		f'Hi {member.name}, welcome to my Discord server!'
	)

@client.event
async def arun_message(message):
	print("Trigger 1")
	print(message.author)

@client.event
async def on_message(message):
	if message.content.startswith("$rules"):
		print(message.content.startswith("$rules"))
		embedVar = discord.Embed(title="rules", description="Desc", color=0x4f7bc5)
		embedVar.add_field(name="Line1", value="1. hello we are not cringe gaming and surival games", inline=False)
		embedVar.add_field(name="Line2", value="2. which is why I say ac", inline=False)
		embedVar.add_field(name="Line3", value="3. disco boost or ban", inline=False)
		await message.channel.send(embed=embedVar)
	elif message.content.startswith("$nice"):
		print("Nice one")
	else:
		print("what?")

client.run(DISCORD_TOKEN)
