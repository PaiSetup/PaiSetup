from utils.os_function import require_windows

require_windows()

from utils.command import *


def set_user_env_variable(name, value):
    run_powershell_command(f'[Environment]::SetEnvironmentVariable("{name}", "{value}", "User")')


def set_machine_env_variable(name, value):
    run_powershell_command(f'[Environment]::SetEnvironmentVariable("{name}", "{value}", "Machine")')
