from steps.step import Step


class JavaStep(Step):
    def __init__(self):
        super().__init__("Java")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "java-environment-common",
            "java-runtime-common",
        )

    def perform(self):
        self._file_writer.write_section(
            ".config/LinuxSetup/xinitrc_base",
            "Override locations of java cache",
            ['export _JAVA_OPTIONS=-Djava.util.prefs.userRoot="$XDG_CONFIG_HOME"/java'],
        )
