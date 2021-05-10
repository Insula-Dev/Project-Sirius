# Project-Sirius

Sirius rises late in the dark, liquid sky
On summer nights, star of stars,
Orion's Dog they call it, brightest
Of all, but an evil portent, bringing heat
And fevers to suffering humanity.

## How to develop this code (**important**)

If you're just touching up some of the main code, pull from and push to master branch. However, if you're adding wholly new functionality to the project, *even if this affects code from the master branch*, create a pull request and develop this on a **well named** branch. When you want to merge back into the master branch, or once you've had enough of testing it, then you'll need to sort through each change everyone else has made to the existing code and be careful not to keep old code. Wherever functionality or conventions conflict, invoke everybody involved and prepare to get your ass handed to you.

That is all.

Thanks.

# File structure

## data.json

```
{
    "bot": {},
    "servers": {
        "SERVER_ID": {
            "rules": {
                "title": "RULES_TITLE",
                "rules list": [
                    "RULE_1",
                    ...
                    "RULE_N"
                ],
                "image link": "IMAGE_LINK"
            },
            "roles message id": ROLES_MESSAGE_ID,
            "roles": {
                "ROLE_ID": {
                    "name": "ROLE_NAME",
                    "emoji": "ROLE_EMOJI"
                }
            }
        }
    }
}
```

Add rules to code.

Protocol for adding bot to new server needed...

# History

The annals of dog.

## The Holy Merge

It is wrought in the eternal will of the creator that someday the Two Branches of Sirius should finally merge properly. The day of reckoning is feared amongst all competent programmers, and otherwise dismissed by those who do not understand its gravity...