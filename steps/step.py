from utils.log import log, LogIndent


class Step:
    def __init__(self, name):
        self.name = name

    def setup_external_services(self, file_writer):
        self._file_writer = file_writer

    def register_as_dependency_listener(self, dependency_dispatcher):
        pass

    def express_dependencies(self, dependency_dispatcher):
        pass

    def perform(self):
        if self._is_method_overriden(Step._perform_impl):
            log(f"Performing step: {self.name}")
            with LogIndent():
                self._perform_impl()

    def _perform_impl(self):
        raise NotImplementedError()

    def _is_method_overriden(self, method):
        method_name = method.__name__
        self_dict = self.__class__.__dict__
        class_dict = Step.__dict__
        return method_name in self_dict and self_dict[method_name] != class_dict[method_name]
