# Imports
import json


# Variables
{
	"config": {
		"rank system": False
	},
	"rules": {
		"title": "",
		"description": "",
		"list": [],
		"image link": ""
	},
	"roles": {
		"admin role id": 0,
		"category list": {
			"Server": {
				"message id": 0,
				"role list": {}
			}
		}
	},
	"ranks": {}
	"polls": {
		"message id": {
			"title" : "poll title",
			"time" : "poll timestamp",
			"options" : {

			}
		}
	}
}


# Functions
def recursion():
	"""Bruh."""

	print()


# Main body
if __name__ == "__main__":

	# Load the data file into the data variable
	with open("data.json", encoding='utf-8') as file:
		data = json.load(file)

	# For server in servers
	for server in data["servers"]:
		print("Server ID:", server)

		for variable in data["servers"][server]:
			if isinstance(data[server][variable], dict) or isinstance(data[server][variable], list):
			#if type(data[server][variable]) is type({}) or type(data[server][variable]) is type([]):
