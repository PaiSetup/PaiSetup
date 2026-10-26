---
name: paisetup-step
description: Guidelines for creating or modifying a PaiSetup Step (steps/**). Use whenever adding a new step, changing an existing step's perform()/push_dependencies()/pull_dependencies(), or deciding where a step's paths, files, logs or error handling should go.
---

# Creating PaiSetup steps

Read the project `CLAUDE.md` first for the architecture (setup modes, services, dependency dispatcher,
package steps). This skill covers how to write a step well.

## Skeleton

```python
from steps.step import Step
from utils.command import *
from utils.services.file_writer import FileType
from utils.services.paths import KnownPath


class FooStep(Step):
    def __init__(self):
        super().__init__("Foo")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("foo")
        dependency_dispatcher.set_env("Foo paths", "FOO_HOME", self._paths.get(KnownPath.DataHome) / "foo")

    def perform(self):
        self._enable_service()
        self._generate_config()

    def _enable_service(self):
        ...

    def _generate_config(self):
        ...
```

## Guidelines

### No module-level constants
Don't put `SOME_CONSTANT = 1` at the top of the file or the class. Write the value inline where it's used.

### perform() must be overridden directly - or not at all
`execute_steps()` only calls `perform()` when the concrete step class defines it itself
(`Step.is_method_overriden()` checks only the class's own `__dict__`).
- If the step only pushes/pulls dependencies (e.g. just adds packages), **don't** define `perform()`.
- If the step derives from a base class that implements `perform()` (e.g. `NotesStepBase`,
  `DushStepBase`), it **must** override it, even if it only calls `super().perform()`. Otherwise the base
  implementation is silently skipped.

### Split perform() into logical chunks, with logs
`perform()` should read like a table of contents: a few calls to private methods, each doing one logical
thing (`_enable_service()`, `_configure()`, `_generate_bookmarks()`, ...). Each chunk logs what it's doing.

### Logging
Never `print()`. Use `self._logger`:
- `self._logger.log("Setting up config files in /usr/share/lightdm")` for progress.
- `with self._logger.indent("Making sure existing XDG dirs are ok"):` for nested work, so its logs are
  indented under the parent message. Use it when a chunk logs per-item results (one line per dir,
  package, file).
- `self._logger.push_warning(...)` for problems the user should see in the summary at the end of the run.

### Writing files
Never `open(..., "w")` directly. Use `self._file_writer`:
- `write_lines(path, lines, file_type=...)` - write plain lines.
- `write_section(path, section_comment, lines, file_type=...)` - lines preceded by a comment describing
  them. Cleaner than `write_lines`, but not applicable in every case. Prefer `write_section` where
  possible.
- `write_symlink`, `write_executable_script`, `patch_ini_file`, `patch_dot_desktop_file`, `remove_file`.
Any number of steps can write to the same file; their lines are concatenated. Files are recreated from
scratch on every run (which keeps the step idempotent) and written at the end of the run.

### Environment variables

Linux: When setting environment variables, use `dependency_dispatcher.set_env(section, name, value)` in
`push_dependencies()`.
- It sets the variable in the current process, so `perform()` of other steps (and commands they run) can
  query it with `self._env.get()`. Don't rely on it in other steps' `push_dependencies()`, since the
  order of pushes is undefined.
- It writes the variable to `env.sh` and `environment.d`, so there's no need to write `export` lines.
- Values can't reference other variables (`$`). To extend a list variable like `PATH`, use
  `dependency_dispatcher.append_env(section, name, value)` instead.
- Each variable can be set by only one step.

Windows: use helpers in `utils.windows.env`:
- `set_user_env_variable(name, value)` / `set_machine_env_variable(name, value)` - persist a variable
  for the current user or all users.
- `add_to_path(path, system=False)` - append to the user or machine `PATH`, if not there already.
- They only write to the registry and don't affect the current process. If other steps need the
  variable during this run, also set it with `self._env.set(...)`.


### Paths
Paths are managed by the `Paths` service (`self._paths`) and the `KnownPath` enum
(`utils/services/paths.py`). The rules:
- A path used by **only one step** is **not** a `KnownPath`. The step decides for itself and computes it
  in `__init__()` or `perform()` (e.g. the Notes and Dush directories).
- A path used by **multiple steps** **is** a `KnownPath`. Exactly one step makes the decision and sets it
  with `self._paths.set(...)` in its `__init__()` (`FoldersStep` on Windows, `HomeDirectoryStep` on
  Linux). Home and the PaiSetup root are set automatically.
- Steps may **query** paths only in `push_dependencies()`, `pull_dependencies()` or `perform()` -
  **never in `__init__()`**, because step construction order is undefined. If something computed in
  `__init__()` needs a known path, move that computation to the phase that first needs it.
- `self._paths.get(...)` is required by default and raises if the path is missing. Pass
  `required=False` only for paths that a setup mode or plugin may legitimately not set, and handle
  `None` explicitly.
- Before hardcoding something like `self._paths.home() / "downloads"` or `.local/share`, check whether a
  `KnownPath` already exists for it. If a second step starts needing a path that was private to one step,
  promote it to a `KnownPath`.
- Some `KnownPath` values exist only on Windows or only on Linux; referencing one on the other OS is an
  error by design.

### Idempotency
`setup.py` is run over and over. A step must produce the same result whether it runs for the first or
the tenth time: use `mkdir(parents=True, exist_ok=True)`, check before creating/enabling/renaming, rely
on FileWriter regenerating files, never append to a file on every run, never assume a clean machine.

### Failures: ask the user
Whenever something in the step can fail (a command returns non-zero, a file or directory is missing,
a package isn't installed, a network download fails, unexpected output), **ask the user how to handle
it** before writing the code. Offer the options:
- ignore it silently,
- raise an exception (stop the whole setup),
- `self._logger.push_warning(...)` and continue/return,
- write a workaround,
- handle it differently (fallback value, skip just this item, ...).

### Speed: skip slow commands when possible
Calling OS commands or third-party tools (`systemctl`, package managers, compilers, `gsettings`,
`git` operations, downloads) can be slow, and every run pays for them. When a step calls such a command:
- Tell the user the command may be slow and suggest measuring it on a real run (the logger prints the
  time since the previous log line) to decide whether it's worth making cheaper.
- Suggest a cheap way to check whether the command is needed at all before running it, and skip it if
  not. Example from `LightDmStep._enable_service()`: query `systemctl status display-manager` first and
  only run `sudo systemctl enable lightdm.service` if LightDM isn't already the display manager. Other
  examples: compare current vs desired value before setting it, check if a file/dir/symlink already
  matches, use `ext.should_build(...)` before compiling.
Iterating over a short list or reading a file is not slow - don't optimize those.

### Shelling out
Use `run_command(...)` (or `run_powershell_command(...)` on Windows) from `utils/command.py`, never
`subprocess` directly. It raises `CommandError` on non-zero exit; capture output with
`stdout=Stdout.return_back()`.

### Packages
Request packages with `dependency_dispatcher.add_packages(...)` in `push_dependencies()`; never install
them yourself. Linux steps use Arch package names (the Debian step translates them). On Windows, verify
`PackageInfo` knows how to install every new Chocolatey package, and ask the user about the installer
type and parameters if it doesn't.

### Setup mode
A step does nothing until a setup mode runs it. Import it in `steps/<os>/__init__.py` (or the plugin's
`__init__.py`) and add it to the `get_steps()` list of every mode that should run it. If it's not obvious
which modes those are, ask the user.

### Running the new step
Never run `setup.py` on your own. It changes the real machine. Let the user review the code first, then
offer to run it. If they agree, run plain `./setup.py` with no arguments. Afterwards, go through the
output: report the warnings summary and look at the timings of the new step's log lines. If something
is slow, offer to speed it up as described in "Speed" above.
