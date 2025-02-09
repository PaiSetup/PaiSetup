from steps.step import Step
from utils.dependency_dispatcher import DependencyType, dependency_listener


class Events:
    def __init__(self):
        self._events = []

    def _process(self, s, append):
        if append:
            self._events.append(s)
        return s

    def push_dependencies(self, step_name, append=False):
        s = f"{step_name}.push_dependencies()"
        return self._process(s, append)


    def handler(self, step_name, handler_name, caller_step_name, append=False):
        s = f"{caller_step_name} -> {step_name}.{handler_name}()"
        return self._process(s, append)


events = Events()

class StepA(Step):
    def __init__(self):
        super().__init__("a")

    @dependency_listener
    def call_a(self, caller):
        events.handler("a", "call_a", caller, True)

    def push_dependencies(self, dependency_dispatcher):
        events.push_dependencies("a", True)
        dependency_dispatcher.call_b(self.name)

class StepB(Step):
    def __init__(self):
        super().__init__("b")

    @dependency_listener
    def call_b(self, caller):
        events.handler("b", "call_b", caller, True)

    def push_dependencies(self, dependency_dispatcher):
        events.push_dependencies("b", True)
        dependency_dispatcher.call_c(self.name)

class StepC(Step):
    def __init__(self):
        super().__init__("b")

    @dependency_listener
    def call_c(self, caller):
        events.handler("c", "call_c", caller, True)

    def push_dependencies(self, dependency_dispatcher):
        events.push_dependencies("c", True)
        # dependency_dispatcher.call_c(self.name)


def get_steps(args, root_dir, build_dir, secret_dir):
    events = []
    return [
        StepA(),
        StepB(),
        StepC(),
    ]
