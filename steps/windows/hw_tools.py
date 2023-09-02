from steps.step import Step


class HwToolsStep(Step):
    def __init__(self, gaming):
        super().__init__("HwTools")
        self._gaming = gaming

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "hwmonitor",
            "crystaldiskmark",
            "crystaldiskinfo.install",
            # "xtreme-tuner",
            "killdisk-freeware",
        )
        if self._gaming:
            dependency_dispatcher.add_packages(
                "msiafterburner",
                "furmark",
            )
