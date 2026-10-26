from steps.step import Step
from utils.services.paths import KnownPath


class VagrantStep(Step):
    def __init__(self):
        super().__init__("Vagrant")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("vagrant")

        data_home = self._paths.get(KnownPath.DataHome)
        dependency_dispatcher.set_env("Vagrant paths", "VAGRANT_HOME", f"{data_home}/vagrant")
        dependency_dispatcher.set_env("Vagrant paths", "VAGRANT_ALIAS_FILE", f"{data_home}/vagrant/aliases")
