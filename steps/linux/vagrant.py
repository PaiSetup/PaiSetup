from steps.step import Step


class VagrantStep(Step):
    def __init__(self):
        super().__init__("Vagrant")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("vagrant")

        data_home = self._env.get("XDG_DATA_HOME")
        dependency_dispatcher.set_env("Vagrant paths", "VAGRANT_HOME", f"{data_home}/vagrant")
        dependency_dispatcher.set_env("Vagrant paths", "VAGRANT_ALIAS_FILE", f"{data_home}/vagrant/aliases")
