from utils.log import log, LogIndent


class Step:
    def __init__(self, name):
        self.name = name

    def register_as_dependency_listener(self, dependency_dispatcher):
        pass

    def express_dependencies(self, dependency_dispatcher):
        pass

    def perform(self):
        log(f"Performing step: {self.name}")
        with LogIndent():
            self._perform_impl()

    def _perform_impl(self):
        raise NotImplementedError()
