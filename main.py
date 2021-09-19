# Imports
import math
import time
import json
from datetime import date
import discord
from discord.ext import commands
import discord_components
import discord_slash.error
from discord_slash import SlashCommand
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord.ext.commands import Bot
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType, ActionRow

# Local imports
from log_handling import *
from imaging import generate_rank_card

# Variables
with open("data.json") as file:
	data = json.load(file)
TEMP_SERVER_STRUCTURE = {
	"config": {
		"announcements channel id": None
	}
}

# Cache
roleMessageList = [] # List kept so this whole thing below doesn't have to be done everytime someone wants to change a role. PLEASE STOP LOOKING AT THIS PABLO!!!
for server in data["servers"]:
	#try:
	print(server)
	for category in data["servers"][server]["roles"]["categories"]: # ASSUMES category has one message id but only 5 buttons can be in a message!
		roleMessageList.append(data["servers"][server]["roles"]["categories"][category]["message id"])
	#except KeyError as exception:
	#	print("No categories in " + server+str(exception))
print(roleMessageList)

# Client stuff
#client = discord.Client(intents=discord.Intents.all(), command_prefix="-")
client = commands.Bot(command_prefix="-")


# But first, functions
def update_data():
	"""Writes the updated data to the file."""

	try:
		with open("data.json", "w", encoding='utf-8') as file:
			json.dump(data, file, indent=4)
		logger.debug("Updated data.")
	except Exception as exception:
		logger.error("Failed to update data. Exception: " + exception)


def initialise_guild(guild):
	"""Initialises data for a new guild."""

	try:
		data["servers"][str(guild.id)] = TEMP_SERVER_STRUCTURE
		logger.debug("Initialised guild " + guild.name + " (" + str(guild.id) + ").")
		update_data()
	except Exception as exception:
		logger.error("Failed to initialise guild " + guild.name + " (" + str(guild.id) + "). Exception: " + exception)


# Client events
@client.event
async def on_ready():
	"""Runs when the client is ready."""

	logger.info("`on_ready`")

	# If the guild has announcements enabled, send an announcement into their announcements channel.
	for guild in client.guilds:
		if data["servers"][str(guild.id)]["config"]["announcements channel id"] != None:
			channel = discord.utils.get(guild.channels,id=data["servers"][str(guild.id)]["config"]["announcements channel id"])
			await channel.send("**" + client.user.name + "** online\nVersion [VERSION].")

	print("Ready!")


@client.event
async def on_guild_join(guild):
	"""Runs when the client joins a guild."""

	logger.info("`on_guild_join` " + guild.name + " (" + str(guild.id) + ").")

	# If server data doesn't already exist, initialise server data
	if str(guild.id) not in data["servers"]:
		initialise_guild(guild)


@client.event
async def on_guild_remove(guild):
	"""Runs when the client is removed from a guild."""

	logger.info("`on_guild_remove` " + guild.name + " (" + str(guild.id) + ").")


@client.event
async def on_ready():
	DiscordComponents(client)

	print(f"Logged in as {client.user}!")

	while True:
		response = await client.wait_for("button_click")
		print("Response!")
		if response.message.id in roleMessageList:
			await response.respond(type=InteractionType.UpdateMessage, content=f'{response.component.label} clicked')
			guild = response.guild

			# Check if the roles have been set up
			if len(data["servers"][str(guild.id)]["roles"]) != 0:

				# Check if we're still in the guild and it's cached
				if guild is None:
					return

				# If the emoji isn't the one we care about then delete it and exit as well
				role_id = -1
				for category in data["servers"][str(guild.id)]["roles"]:  # For category in list
					for role in data["servers"][str(guild.id)]["roles"]["categories"][category]["list"]:  # For role in category
						print("Name in data:"+role)
						print("Name from response:"+response.custom_id)
						if role == response.custom_id:
							role_id = int(role)
							break

				# Make sure the role still exists and is valid
				print(role_id)
				role = guild.get_role(role_id)
				if role is None:
					print("Role ain't there chief")
					return

				# Finally, add the role
				try:
					member = guild.get_member(response.user.id) # Converts chad user, to beta member
					await member.add_roles(role)
					logger.info("Role `" + role.name + "` added to " + response.user.name)  # Event log
				# If we want to do something in case of errors we'd do it here
				except Exception as exception:
					logger.error("Failed to add role " + role.name + " to " + response.user.name + ". Exception: " + str(exception))  # Event log


@client.event
async def on_message(message):
	if message.content == "-button":
		await message.send("My Message", components=create_button(style=ButtonStyle.green, label="A␣GreenButton"))

# Buttons command
@slash.slash(
	name="buttons",
	description="Hmm...",
	guild_ids=guild_ids)
