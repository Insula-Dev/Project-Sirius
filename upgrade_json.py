import json

def upgrade_dict(original,template):
	try:
		if type(template) == type({}):
			for key in template:
				if key != key.upper():
					if key not in original:
						original[key] = template[key]
					original[key] = upgrade_dict(original[key],template[key])
				else:
					for uniqueKey in original:
						original[uniqueKey] = upgrade_dict(original[uniqueKey],template[key])

	except TypeError:
		print("Traversed to base")
	return original

def format_dict(dict):
	dict = str(dict)
	formatted = ""
	level = -1
	for char in dict:
		formatted += char
		if char == "{":
			level += 1
			formatted += "\n" + "	"*level
		elif char == ",":
			formatted += "\n" + "	" * level
		elif char == "}":
			level -= 1
			formatted += "\n" + "	" * level
	return formatted

server_structure = {
	"config": {
		"rank system": False,
		"admin role id": 0,
		"announcements channel id": 0
	},
	"rules": {
		"title": "Server rules",
		"description": "",
		"list": [],
		"image link": ""
	},
	"roles": {
		"categories": {
			"CATEGORY": {
				"message id": 0,
				"pogchamp": 69420,
				"roles": {}
			}
		}
	},
	"ranks": {}
}

# Load the data file into the data variable
with open("data.json", encoding='utf-8') as file:
	data = json.load(file)
for server in data["servers"]:
	print(format_dict(upgrade_dict(data["servers"][server],server_structure)))
	print("---------------------------------------------------\n")
