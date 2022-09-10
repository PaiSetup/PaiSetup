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
        pass

    def is_method_overriden(self, method):
        method_name = method.__name__
        self_dict = self.__class__.__dict__
        class_dict = Step.__dict__
        return method_name in self_dict and self_dict[method_name] != class_dict[method_name]
