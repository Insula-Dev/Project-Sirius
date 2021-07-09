# Imports
import json


# Variables
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
				"role list": {}
			}
		}
	},
	"ranks": {},
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
def getval(dct, lst):
	"""Get data.
	Iterative approach."""

	for key in lst[:-1]:
		dct = dct[key]
	return dct[lst[-1]]

def getval_alt(dct, lst):
	"""Get data.
	Recursive approach."""

	if len(lst) == 1:
		return dct[lst[0]]
	else:
		getval_alt(dct[lst[0]], lst[1:])

def setval(dct, lst, val):
	"""Update data.
	Iterative approach."""

	for key in lst[:-1]:
		dct = dct[key]
	dct[lst[-1]] = val

def setval_alt(dct, lst, val):
	"""Update data.
	Recursive approach."""

	if len(lst) == 1:
		dct[lst[0]] = val
	else:
		setval_alt(dct[lst[0]], lst[1:], val)


# Main body
if __name__ == "__main__":

	# Load the data file into the data variable
	with open("data.json", encoding='utf-8') as file:
		data = json.load(file)

	for server in data["servers"]:
		instance = server_structure
		for key in list(instance.keys()):
			print(key)
		for key in list(server.keys()):
			print(key)
			# ... For every variable:
			#value = getval(location)

	"""# For server in servers
	for server in data["servers"]:
		print("Server ID:", server)

		for variable in data["servers"][server]:
			if isinstance(data[server][variable], dict) or isinstance(data[server][variable], list):
				#if type(data[server][variable]) is type({}) or type(data[server][variable]) is type([]):"""
