import utils

class Logger:
    def __init__(self, log_dir):
        self._warnings = []
        self._log_dir = log_dir

        for file in log_dir.iterdir():
            if file.suffix == ".log":
                file.unlink()

    def push_warning(self, text, *, print=True):
        self._warnings.append(text)
        if print:
            utils.log.log(f"WARNING: {text}")

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
        print()
        for text in self._warnings:
            print(f"WARNING: {text}")
