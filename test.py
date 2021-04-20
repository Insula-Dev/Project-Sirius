# Imports
from random import randint
import json

data = {}
with open("data.json") as data_file:
	guildId = "489893521176920076"
	guildName = "The Hat Shop"
	print(guildName, "(id:", guildId, ")")  # Event log
	guild_data = json.load(data_file)["servers"][guildId]

	# Prepares roles dict to put in data dict
	roles = {}
	"""
	for role in guild_data["roles"]:
		roles[int(role)] = role

		print(roles)"""

	# Adds python readable roles dict to data dict
	data[guild.id] = guild_data
	print(guild_data["roles"])
	for role in guild_data["roles"]:
		print("A role is : "+ role)
		data[guildId]["roles"].update({int(role):guild_data["roles"][role]})
		print("Data "+data[guildId])
		print("Roles key "+ str(roles.keys()))
		data[guildId]["roles"][int(roles.keys())] = role