from steps.step import Step


class RaspberryPiStep(Step):
    def __init__(self):
        super().__init__("RaspberryPi")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "putty",
            "screen",
            "rpi-imager-bin",
        )

    def perform(self):
        (self._env.home() / ".config/putty").mkdir(exist_ok=True)
