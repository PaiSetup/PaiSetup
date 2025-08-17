from steps.step import Step


class ProgrammingJavaStep(Step):
    def __init__(self, include_android):
        super().__init__("ProgrammingJava")
        self._include_android = include_android

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            # "java-environment-common", # Needed only for JDK
            "java-runtime-common",
            "jre-openjdk",
        )
        if self._include_android:
            dependency_dispatcher.add_packages("android-studio")

        # We can move some files to XDG directories with java env variables, but not all. Devs seem
        # to not care. See:
        #    - https://bugs.openjdk.org/browse/JDK-8290140
        #    - https://aur.archlinux.org/packages/openjdk-src-xdg (not checked)
        dependency_dispatcher.register_homedir_file(".java")
        if self._include_android:
            dependency_dispatcher.register_homedir_file(".android")
            dependency_dispatcher.register_homedir_file("Android")

    def perform(self):
        self._file_writer.write_section(
            ".config/PaiSetup/env.sh",
            "Override locations of java cache",
            [
                'export _JAVA_OPTIONS=-"Djava.util.prefs.userRoot=$XDG_CONFIG_HOME/java -Djavafx.cachedir=$XDG_CACHE_HOME/openjfx"',
                'export GRADLE_USER_HOME="$XDG_DATA_HOME"/gradle',
            ],
        )
