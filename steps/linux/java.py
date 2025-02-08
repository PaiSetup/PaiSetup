from steps.step import Step


class JavaStep(Step):
    def __init__(self):
        super().__init__("Java")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            # "java-environment-common", # Needed only for JDK
            "java-runtime-common",
            "jre-openjdk",
        )

        # We can move some files to XDG directories with java env variables, but not all. Devs seem
        # to not care. See:
        #    - https://bugs.openjdk.org/browse/JDK-8290140
        #    - https://aur.archlinux.org/packages/openjdk-src-xdg (not checked)
        dependency_dispatcher.register_homedir_file(".java")

    def perform(self):
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Override locations of java cache",
            ['export _JAVA_OPTIONS=-"Djava.util.prefs.userRoot=$XDG_CONFIG_HOME/java -Djavafx.cachedir=$XDG_CACHE_HOME/openjfx"'],
        )
