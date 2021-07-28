import json

def upgrade_dict(original,template):
	try:
		for key in template:
			if key not in original:
				original.update(key)
			original[key] = upgrade_dict(original[key],template[key])
			print(original[key])
	except TypeError:
		print("Traversed to base")
	return original

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
		"category list": {
			"Server": {
				"message id": 0,
				"roles list": {}
			}
		}
	},
	"ranks": {}
}

# Load the data file into the data variable
with open("data.json", encoding='utf-8') as file:
	data = json.load(file)

for server in data["servers"]:
	print(upgrade_dict(data["servers"][server],server_structure))