# Commands

- `help`
- `ping`
- `8ball poo`

# File structure

## config.json

```JSON
{
	"token": [str, the bot's token],
	"debug": [bool, whether or not the bot boots in debug mode],
	"level": [str, what level the bot outputs debug logs at]
}
```

## data.json

New initialisation:

```JSON
{
	[str, server ID]: {
		"colour": [str, python format hex code for embed colour]
	},
	[...]
}
```

Full initialisation:

```JSON
{
	[str, server ID]: {
		"colour": [str, python format hex code for embed colour],
		"announcement channel": [str, announcement channel ID],
		"confessions": [
			[str, confession],
			[...]
		]
	},
	[...]
}
```
