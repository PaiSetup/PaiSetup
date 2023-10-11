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
    def __init__(self, log_dir):
        self._indent_level = 0
        self._indent = ""
        self._last_log_time = None

        self._warnings = []
        self._log_dir = log_dir

        for file in log_dir.iterdir():
            if file.suffix == ".log":
                file.unlink()

    def _get_log_delta_time(self):
        width = 13

        log_time = time.time()
        if self._last_log_time is None:
            content = " " * width
        else:
            time_ms = (log_time - self._last_log_time) * 1000
            content = f"+{time_ms:.2f}ms".rjust(width)

        self._last_log_time = log_time

        return f"[{content}] "

    def log(self, message, add_indent=False):
        log_time = self._get_log_delta_time()

        indent_increase = 1 if add_indent else 0
        with LogIndent(self, indent_increase=indent_increase):
            print(f"{log_time}{self._indent}{message}")

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
        log_file_path = (self._log_dir / report_name).with_suffix(".log")
        self.push_warning(f"{text} See logs at {log_file_path}", print=print)

        if log_file_path.exists():
            # Generate a self-warning and ignore. We will overwrite the old log.
            self.push_warning(f"Multiple warning reports written to {log_file_path}")

        with open(log_file_path, "w") as log_file:
            log_file.write(report_content)

    def finalize(self):
        self.log("END")
        print()
        for text in self._warnings:
            print(f"WARNING: {text}")
