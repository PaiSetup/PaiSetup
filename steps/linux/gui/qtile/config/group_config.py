from libqtile.config import Group


class GroupConfig:
    def __init__(self):
        self.groups = [Group(i, label="") for i in "123456789"]

        self.web = self.groups[0]
        self.web.label = ""

        self.code = self.groups[1]
        self.code.label = ""

        self.draw = self.groups[7]
        self.draw.label = ""

        self.video = self.groups[8]
        self.video.label = ""
