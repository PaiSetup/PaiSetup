import time


class LogIndent:
    def __init__(self, logger, indent_increase=1, message=None):
        self._logger = logger
        self._indent_increase = indent_increase
        self._message = message

    def __enter__(self):
        if self._message is not None:
            self._logger.log(self._message)
        self._logger.update_indent(self._logger.get_indent_level() + self._indent_increase)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._logger.update_indent(self._logger.get_indent_level() - self._indent_increase)


class Logger:
    def __init__(self, log_dir, perf_analyzer, enabled):
        self._indent_level = 0
        self._indent = ""
        self._last_log_time = None

        self._warnings = []
        self._log_dir = log_dir
        self._perf_analyzer = perf_analyzer
        self._enabled = enabled

        if self._log_dir is not None:
            for file in self._log_dir.iterdir():
                if file.suffix == ".log":
                    file.unlink()

    def log(self, message, short_message=None, add_indent=False, silent=False):
        # Calculate delta time
        width = 13
        log_time = time.time()
        if self._last_log_time is None:
            delta_time_ms = None
            delta_time_ms_str = " " * width
        else:
            delta_time_ms = (log_time - self._last_log_time) * 1000
            delta_time_ms_str = f"+{delta_time_ms:.2f}ms".rjust(width)

        # Update last log time
        self._last_log_time = log_time

        indent_increase = 1 if add_indent else 0
        if self._enabled and not silent:
            with LogIndent(self, indent_increase=indent_increase):
                print(f"[{delta_time_ms_str}] {self._indent}{message}")

        message_for_perf_analyzer = message
        if short_message is not None:
            message_for_perf_analyzer = short_message
        self._perf_analyzer.notify_log(message_for_perf_analyzer, delta_time_ms, self._indent_level + indent_increase)

    def silent_log(self, *args, **kwargs):
        kwargs["silent"] = True
        self.log(*args, **kwargs)

    def update_indent(self, new_indent_level):
        self._indent_level = new_indent_level
        self._indent = "    " * self._indent_level

    def get_indent_level(self):
        return self._indent_level

    def indent(self, message=None):
        return LogIndent(self, indent_increase=1, message=message)

    def push_warning(self, text, *, print_to_console=True):
        self._warnings.append(text)
        if print_to_console:
            self.log(f"WARNING: {text}")

    def push_warning_with_report(
        self,
        text,
        report_name,
        report_content,
        *,
        print=True,
    ):
        if self._log_dir is None:
            return

        log_file_path = (self._log_dir / report_name).with_suffix(".log")
        self.push_warning(f"{text} See logs at {log_file_path}", print_to_console=print)

        if log_file_path.exists():
            # Generate a self-warning and ignore. We will overwrite the old log.
            self.push_warning(f"Multiple warning reports written to {log_file_path}")

        with open(log_file_path, "w") as log_file:
            log_file.write(report_content)

    def get_log_dir(self):
        return self._log_dir

    def finalize(self):
        self.log("END")
        print()
        for text in self._warnings:
            print(f"WARNING: {text}")
