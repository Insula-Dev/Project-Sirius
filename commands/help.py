@client.command()
async def _help(ctx):
	logger.debug(f"`{PREFIX}help` called by {ctx.author.name}")
	try:
		embed = discord.Embed(title="🤔 Need help?", description=f"Here's a list of {client.user.name}'s commands!", colour=COLOUR)
		embed.add_field(name="__help__", value="...")
		await ctx.send(embed=embed)
	except Exception as exception:
		logger.error(f"Failed to run `{PREFIX}help` in {ctx.guild.name} ({ctx.guild.id})")
