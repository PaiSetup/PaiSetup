class KeyBinding:
    def __init__(self, keys):
        self.hold_ctrl = False
        self.hold_shift = False
        self.hold_mod = False
        if type(keys) is str:
            self.keys = [keys]
        elif type(keys) is list:
            self.keys = keys
        else:
            raise ValueError("keys should be a string or a list of strings")
        self.command = ""
        self.command_shell = False
        if not isinstance(self.keys, list):
            self.keys = [self.keys]
        self.description = "UNKNOWN"

    def ctrl(self):
        self.hold_ctrl = True
        return self

    def shift(self):
        self.hold_shift = True
        return self

    def mod(self):
        self.hold_mod = True
        return self

    def execute(self, command):
        self.command = command
        return self

    def executeShell(self, command):
        self.command = command
        self.command_shell = True
        return self

    def desc(self, description):
        self.description = description
        return self
