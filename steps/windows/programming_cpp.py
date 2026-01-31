from steps.step import Step


class ProgrammingCppStep(Step):
    def __init__(self, graphics):
        super().__init__("ProgrammingCpp")
        self._graphics = graphics

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "cmake",
            "doxygen.install",
            "qt5-default",
            "jom",
            "visualstudio2022community",
            "visualstudio2022-workload-nativedesktop",
            "visualstudio2022-workload-nativegame",
        )
        if self._graphics:
            dependency_dispatcher.add_packages("pix")
