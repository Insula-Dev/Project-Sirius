# Default features

These features will always be accessible.
- Ping (/ping)
- Help (/help)
- Embed (/embed)
- Statistics (/stats)

# Advanced features

These features aren't necessary, requiring configuration.
- Rules (/rules)
- Roles (/roles)
- Ranks (/get rank)

# Protocol

- Server data is kept in data.json until the bot is pruned.
- The bot is pruned manually, by each server's last activity date.

How is the data.json file formatted?
```json
{
	"config": {},
	"servers": {
		SERVER_ID: {
			"config": {
				"admin role id": ADMIN_ROLE_ID,
				"announcements channel id": ANNOUNCEMENTS_CHANNEL_ID
			},
			"rules": {
				"title": RULES_TITLE,
				"description": RULES_DESCRIPTION,
				"list": RULES_LIST
			},
			"roles": {
				ROLES_CATEGORY_A_NAME: {
					"message id": ROLES_CATEGORY_A_MESSAGE_ID,
					"list": {
						ROLES_CATEGORY_A_ROLE_A_ID: {
							"name": ROLES_CATEGORY_A_ROLE_A_NAME,
							"emoji": ROLES_CATEGORY_A_ROLE_A_EMOJI
						}
					}
				}
			},
			"ranks": RANKS_DATA
		}
	}
}
```

*SERVER_ID* is a string containing the server's ID.

*ADMIN_ROLE_ID* is an integer containing the admin role's ID.
*ANNOUNCEMENTS_CHANNEL_ID* is an integer containing the announcements channel ID.

*RULES_TITLE* is a string containing the title of the rules embed.
*RULES_DESCRIPTION* is a string containing the description of the rules embed.
*RULES_LIST* is a list containing the rules of the rules embed.

*ROLES_CATEGORY_A_NAME* is a string containing the name of the role category.
*ROLES_CATEGORY_A_MESSAGE_ID* is an integer containing the role category message's ID.
*ROLES_CATEGORY_A_ROLE_A_ID* is a string containing the category role's ID.
*ROLES_CATEGORY_A_ROLE_A_NAME* is a string containing the category role's name.
*ROLES_CATEGORY_A_ROLE_A_EMOJI* is a string containing the category role's emoji.

*RANKS_DATA* is a dictionary containing the user IDs (as strings) as keys and the user experience points (as integers) as values.

# FAQs

**Q**: How do I interface with Sirius as a user?
**A**: Use commands through Discord.

**Q**: How do I interface with Sirius as an admin?
**A**: Use admin commands through Discord and the website.

**Q**: How do I interface with Sirius as a developer?
**A**: Use commands through Discord and the website. Use the Sirius interface otherwise.













Pablo brain

on guild join -> check if data? -> yes? no action, no? initialise guild
on guild remove -> keep data.

settings
announcements -> on=announcement_channel_id!=null, off=announcement_channel_id==null

issues
versions don't work
user name can't be retrieved through ctx.user.name in slash commands