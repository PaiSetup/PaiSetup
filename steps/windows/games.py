from steps.step import Step


class GamesStep(Step):
    def __init__(self):
        super().__init__("Games")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "steam-client",
            "minecraft-launcher",
        )