async def _buttons(ctx):
	guild = message.guild
	# If the roles have been set up
	if "roles" in data["servers"][str(guild.id)] and len(data["servers"][str(guild.id)]["roles"]) != 0:

		# Delete the command message
		#await message.delete()

		# Send one roles message per category
		await message.channel.send("🗒️ **Role selection**\nReact to get a role, unreact to remove it.")
		for category in data["servers"][str(guild.id)]["roles"]["categories"]:  # For category in roles
			# Message per category
			buttons = []
			rows = []
			buttonRow = []
			fill = 0
			print(guild.id)
			print(category)
			for role in data["servers"][str(guild.id)]["roles"]["categories"][category]["list"]:  # For role in category
				emojiCode = data["servers"][str(guild.id)]["roles"]["categories"][category]["list"][role]["emoji"]
				if emojiCode[:1] == "<":
					for emoji in message.guild.emojis:
						if emoji.name in emojiCode:
							emojiCode = emoji
				if fill < 5:
					buttonRow.append(create_button(style=ButtonStyle.blue, custom_id=role,label=data["servers"][str(guild.id)]["roles"]["categories"][category]["list"][role]["name"], emoji=emojiCode))
					fill += 1
				else:
					buttons.append(buttonRow)
					rows.append(create_actionrow(*buttonRow))
					buttonRow = []
					buttonRow.append(create_button(style=ButtonStyle.blue, custom_id=role,label=data["servers"][str(guild.id)]["roles"]["categories"][category]["list"][role]["name"], emoji=emojiCode))
					fill=0


			# Add button to message per role
			category_message = await message.channel.send(content="Click button to get role", components=rows)

			# Update the category's message id variable
			data["servers"][str(guild.id)]["roles"]["categories"][category]["message id"] = category_message.id
			print("Cat ID: "+str(category_message.id))
			roleMessageList.append(category_message.id)

		# Write the updated data
		update_data()

	# If the roles haven't been set up
	else:
		logger.debug("Roles have not been set up for " + str(message.guild.id))  # Event log
		await message.channel.send(
			"Uh oh, you haven't set up any roles! Get a server admin to set them up at https://www.lingscars.com/")



# Slash command stuff
slash = SlashCommand(client, sync_commands=True)

guild_ids = [834213187468394517, 870789318501871706]


# Ping command
@slash.slash(name="ping", guild_ids=guild_ids)
async def _ping(ctx):
	logger.debug("`/ping` called by " + ctx.author.name + ".")
	await ctx.send(f"Pong! ({client.latency * 1000}ms)")


# Help command
@slash.slash(name="help", description="This is our first description. Woohoo!", guild_ids=guild_ids)
async def _help(ctx):
	logger.debug("`/help` called by " + ctx.author.name + ".")
	embed_help = discord.Embed(title="🤔 Need help?",
							   description="Here's a list of " + client.user.name + "'s commands!", color=0xffc000)
	embed_help.add_field(name=str("/get rank"),
						 value="Creates your rank card, showing your current rank and progress to the next rank.")
	embed_help.add_field(name=str("/embed"), value="Creates an embed. **Documentation needed**...")
	embed_help.add_field(name=str("/help"), value="Creates the bot's help embed, listing the bot's commands.")
	embed_help.add_field(name=str("/rules"), value="Creates the server's rules embed.\nAdmin only feature.")
	embed_help.add_field(name=str("/roles"), value="Creates the server's roles embed.\nAdmin only feature.")
	embed_help.add_field(name=str("/stats"), value="Creates the server's stats embed.\nAdmin only feature.")
	embed_help.add_field(name=str("/locate"),
						 value="Locates the instance of " + client.user.name + ".\nDev only feature.")
	embed_help.add_field(name=str("/kill"), value="Ends the instance of " + client.user.name + ".\nDev only feature.")
	await ctx.send(embed=embed_help)


# Statistics command
@slash.slash(name="stats", guild_ids=guild_ids)
async def _stats(ctx):
	logger.debug("`/stats` called by " + ctx.author.name + ".")

	# Generate statistics
	members = {}
	channel_statistics = ""
	member_statistics = ""
	for channel in ctx.guild.text_channels:
		message_count = 0
		async for message_sent in channel.history(limit=None):
			message_count += 1
			# Don't count messages from bots
			if message_sent.author.bot is False:
				if message_sent.author not in members:
					members[message_sent.author] = 1
				else:
					members[message_sent.author] += 1
		channel_statistics += channel.name + ": " + str(message_count) + "\n"
	for member in members:
		member_statistics += member.name + ": " + str(members[member]) + "\n"

	# Create and send statistics embed
	embed_stats = discord.Embed(title="📈 Statistics for " + ctx.guild.name, color=0xffc000)
	embed_stats.add_field(name="Channels", value=channel_statistics)
	embed_stats.add_field(name="Members", value=member_statistics)
	embed_stats.set_footer(text="Statistics updated • " + date.today().strftime("%d/%m/%Y"),
						   icon_url=ctx.guild.icon_url)
	await ctx.send(embed=embed_stats)


# Run client
with open("token.txt") as file:
	client.run(file.read())