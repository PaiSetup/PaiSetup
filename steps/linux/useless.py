from xml.dom import minidom

from steps.step import Step
from utils.keybinding import KeyBinding


class UselessStep(Step):
    def __init__(self):
        super().__init__("Useless")

    def push_dependencies(self, dependency_dispatcher):
        packages = [
            "sl",
            "cmatrix",
            "neofetch",
            "asciiquarium",
        ]
        dependency_dispatcher.add_packages(packages)

        commands = [
            "notify-send 'Displaying useless shit on screen'",
            "$TERMINAL_CMD cmatrix",
            "$TERMINAL_CMD bash -c 'neofetch; sleep 999'",
            "$TERMINAL_CMD sl -ade -1000",
            "$TERMINAL_CMD asciiquarium",
        ]
        commands = ") & (".join(commands)
        commands = "(" + commands + ") &"
        dependency_dispatcher.add_keybindings(KeyBinding("u").mod().shift().executeShell(commands).desc("Spawn useless shit on the screen"))
