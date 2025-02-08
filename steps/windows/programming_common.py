from steps.step import Step


class ProgrammingCommonStep(Step):
    def __init__(self):
        super().__init__("ProgrammingCommon")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "hxd",
            "graphviz",
            "sysinternals",
            "vagrant",
        )
