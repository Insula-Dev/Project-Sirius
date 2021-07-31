# Imports
import time
import json
from datetime import date
import discord
from discord_slash import SlashCommand


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


# Client stuff
client = discord.Client(intents=discord.Intents.all())

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
			channel = discord.utils.get(guild.channels, id=data["servers"][str(guild.id)]["config"]["announcements channel id"])
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




# Slash command stuff
slash = SlashCommand(client, sync_commands=True)

guild_ids = [834213187468394517, 870789318501871706]

# Ping command
@slash.slash(name="ping", guild_ids=guild_ids)
async def _ping(ctx):
	logger.debug("`/ping` called by " + ctx.author.name + ".")
	await ctx.send(f"Pong! ({client.latency*1000}ms)")

# Help command
@slash.slash(name="help", description="This is our first description. Woohoo!", guild_ids=guild_ids)
async def _help(ctx):
	logger.debug("`/help` called by " + ctx.author.name + ".")
	embed_help = discord.Embed(title="🤔 Need help?", description="Here's a list of " + client.user.name + "'s commands!", color=0xffc000)
	embed_help.add_field(name=str("/get rank"), value="Creates your rank card, showing your current rank and progress to the next rank.")
	embed_help.add_field(name=str("/embed"), value="Creates an embed. **Documentation needed**...")
	embed_help.add_field(name=str("/help"), value="Creates the bot's help embed, listing the bot's commands.")
	embed_help.add_field(name=str("/rules"), value="Creates the server's rules embed.\nAdmin only feature.")
	embed_help.add_field(name=str("/roles"), value="Creates the server's roles embed.\nAdmin only feature.")
	embed_help.add_field(name=str("/stats"), value="Creates the server's stats embed.\nAdmin only feature.")
	embed_help.add_field(name=str("/locate"), value="Locates the instance of " + client.user.name + ".\nDev only feature.")
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
	embed_stats.set_footer(text="Statistics updated • " + date.today().strftime("%d/%m/%Y"), icon_url=ctx.guild.icon_url)
	await ctx.send(embed=embed_stats)


# Run client
with open("token.txt") as file:
    client.run(file.read())
