import utils


class WarningHub:
    def __init__(self):
        self._warnings = []

    def push(self, text, print=True):
        self._warnings.append(text)
        if print:
            utils.log.log(f"WARNING: {text}")

    def finalize(self):
        print()
        for text in self._warnings:
            print(f"WARNING: {text}")