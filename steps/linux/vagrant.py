from steps.step import Step


class VagrantStep(Step):
    def __init__(self):
        super().__init__("Vagrant")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("vagrant")

    def perform(self):
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Override locations of vagrant home",
            [
                'export VAGRANT_HOME="$XDG_DATA_HOME"/vagrant',
                'export VAGRANT_ALIAS_FILE="$XDG_DATA_HOME"/vagrant/aliases',
            ],
        )
