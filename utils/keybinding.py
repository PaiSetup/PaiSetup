class KeyBinding:
    def __init__(self, keys):
        self.hold_ctrl = False
        self.hold_shift = False
        self.hold_mod = False
        self.keys = keys
        self.command = ""
        if not isinstance(self.keys, list):
            self.keys = [self.keys]

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
