from steps.step import Step
from utils.services.paths import KnownPath


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

        config_home = self._paths.get(KnownPath.ConfigHome)
        cache_home = self._paths.get(KnownPath.CacheHome)
        data_home = self._paths.get(KnownPath.DataHome)
        dependency_dispatcher.set_env(
            "Override locations of java cache",
            "_JAVA_OPTIONS",
            f"-Djava.util.prefs.userRoot={config_home}/java -Djavafx.cachedir={cache_home}/openjfx",
        )
        dependency_dispatcher.set_env("Override locations of java cache", "GRADLE_USER_HOME", f"{data_home}/gradle")
