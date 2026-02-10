from steps.step import Step


class MultimediaToolsStep(Step):
    def __init__(self):
        super().__init__("MultimediaTools")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "audacity",
            # "formatfactory", # TODO-WINDOWS broken package
            "gimp",
            # "irfanview", # TODO-WINDOWS broken package
            "pdfsam.install",
        )
