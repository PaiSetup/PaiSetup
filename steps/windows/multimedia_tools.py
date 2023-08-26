from steps.step import Step


class MultimediaToolsStep(Step):
    def __init__(self):
        super().__init__("MultimediaTools")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "audacity",
            # "formatfactory", # broken package
            "gimp",
            "irfanview",
            "pdfsam.install",
        )
