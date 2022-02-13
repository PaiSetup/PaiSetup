from utils.log import log, LogIndent


class Step:
    def __init__(self, name, has_action=True):
        self.name = name
        self.has_action = has_action

    def register_as_dependency_listener(self, dependency_dispatcher):
        pass

    def express_dependencies(self, dependency_dispatcher):
        pass

    def perform(self):
        if self.has_action:
            log(f"Performing step: {self.name}")
            with LogIndent():
                self._perform_impl()

    def _perform_impl(self):
        raise NotImplementedError()
