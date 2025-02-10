from steps.step import Step
from utils.dependency_dispatcher import DependencyType, dependency_listener
from utils.execute_steps import execute_steps


class Events:
    def __init__(self):
        self._events = []

    def push_dependencies(self, step_name, append=False):
        s = f"{step_name}.push_dependencies()"
        self._events.append(s)

    def handler(self, step_name, handler_name, caller_step_name, append=False):
        s = f"{caller_step_name} -> {step_name}.{handler_name}()"
        self._events.append(s)

    def __eq__(self, other):
        if len(self._events) != len(other._events):
            return False
        elements_eq = (x == y for x,y in zip(self._events, other._events))
        return all(elements_eq)


class StepA(Step):
    def __init__(self, events):
        super().__init__("a")
        self.events = events

    @dependency_listener
    def call_a(self, caller):
        self.events.handler("a", "call_a", caller)

    def push_dependencies(self, dependency_dispatcher):
        self.events.push_dependencies("a")
        dependency_dispatcher.call_b(self.name)

class StepB(Step):
    def __init__(self, events):
        super().__init__("b")
        self.events = events

    @dependency_listener
    def call_b(self, caller):
        self.events.handler("b", "call_b", caller)

    def push_dependencies(self, dependency_dispatcher):
        self.events.push_dependencies("b")
        dependency_dispatcher.call_c(self.name)

class StepC(Step):
    def __init__(self, events):
        super().__init__("b")
        self.events = events

    @dependency_listener
    def call_c(self, caller):
        self.events.handler("c", "call_c", caller)

    def push_dependencies(self, dependency_dispatcher):
        self.events.push_dependencies("c")
        # dependency_dispatcher.call_c(self.name)


def test_in_order_chain():
    actual_events = Events()
    steps = [
        StepA(actual_events),
        StepB(actual_events),
        StepC(actual_events),
    ]
    execute_steps(steps)

    expected_events = Events()
    expected_events.push_dependencies("a"),
    expected_events.push_dependencies("b"),
    expected_events.push_dependencies("c"),
    expected_events.handler("c", "call_c", "b"),
    expected_events.handler("b", "call_b", "a"),

    if actual_events == expected_events:
        print("PASS")
    else:
        print("FAIL")

def test_reverse_order_chain():
    actual_events = Events()
    steps = [
        StepC(actual_events),
        StepB(actual_events),
        StepA(actual_events),
    ]
    execute_steps(steps)

    expected_events = Events()
    expected_events.push_dependencies("c"),
    expected_events.push_dependencies("b"),
    expected_events.handler("c", "call_c", "b"),
    expected_events.push_dependencies("a"),
    expected_events.handler("b", "call_b", "a"),

    if actual_events == expected_events:
        print("PASS")
    else:
        print("FAIL")