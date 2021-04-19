class Role:

    def __init__(self, name, roleID, emoji):
        self.name = str(name)
        self.roleID = int(roleID)
        self.emoji = str(emoji)

    def getName(self):
        return self.name

    def getID(self):
        return self.roleID

    def getEmoji(self):
        return self.emoji