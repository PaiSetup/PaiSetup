indent_level = 0
indent = ""


def update_indent(new_indent_level):
    global indent
    global indent_level
    indent_level = new_indent_level
    indent = "    " * indent_level


class LogIndent:
    def __enter__(self):
        update_indent(indent_level + 1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        update_indent(indent_level - 1)


def log(message):
    print(f"{indent}{message}")
