from contextlib import nullcontext
import time

indent_level = 0
indent = ""
last_log_time = None


def update_indent(new_indent_level):
    global indent
    global indent_level
    indent_level = new_indent_level
    indent = "    " * indent_level


class LogIndent:
    def __init__(self, message=None):
        self._message = message

    def __enter__(self):
        if self._message is not None:
            log(self._message)
        update_indent(indent_level + 1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        update_indent(indent_level - 1)


def _get_log_delta_time():
    global last_log_time
    width = 13

    log_time = time.time()
    if last_log_time is None:
        content = " " * width
    else:
        time_ms = (log_time - last_log_time) * 1000
        content = f"+{time_ms:.2f}ms".rjust(width)

    last_log_time = log_time

    return "[" + content + "] "


def log(message, add_indent=False):
    log_time = _get_log_delta_time()

    with LogIndent() if add_indent else nullcontext():
        print(f"{log_time}{indent}{message}")
