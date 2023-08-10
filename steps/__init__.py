import platform

current_os = platform.system()
if current_os == "Linux":
    from .linux import get_steps
elif current_os == "Windows":
    from .windows import get_steps
else:
    raise ImportError(f"Unsupported OS: {current_os}")

# TODO enable developer mode to be able to symlink https://stackoverflow.com/questions/44158326/win10-how-to-activate-developer-mode-using-powershell-or-cmd-exe
