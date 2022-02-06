@client.command()
async def ping(ctx):
	logger.debug(f"`{PREFIX}ping` called by {ctx.author.name}")
	try:
		await ctx.send(f"Pong! {round(client.latency * 1000)}ms")
	except Exception as exception:
		logger.error(f"Failed to run `{PREFIX}ping` in {ctx.guild.name} ({ctx.guild.id})")
