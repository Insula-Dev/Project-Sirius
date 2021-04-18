# Imports
from random import randint
import discord
from discord.ext import commands
from discord import File

# Variables
DISCORD_TOKEN = "ODMxOTQ0NTIyNzQ4NTI2Njg0.YHcmtw.f6d4WtNBu73btYi2Lx_LW0564WE"
GUILD_NAME = "The Hat Shop" # The Hat Shop (id: {489893521176920076}

# Easy to reference roles and emojis (name, role id, emoji id)
ping = ["Ping",831945402265239562,"🔔"]
test = ["Test role",832309999908421702,"🦴"]
stardew = ["Stardew",832997725883596820,"<:stardew:832999319665246308>"]
ror = ["Risk Of Rain",832658067158073406,"<:ror:832655432127610880>"]
minecraft = ["Minecraft",832998331756183632,"<:minecraft:832659767951622185>"]
party = ["Party Games",832997546157932585,"<:jackbox:832660115739770961>"]
zombies = ["Zombies",832997616245407815,"<:zombies:833001048867864607>"]

roles = [ping,test,stardew,ror,minecraft,party,zombies]

role_emojis = [] # List of emojis
for x in range(len(roles)):
    role_emojis.append(roles[x][2])
prefix = "!"  # The thing before the command

client = commands.Bot(command_prefix=prefix)


def getUsername(author):
    return str(author)[:-5]


# Rules Response
embedRules = discord.Embed(title="Rules", description="The rules innit", color=0xCE6A76)
embedRules.set_image(url="https://media.discordapp.net/attachments/504791913241772052/504817198028816395/RULES.jpg")
embedRules.add_field(name="Server-wide rules", value="1. Keep spam to a minimum\n\n"
                                                     "2. NSFW in appropriate channels\n\n"
                                                     "3. Use appropriate text / voice channels depending on your activity\n\n"
                                                     "4. Keep fighting and arguing to a minimum, keep it to a DM or another server\n\n"
                                                     "5. No pictures of other people even with said persons permission\n\n"
                                                     "6. No posting other peoples or your personal details\n\n"
                                                     "7. No advertising of any kind including other discord servers\n\n"
                                                     "8. No impersonating other people\n\n"
                                                     "9. Do not ask for Staff\n\n"
                                                     "10. No unnecessary pings\n\n"
                                                     "11. Do not bot abuse\n\n"
                                                     "12. Do not music bot abuse (E . G Earrape, Repeating songs, Ultra Long 'songs')",
                     inline=False)
embedRules.add_field(name="Banned list", value="1. Lindsey#2249", inline=False)



# Roles Response
embedRoles = discord.Embed(title="Role selection", description="React to get a role, unreact to remove it.",
                           color=0x4f7bc5)
embedRoles.add_field(name="Server", value="🔔 Ping", inline=False)

gamesList = ""
for i in range(2,len(roles)):
    gamesList += roles[i][0] + roles[i][2] + "\n"

embedRoles.add_field(name="Games", value=gamesList, inline=False)


""" # This code can be used to quickly do ... other things instead without using Pablo's convoluted class
@client.command()
async def hello(ctx):
    print("Hello activated")
    await ctx.send("Hi")
client.run(DISCORD_TOKEN)
"""

