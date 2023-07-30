from steps.step import Step
from utils.log import log


class VscodeStep(Step):
    def __init__(self, root_build_dir):
        super().__init__("Vscode")
        self._root_build_dir = root_build_dir

    def perform(self):
        log("Hello from VsCodeStep")
