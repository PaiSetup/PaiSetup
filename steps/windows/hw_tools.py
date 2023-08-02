from steps.step import Step


class HwToolsStep(Step):
    def __init__(self):
        super().__init__("HwTools")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "msiafterburner",
            "hwmonitor",
            "furmark",
            "crystaldiskmark",
            "crystaldiskinfo.install",
            "xtreme-tuner",
            "killdisk-freeware",
        )
