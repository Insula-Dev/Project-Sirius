# Commands

- `help`
- `ping`
- `8ball poo`

def help(ctx):
  commands = {
    "ping": "Pong",
    "question": "Gives an answer to your question"
}

    if there is an argument:
        ctx.send(help[argument])







sends a poll command
create buttons with ids
ids sent to discord

button press
we're told button id
WE'RE ALSO TOLD
MESSAGE ID

    IF person hasn't got button in the

ADD 1 to the button value count
done





candidates[candidate] = {"name":option, "voters":[1231235432532,563452134124]}

poll = self.data["servers"][str(guild.id)]["poll"]
poll = {guild1:[],guild2:[I am poll]}
poll[str(message.guild.id)].update(
    {str(poll_message.id):
        {
            "title": title,
            "options": {
                "1":
                {
                    "name": "option 1",
                    "voters":[1231235432532,563452134124]
                },
                "2":
                {
                    "name": "option 2",
                    "voters":[563452134124]
                }
            },
            "config": {
            		"winner": winner,
            		"anonymous": anonymous,
                    "multiple": False
            }
        }
    }
)
