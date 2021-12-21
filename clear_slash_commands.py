import json

from discord_slash.utils.manage_commands import remove_all_commands

async def clearCommands():
	with open("config.json", encoding='utf-8') as file:
		config = json.load(file)
		await remove_all_commands(831944522748526684,config["token"],None)

#clearCommands()