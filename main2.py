import discord
from discord_slash import SlashCommand # Importing the newly installed library.

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

@client.event
async def on_ready():
	print("Ready!")

guild_ids = [834213187468394517] # Put your server ID in this array.

@slash.slash(name="ping", guild_ids=guild_ids)
async def _ping(ctx): # Defines a new "context" (ctx) command called "ping."
	await ctx.send(f"Pong! ({client.latency*1000}ms)")

@slash.slash(name="help", guild_ids=guild_ids)
async def _help(ctx):
	await ctx.send()

with open("token.txt") as file:
	client.run(file.read())