# Definitions
class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_message_id = 833006606609678376
        #self.role_message_id = 832335885470662717  # ID of the message that can be reacted to to add/remove a role.
        # Dictoinary of emojis reffering to roles
        self.emoji_to_role = \
            {
                discord.PartialEmoji(name='🔔'): 831945402265239562, # Number is the role id
                # ID of the role associated with unicode emoji '🔔'
                discord.PartialEmoji(name='🦴'): 832309999908421702,
                # ID of the role associated with unicode emoji '🦴'
                discord.PartialEmoji(name=stardew[2]): stardew[1], # Change to stardew
                # ID of the role associated with a partial emoji's ID
                discord.PartialEmoji(name=ror[2]): ror[1],
                # ID of the role associated with a partial emoji's ID
                discord.PartialEmoji(name=minecraft[2]): minecraft[1],
                # ID of the role associated with a partial emoji's ID
                discord.PartialEmoji(name=party[2]): party[1], # Change to party games
                # ID of the role associated with a partial emoji's ID
                discord.PartialEmoji(name=zombies[2]): zombies[1],  # Change to COD "Zombies"
                # ID of the role associated with a partial emoji's ID
            }

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Gives a role based on a reaction emoji."""

        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id != self.role_message_id:
            return

        # Check if we're still in the guild and it's cached.
        guild = self.get_guild(payload.guild_id)
        if guild is None:
            return

        print(payload.emoji)
        # If the emoji isn't the one we care about then exit as well.
        try:
            print(self.emoji_to_role)
            role_id = self.emoji_to_role[payload.emoji]
            print("Emoji identified")
        except KeyError:
            print("Emoji failed to be identified")
            return

        # Make sure the role still exists and is valid.
        role = guild.get_role(role_id)
        if role is None:
            return

        # Finally, add the role.
        try:
            await payload.member.add_roles(role)
            print("Role added to", payload.member.name)  # Event log

        # If we want to do something in case of errors we'd do it here.
        except discord.HTTPException:
            pass

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Removes a role based on a reaction emoji."""

        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id != self.role_message_id:
            return

        # Check if we're still in the guild and it's cached.
        guild = self.get_guild(payload.guild_id)
        if guild is None:
            return

        # If the emoji isn't the one we care about then exit as well.
        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            return

        # Make sure the role still exists and is valid.
        role = guild.get_role(role_id)
        if role is None:
            return

        # The payload for `on_raw_reaction_remove` does not provide `.member`
        # so we must get the member ourselves from the payload's `.user_id`.

        # Make sure the member still exists and is valid.
        member = guild.get_member(payload.user_id)
        if member is None:
            return

        # Finally, remove the role.
        try:
            await member.remove_roles(role)
            print("Role removed from", member.name)  # Event log

        # If we want to do something in case of errors we'd do it here.
        except discord.HTTPException:
            pass

    async def on_ready(self):

        for guild in self.guilds:
            if guild.name == GUILD_NAME:
                break

        # Event log
        print(self.user, "is connected to the following guild:")
        print(guild.name, "(id:", {guild.id})
        print()
        print(self.user.name)
        print(self.user.id)
        print('------')

    # Runs when any message is received
    async def on_message(self, message):

        # Don't respond to yourself
        if message.author.id == self.user.id:
            return

        # Rules
        if message.content.startswith(prefix + "rules"):
            embedRules.set_author(name=self.get_guild(message.guild.id).name, icon_url=self.get_guild(message.guild.id).icon_url)
            embedRules.set_thumbnail(url="https://media.discordapp.net/attachments/504791913241772052/504817198028816395/RULES.jpg")
            print("`!rules` called by", message.author)  # Event log
            await message.channel.send(embed=embedRules)

        # Roles
        if message.content.startswith(prefix + "roles"):
            print("`!roles` called by", message.author)  # Event log
            rolesMessage = await message.channel.send(embed=embedRoles)
            self.role_message_id = rolesMessage.id
            for emoji in role_emojis:
                await rolesMessage.add_reaction(emoji)

        # Core functionality (do not alter)
        if getUsername(message.author) == "MUIArun":
            print("Arun sighted. Locking on.")  # Event log
            if message.content.startswith("APE"):
                user = message.author
                """try:
                    await user.add_roles(discord.utils.get(user.guild.roles, name="Admin"))
                except Exception as e:
                    await message.channel.send('There was an error running this command ' + str(e))  # if error"""
            elif randint(1, 10) == 1:
                await message.channel.send("shut up arun")
                print("Doggie down.")  # Event log
            else:
                print("Mission failed, RTB.")  # Event log

        if message.content.startswith("!kill"):
            print("You sick bastard.")
            await message.channel.send(file=File("dogdeadinnit.mp3"))

            exit()  # THIS IS A HORRIBLE HEURISTIC





# Main body
intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
