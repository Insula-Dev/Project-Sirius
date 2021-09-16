# Imports
import time
import json
from datetime import date, datetime
import discord
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option


# Local imports
from log_handling import *
from imaging import generate_rank_card


# Variables
with open("data.json", encoding="utf-8") as file:
	data = json.load(file)
cache = {}
TEMP_SERVER_STRUCTURE = {
	"config": {
		"announcements channel id": None
	}
}


# Functions
def update_data():
	"""Writes the updated data variable to the file."""

	try:
		with open("data.json", "w", encoding='utf-8') as file:
			json.dump(data, file, indent=4)
		logger.debug("Updated data")
	except Exception as exception:
		logger.error("Failed to update data. Exception: " + exception)

def initialise_guild(guild):
	"""Initialises data for a new guild."""

	try:
		data["servers"][str(guild.id)] = TEMP_SERVER_STRUCTURE
		logger.debug("Initialised guild " + guild.name + " (" + str(guild.id) + ")")
		update_data()
	except Exception as exception:
		logger.error("Failed to initialise guild " + guild.name + " (" + str(guild.id) + "). Exception: " + exception)


# Main code
if __name__ == "__main__":
	# Client stuff
	client = discord.Client(intents=discord.Intents.all())

	# Client events
	@client.event
	async def on_ready():
		"""Runs when the client is ready."""

		logger.debug("`on_ready`")

		# If the guild has been added to a guild while offline
		for guild in client.guilds:

			if str(guild.id) not in data["servers"]:
				logger.warning("The bot is in a guild (" + guild.name + " (" + str(guild.id) + ")) but has no data for it.")

				# Initialise guild
				initialise_guild(guild)

		for guild in client.guilds:

			# Initialise cache for guilds
			cache[str(guild.id)] = {}

			try:
				# If the guild has announcements enabled, sends an announcement in their announcements channel
				if data["servers"][str(guild.id)]["config"]["announcements channel id"] != None:
					channel = discord.utils.get(guild.channels, id=data["servers"][str(guild.id)]["config"]["announcements channel id"])
					await channel.send("**" + client.user.name + "** online\nVersion [VERSION].")
			except Exception as exception:
				logger.error("Failed to send announcement message in " + guild.name + " (" + guild.id + ")")

		print("Ready!")

	@client.event
	async def on_guild_join(guild):
		"""Runs when the client joins a guild."""

		logger.debug("`on_guild_join` " + guild.name + " (" + str(guild.id) + ").")

		# If server data doesn't already exist, initialises server data
		if str(guild.id) not in data["servers"]:
			initialise_guild(guild)

	@client.event
	async def on_guild_remove(guild):
		"""Runs when the client is removed from a guild."""

		logger.debug("`on_guild_remove` " + guild.name + " (" + str(guild.id) + ").")

	@client.event
	async def on_message(message):
		"""Runs when a message is sent."""

		logger.debug("Message sent by " + message.author.name + ".")

		# Ignores bots
		if message.author.bot is True:
			return

		# If the ranks functionality is enabled
		if "ranks" in data["servers"][str(message.guild.id)]:
			try:
				if (message.author.id not in cache[str(message.guild.id)]) or ((datetime.now() - cache[str(message.guild.id)][message.author.id]).seconds // 3600 > 0):
					
					# Update the cache and increment the user's experience
					cache[str(message.guild.id)][message.author.id] = datetime.now()
					if str(message.author.id) in data["servers"][str(message.guild.id)]["ranks"]:
						data["servers"][str(message.guild.id)]["ranks"][str(message.author.id)] += 1
					else:
						data["servers"][str(message.guild.id)]["ranks"][str(message.author.id)] = 1

					# Write the updated data
					update_data()

			except Exception as exception:
				logger.error("Failed to add experience to " + message.author.name + " in " + ctx.guild.name + " (" + str(ctx.guild.id) + ")")

	@client.event
	async def on_raw_reaction_add(payload):
		"""Runs when a reaction is added."""

		# If the roles functionality is enabled
		if "roles" in data["servers"][str(payload.guild_id)]:

			try:
				# Ignores bots
				if payload.member.bot is True:
					return

				# Checks if the message is one we care about
				message_relevant = False
				for category in data["servers"][str(payload.guild_id)]["roles"]:
					if payload.message_id == data["servers"][str(payload.guild_id)]["roles"][category]["message id"]:
						message_relevant = True
						break
				if message_relevant is False:
					return

				# Checks if the bot is still in the server and if it's cached
				if client.get_guild(payload.guild_id) is None:
					return

				# Checks if the reaction is one of the ones we care about
				role_id = -1
				for category in data["servers"][str(payload.guild_id)]["roles"]:
					for role in data["servers"][str(payload.guild_id)]["roles"][category]["list"]:
						if str(payload.emoji) == data["servers"][str(payload.guild_id)]["roles"][category]["list"][role]["emoji"]:
							role_id = int(role)
							break
				if role_id == -1:  # Removes the reaction if it one of the ones we care about
					channel = await client.fetch_channel(payload.channel_id)
					message = await channel.fetch_message(payload.message_id)
					if payload.emoji.is_custom_emoji() is False:  # If the emoji is a custom emoji
						reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
					else:  # If the emoji is not a custom emoji
						reaction = discord.utils.get(message.reactions, emoji=payload.emoji)
					await reaction.remove(payload.member)
					return

				# Checks if the role exists and is valid
				role = client.get_guild(payload.guild_id).get_role(role_id)
				if role is None:
					return

				# Adds the role
				await payload.member.add_roles(role)
				logger.debug("Added role " + role.name + " to " + payload.member.name)

			except Exception as exception:
				logger.error("Failed to add role " + role.name + " to " + payload.member.name + ". Exception: " + exception)

	@client.event
	async def on_raw_reaction_remove(payload):
		"""Runs when a reaction is removed."""

		# If the roles functionality is disabled
		if "roles" in data["servers"][str(payload.guild_id)]:

			try:
				# The payload for `on_raw_reaction_remove` does not provide `.member`
				# so we must get the member ourselves from the payload's `.user_id`
				member = client.get_guild(payload.guild_id).get_member(payload.user_id)

				# Ignores bots
				if member.bot is True:
					return

				# Checks if the message is one we care about
				message_relevant = False
				for category in data["servers"][str(payload.guild_id)]["roles"]:
					if payload.message_id == data["servers"][str(payload.guild_id)]["roles"][category]["message id"]:
						message_relevant = True
						break
				if message_relevant is False:
					return

				# Checks if the bot is still in the server and if it's cached
				if client.get_guild(payload.guild_id) is None:
					return

				# Checks if the reaction is one of the ones we care about
				role_id = -1
				for category in data["servers"][str(payload.guild_id)]["roles"]:
					for role in data["servers"][str(payload.guild_id)]["roles"][category]["list"]:
						if str(payload.emoji) == data["servers"][str(payload.guild_id)]["roles"][category]["list"][role]["emoji"]:
							role_id = int(role)
							break

				# Checks if the role exists and is valid
				role = client.get_guild(payload.guild_id).get_role(role_id)
				if role is None:
					return

				# Removes the role
				await member.remove_roles(role)
				logger.debug("Removed role " + role.name + " from " + member.name)
			except Exception as exception:
				logger.error("Failed to remove role " + role.name + " from " + member.name + ". Exception: " + exception)


	# Slash commands
	slash = SlashCommand(client, sync_commands=True)
	guild_ids = [834213187468394517, 870789318501871706]

	# Ping command
	@slash.slash(name="ping", description="Ping test.", guild_ids=guild_ids)
	async def _ping(ctx):
		"""Runs on the ping slash command."""

		logger.debug("`/ping` called by " + ctx.author.name + ".")

		try:
			await ctx.send("Pong! (" + str(round(client.latency, 3)) + "s)")
		except Exception as exception:
			logger.error("Failed to send ping message in " + ctx.guild.name + " (" + str(ctx.guild.id) + ")")

	# Help command
	@slash.slash(name="help", description="Displays help information.", options=[create_option(name="command", description="The slash command you want help with. Leave blank if you want to see help for all commands.", option_type=3, required=False)], guild_ids=guild_ids)
	async def _help(ctx, command=None):
		"""Runs on the help slash command."""

		logger.debug("`/help` called by " + ctx.author.name + ".")

		try:
			if command == None:
				help_embed = discord.Embed(title="🤔 Need help?", description="Here's a list of " + client.user.name + "'s commands!\nFor more detailed help, go to https://www.lingscars.com/", color=0xffc000)
				help_embed.add_field(name=str("/ping"), value="Engage in a ruthless game of table tennis.")
				help_embed.add_field(name=str("/help"), value="Sends the bot's help embed, listing the bot's commands.")
				help_embed.add_field(name=str("/embed"), value="Sends a custom made embed.")
				help_embed.add_field(name=str("/rank"), value="Sends the user's rank card, showing their current rank and their progress to the next rank.")
				help_embed.add_field(name=str("/stats"), value="Sends the server's stats embed.\nAdmin only feature.")
				help_embed.add_field(name=str("/rules"), value="Sends the server's rules embed.\nAdmin only feature.")
				help_embed.add_field(name=str("/roles"), value="Sends the server's roles embed.\nAdmin only feature.")
				await ctx.send(embed=help_embed)
			else:
				if command == "ping":
					help_embed = discord.Embed(title="🗒️ Information for /ping", description="Engage in a ruthless game of table tennis.", color=0xffc000)
					await ctx.send(embed=help_embed)
				elif command == "help":
					help_embed = discord.Embed(title="🗒️ Information for /help", description="Lists the bot's commands.\nOptional parameter `command` specifies the command to display information for.", color=0xffc000)
					await ctx.send(embed=help_embed)
				elif command == "embed":
					help_embed = discord.Embed(title="🗒️ Information for /help", description="Sends a custom made embed.\n Required parameters `title` and `description specify the embed's title and description. Optional parameter `color` specifies the embed's color.", color=0xffc000)
				elif command == "rank":
					help_embed = discord.Embed(title="🗒️ Information for /rank", description="Sends the user's rank card, showing their current rank and their progress to the next rank.", color=0xffc000)
				else:
					await ctx.send("Command not recognised...\nUse `/help` to see all commands and `/help command:` to get help for a specific command.")
		except Exception as exception:
			logger.error("Failed to send help message in " + ctx.guild.name + " (" + str(ctx.guild.id) + ")")

	# Embed command
	@slash.slash(name="embed", description="Sends a custom made embed.", options=[create_option(name="title", description="The embed title.", option_type=3, required=True), create_option(name="description", description="The embed description.", option_type=3, required=True), create_option(name="color", description="The embed color. Takes hexadecimal colour values.", option_type=3, required=False)], guild_ids=guild_ids)
	async def _embed(ctx, title, description, color="0xffc000"):
		"""Runs on the embed slash command."""

		logger.debug("`/embed` called by " + ctx.author.name)

		try:
			try:
				color = int(color, 16)
			except ValueError:
				color = 0xffc000

			embed = discord.Embed(title=title, description=description, color=color)
			embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
			await ctx.send(embed=embed)

		except Exception as exception:
			logger.error("Failed to send embed message in " + ctx.guild.name + " (" + str(ctx.guild.id) + ")")

	# Rank command
	@slash.slash(name="rank", description="Sends the user's rank card, showing their current rank and their progress to the next rank.", guild_ids=guild_ids)
	async def _rank(ctx):
		"""Runs on the rank slash command."""

		logger.debug("`/rank` called by " + ctx.author.name)

		# If the ranks functionality is enabled
		if "ranks" in data["servers"][str(ctx.guild.id)]:

			try:
				# Generates the rank card
				if str(ctx.author.id) in data["servers"][str(ctx.guild.id)]["ranks"]:
					rank = int((data["servers"][str(ctx.guild.id)]["ranks"][str(message.author.id)] ** 0.5) // 1)
					percentage = int(round((data["servers"][str(ctx.guild.id)]["ranks"][str(ctx.author.id)] - (rank ** 2)) / (((rank + 1) ** 2) - (rank ** 2)) * 100))
				else:
					rank = 0
					percentage = 0
				generate_rank_card(ctx.author.avatar_url, ctx.author.name, rank, percentage)

				# Creates and sends the rank embed
				rank_embed = discord.Embed()
				file = discord.File("rank_card.png")
				rank_embed.set_image(url="attachment://rank_card.png")
				await ctx.send(embed=rank_embed)

			except Exception as exception:
				logger.error("Failed to send rank message in " + ctx.guild.name + " (" + str(ctx.guild.id) + ")")

		# If the ranks functionality is disabled
		else:
			await ctx.send("Uh oh, you haven't set up any ranks! Get a server admin to set them up at https://www.lingscars.com/")

	@slash.slash(name="test", description="This is just a test command, nothing more.", options=[create_option(name="optone", description="This is the first option we have.", option_type=3, required=True)])
	async def test(ctx, optone: str):
		await ctx.send(content=f"I got you, you said {optone}!")

	# Admin commands

	# Statistics command
	@slash.slash(name="stats", description="Sends the server's stats embed. Admin only feature.", guild_ids=guild_ids)
	async def _stats(ctx):
		"""Runs on the stats slash command."""

		logger.debug("`/stats` called by " + ctx.author.name + ".")

		try:
			# Generate statistics
			members = {}
			channel_statistics = ""
			member_statistics = ""
			for channel in ctx.guild.text_channels:
				message_count = 0
				async for message_sent in channel.history(limit=None):
					message_count += 1
					if message_sent.author.bot is False:  # Don't count messages from bots
						if message_sent.author not in members:
							members[message_sent.author] = 1
						else:
							members[message_sent.author] += 1
				channel_statistics += channel.name + ": " + str(message_count) + "\n"
			for member in members:
				member_statistics += member.name + ": " + str(members[member]) + "\n"

			# Create and send statistics embed
			stats_embed = discord.Embed(title="📈 Statistics for " + ctx.guild.name, color=0xffc000)
			stats_embed.add_field(name="Channels", value=channel_statistics)
			stats_embed.add_field(name="Members", value=member_statistics)
			stats_embed.set_footer(text="Statistics updated • " + date.today().strftime("%d/%m/%Y"), icon_url=ctx.guild.icon_url)
			await ctx.send(embed=stats_embed)

		except Exception as exception:
			logger.error("Failed to send statistics message in " + ctx.guild.name + " (" + str(ctx.guild.id) + ")")

	# Rules command
	@slash.slash(name="rules", description="Sends the server's rules embed. Admin only feature.", guild_ids=guild_ids)
	async def _rules(ctx):
		"""Runs on the rules slash command."""

		logger.debug("`/rules` called by " + ctx.author.name)

		# If the rules functionality is enabled
		if "rules" in data["servers"][str(ctx.guild.id)]:

			try:
				# Creates and sends the rules embed
				rules_embed = discord.Embed(title=data["servers"][str(ctx.guild.id)]["rules"]["title"], description=data["servers"][str(ctx.guild.id)]["rules"]["description"], color=0xffc000, inline=False)
				rules_embed.set_footer(text="Rules updated • " + date.today().strftime("%d/%m/%Y"), icon_url=ctx.guild.icon_url)
				rules_embed.add_field(name="Rules", value="\n".join(data["servers"][str(ctx.guild.id)]["rules"]["list"]))
				await ctx.send(embed=rules_embed)

			except Exception as exception:
				logger.error("Failed to send rules message in " + ctx.guild.name + " (" + str(ctx.guild.id) + ")")

		# If the rules functionality is disabled
		else:
			await ctx.send("Uh oh, you haven't set up any rules! Get a server admin to set them up at https://www.lingscars.com/")

	# Roles command
	@slash.slash(name="roles", description="Sends the server's roles embed. Admin only feature", guild_ids=guild_ids)
	async def _roles(ctx):
		"""Runs on the roles slash command."""

		logger.debug("`/roles` called by " + ctx.author.name)

		# If the roles functionality is enabled
		if "roles" in data["servers"][str(ctx.guild.id)]:

			try:
				# Creates and sends the roles embed
				await ctx.send("🗒️ **Role selection**\nReact to get a role, unreact to remove it.")
				for category in data["servers"][str(ctx.guild.id)]["roles"]:
					roles = []
					for role in data["servers"][str(ctx.guild.id)]["roles"][category]["list"]:
						roles.append(data["servers"][str(ctx.guild.id)]["roles"][category]["list"][role]["emoji"] + " - " + data["servers"][str(ctx.guild.id)]["roles"][category]["list"][role]["name"] + "\n")
					category_message = await ctx.channel.send("**" + category + "**\n" + "".join(roles))

					# Adds reactions to the roles message
					for role in data["servers"][str(ctx.guild.id)]["roles"][category]["list"]:
						await category_message.add_reaction(data["servers"][str(ctx.guild.id)]["roles"][category]["list"][role]["emoji"])

					# Updates the category's message id
					data["servers"][str(ctx.guild.id)]["roles"][category]["message id"] = category_message.id

				# Write the updated data
				update_data()

			except Exception as exception:
				logger.error("Failed to send roles message in " + ctx.guild.name + " (" + str(ctx.guild.id) + ")")

		# If the roles functionality is disabled
		else:
			await ctx.send("Uh oh, you haven't set up any roles! Get a server admin to set them up at https://www.lingscars.com/")

	# CLS command
	@slash.slash(name="cls", guild_ids=guild_ids)
	async def _cls(ctx):
		"""Runs on the cls slash command."""

		logger.debug("`/cls` called by " + ctx.author.name)

		await ctx.channel.purge(limit=5)

		await ctx.send("You've been purged, son.")


	# Run client
	with open("token.txt") as file:
		client.run(file.read())
