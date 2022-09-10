import os
from pathlib import Path

 # TODO move this into FileWriter

def patch_dot_desktop_file(source_name, destination_name, patch_functions):
    """
    Takes .desktop file from /usr/share/applications, applies patch functions to its
    contents and creates a new file in a user specific folder for .desktop files.

    Each line is matched to a zero or one patch function. Contents of a matched line is
    pass to the patch function, which returns a new value for the current line.

    Parameters:
        source_name - name of file in /usr/share/applications with .deskop suffix
        destination_name - name of file in ~/.local/share/applications with .deskop suffix
        patch_functions - a dictionary
            keys are names of values in .desktop file (e.g. "Exec")
            values are functions taking a section, base name (without square bracket modifiers) and value and returning a new value
    """
    source_file_path = f"/usr/share/applications/{source_name}"
    destination_file_path = f"{os.environ['HOME']}/.local/share/applications/{destination_name}"

    with open(source_file_path, "r") as src:
        Path(destination_file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(destination_file_path, "w") as dst:
            section = ''
            for untrimmed_line in src:
                line = untrimmed_line.strip()
                if line.startswith("#"):
                    dst.write(untrimmed_line)
                    continue
                if line.startswith("["):
                    section = line[1:-1]
                    dst.write(untrimmed_line)
                    continue

                # line is e.g. "Name[de]=Vim"
                line_name = line.split("=")[0]  # e.g. "Name[de]"
                line_base_name = line_name.split("[")[0]  # e.g. "Name"
                line_value = "=".join(line.split("=")[1:])  # e.g. "Vim"

                try:
                    patch_function = patch_functions[line_base_name]
                except KeyError:
                    dst.write(untrimmed_line)
                    continue

                modified_line_value = patch_function(section, line_name, line_value)
                modified_line = f"{line_name}={modified_line_value}\n"
                dst.write(modified_line)
