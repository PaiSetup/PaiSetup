from utils.os_function import require_windows

require_windows()

from utils.command import *


def set_user_env_variable(name, value):
    run_powershell_command(f'[Environment]::SetEnvironmentVariable("{name}", "{value}", "User")')


def set_machine_env_variable(name, value):
    run_powershell_command(f'[Environment]::SetEnvironmentVariable("{name}", "{value}", "Machine")')


def add_to_path(path, system=False):
    scope = "Machine" if system else "User"
    current_path = run_powershell_command(f'[Environment]::GetEnvironmentVariable("PATH", "{scope}")', stdout=Stdout.return_back()).stdout.strip()
    current_entries = [entry.lower() for entry in current_path.split(";")]
    if path.lower() in current_entries:
        return
    new_path = f"{current_path};{path}"
    run_powershell_command(f'[Environment]::SetEnvironmentVariable("PATH", "{new_path}", "{scope}")')
