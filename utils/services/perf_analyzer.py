from pathlib import Path

from utils.command import *
from utils.os_function import OperatingSystem


class PerfAnalyzer:
    class Operation:
        def __init__(self, description, indent_level):
            self.description = str(description)
            self.indent_level = indent_level
            self.duration_ms = None
            self.suboperations = []

    def __init__(self, pai_setup_root, enable):
        self._pai_setup_root = pai_setup_root
        self._enable = enable
        self._pending_operation = None
        self._root_operation = PerfAnalyzer.Operation("root", 0)
        self._root_operation.duration_ms = 0
        self._operation_stack = [self._root_operation] + [None] * 8  # Arbitrary number, can be expanded if neccessary
        self._max_indent_level = 0

    def notify_log(self, message, delta_time_ms, indent_level):
        if not self._enable:
            return

        # Last time we called notify_log we kept pending_operation, because we still needed its duration.
        # Now we have it, so information about the operation is complete and we can add it to our database.
        if self._pending_operation is not None:
            self._pending_operation.duration_ms = delta_time_ms
            self._append_operation(self._pending_operation)

        # We increase indent level artificially, because to simplify code we use a "root operation" which is
        # at indent level 0.
        indent_level += 1

        # We know some things about this operation, but we still don't know its duration, because at this point
        # it is just starting. We'll get to know the duration, when next operation starts.
        self._pending_operation = PerfAnalyzer.Operation(message, indent_level)

    def _append_operation(self, operation):
        # Find a parent of our new operation and add it to its children
        parent = self._operation_stack[operation.indent_level - 1]
        parent.suboperations.append(operation)

        # Update operation stack - our new operation occupies its own level and all levels above are cleared
        self._operation_stack[operation.indent_level] = operation
        for i in range(operation.indent_level + 1, len(self._operation_stack)):
            self._operation_stack[i] = None

        # Track max indent level for svg creation
        self._max_indent_level = max(self._max_indent_level, operation.indent_level)

    def finalize(self):
        if not self._enable:
            return

        lines = []

        def process_operation(stack, operation):
            current_stack = stack + [operation.description]
            line = f"{';'.join(current_stack)} {operation.duration_ms}"
            lines.append(line)
            for subop in operation.suboperations:
                process_operation(current_stack, subop)

        for op in self._root_operation.suboperations:
            process_operation([], op)

        lines = "\n".join(lines)
        with open(self._pai_setup_root / "flamegraph.svg", "w") as file:
            if OperatingSystem.current().is_windows():
                return  # TODO it started crashing with some perl errors
                # flamegraph_command = "flamegraph.pl.exe"
            else:
                flamegraph_command = "flamegraph.pl"
            run_command(flamegraph_command, shell=True, stdin=Stdin.string(lines), stdout=Stdout.print_to_file(file))
            print("Flamegraph written to", Path(file.name).resolve())
