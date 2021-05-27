# Project-Sirius

>   Sirius rises late in the dark, liquid sky
>   
>   On summer nights, star of stars,
>   
>   Orion's Dog they call it, brightest
>   
>   Of all, but an evil portent, bringing heat
>   
>   And fevers to suffering humanity.

# Instructions

1. If you pull from a branch, it can only be to create another branch.
2. If you merge into a branch, the merge must be reviewed by over 50% of developers.
3. Branches must be well, explicitly named.
4. Branches must only include changes which are relevant to their name.
5. No forks: spoons only.
6. No working past 2am unless all developers are involved and have agreed to this.
7. No working past 2:15am.

## FAQs:

**Q**: What constitutes a review?
**A**: When over 50% of developers review your code.

**Q**: What is good?
**A**: What over 50% of developers deem to be good.

**Q**: Who can disobey these instructions?
**A**: Not Arun or Pablo.

# Instructions (old) [How to develop this code (**important**)]

If you're just touching up some of the main code, pull from and push to master branch. However, if you're adding wholly new functionality to the project, *even if this affects code from the master branch*, create a pull request and develop this on a **well named** branch. When you want to merge back into the master branch, or once you've had enough of testing it, then you'll need to sort through each change everyone else has made to the existing code and be careful not to keep old code. Wherever functionality or conventions conflict, invoke everybody involved and prepare to get your ass handed to you.

That is all.

Thanks.

# File structure

## data.json

```
{
    "config": {
        "developers": [
            DEVELOPER_ID
        ]
    },
    "servers": {
        "SERVER_ID": {
            "rules": {
                "title": "RULES_TITLE",
                "list": [
                    "RULE"
                ],
                "image link": "IMAGE_LINK"
            },
            "roles": {
                "admin role id": ADMIN_ROLE_ID,
                "message id": ROLES_MESSAGE_ID,
                "category list": {
                    "CATEGORY_NAME": {
                        "message id": MESSAGE_ID,
                        "role list": {
                            "ROLE_ID": {
                                "name": "ROLE_NAME",
                                "emoji": "ROLE_EMOJI"
                            }
                        }
                    }
                }
            },
            "ranks": {
                "USER_ID": XP_AMOUNT
            }
        }
    }
}
```

# History

The annals of dog.
No naming people.

## The Holy Merge

It is wrought in the eternal will of the creator that someday the Two Branches of Sirius should finally merge properly. The day of reckoning is feared amongst all competent programmers, and otherwise dismissed by those who do not understand its gravity...

## The Great Schism

The combined forces of the opposing branches unified into one ungodly, unmergeable branch.

## The Great Disappointment

One of the developers stayed up and considered doing the Great Mergening by himself because he can't spend his time doing the right things. Instead he reinvented part of the bot. What an idiot.

## I want to go back to a normal sleep schedule.

# Appease Arun: Priority 1

- Consider changing convention to message.author to author = message.author. For example:
    `guild_data = self.data["servers"][str(guild.id)]`
