import os
import tempfile
from enum import Enum
from pathlib import Path

from utils.command import *
from utils.os_function import OperatingSystem


class FileType(Enum):
    PosixShell = 1
    XResources = 2
    Bash = 3
    Json = 4
    ConfigFile = 5
    ConfigFileNoComments = 6
    Lua = 7
    Css = 8
    Javascript = 9
    Xml = 10
    Python = 11
    Vimrc = 12

    _properties = {
        # fmt: off
        PosixShell:           ("#",    "",    "#!/usr/bin/sh",    True),
        XResources:           ("!",    "",    None,               False),
        Bash:                 ("#",    "",    "#!/usr/bin/bash",  False),
        Json:                 (None,   "",    None,               False),
        ConfigFile:           ("#",    "",    None,               False),
        ConfigFileNoComments: (None,   "",    None,               False),
        Lua:                  ("--",   "",    None,               False),
        Css:                  ("/*",   " */", None,               False),
        Javascript:           ("//",   "",    None,               False),
        Xml:                  ("<!--", "-->", None,               False),
        Python:               ("#",    "",    "#!/bin/python",    False),
        Vimrc:                ('"',    "",    None,               False),
        # fmt: on
    }

    @classmethod
    def _get_properties(cls, file_type):
        return cls._properties.value[file_type.value]

    @classmethod
    def get_comment_prefix(cls, file_type):
        return cls._get_properties(file_type)[0]

    @classmethod
    def get_comment_suffix(cls, file_type):
        return cls._get_properties(file_type)[1]

    @classmethod
    def get_shebang(cls, file_type):
        return cls._get_properties(file_type)[2]

    @classmethod
    def is_executable(cls, file_type):
        return cls._get_properties(file_type)[3]


class InvalidFileTypeUsageException(Exception):
    pass


class ChangedFileTypeException(Exception):
    pass


class ParseFailureException(Exception):
    pass


class LinePlacement(Enum):
    Preamble = 0
    Env = 1
    Begin = 2
    Normal = 3
    End = 4


class FileDesc:
    def __init__(self, path, file_type):
        self.path = path
        self.file_type = file_type
        self.lines = {placement: [] for placement in LinePlacement}


class FileWriter:
    def __init__(self, home_path):
        self._files = dict()
        self._home_path = home_path

    def resolve_path(self, path):
        path = Path(path)
        if path.is_absolute():
            return path
        else:
            return self._home_path / path

    def _ensure_directory(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    def _recreate_file(self, file_desc):
        # Remove file
        self.remove_file(file_desc.path)

        # Create file
        try:
            with open(file_desc.path, "w"):
                pass
        except PermissionError:
            run_command(f"sudo touch {file_desc.path}")

        # Setup permissions
        if OperatingSystem.current().is_linux() and FileType.is_executable(file_desc.file_type):
            run_command(f"sudo chmod +x {file_desc.path}")

    def _flush_lines_to_file(self, file_desc, truncate=False):
        # Prepare lines to be written as a single long string.
        lines = list(file_desc.lines.values())
        lines = sum(lines, [])
        lines = "\n".join(lines + [""])
        if not lines.strip():
            return

        # Clear saved lines, so they won't be written multiple times.
        file_desc.lines = {placement: [] for placement in LinePlacement}

        # Write lines with syscalls if we have permissions. Otherwise, use sudo subprocess.
        try:
            mode = "w" if truncate else "a"
            with open(file_desc.path, mode) as file:
                file.writelines(lines)
        except PermissionError:
            # TODO: This fails for bash scripts containing quotes or "$1". Write to a temp file and use 'install' instead.
            append_arg = "" if truncate else "--append"
            run_command(f'echo "{lines}" | sudo tee {append_arg} {file_desc.path} >/dev/null', shell=True)

    def finalize(self):
        for file_desc in self._files.values():
            self._flush_lines_to_file(file_desc)

    def write_lines(
        self,
        path,
        lines,
        *,
        file_type=FileType.PosixShell,
        line_placement=LinePlacement.Normal,
        flush=False,
        skip_recreate=False,
    ):
        path = self.resolve_path(path)

        # Get description of the file. If we haven't seen this files yet,
        # perform some additional initialization.
        if path in self._files:
            file_desc = self._files[path]
        else:
            file_desc = FileDesc(path, file_type)
            self._files[path] = file_desc
            if skip_recreate:
                # If we skip recreating the file, it will still contain its previous contents.
                # We have to write the lines immediately and use truncate mode, not append.
                flush = True
            else:
                self._ensure_directory(path)
                self._recreate_file(file_desc)
            self._write_preamble(file_desc)

        # Validate if file type changed
        if file_type != file_desc.file_type:
            raise ChangedFileTypeException()

        # Record the lines to the file description. It will be written to
        # the actual file in finalize().
        file_desc.lines[line_placement] += lines

        # Flush (write immediately) if requested
        if flush:
            self._flush_lines_to_file(file_desc, truncate=skip_recreate)

        # Return resolved path
        return path

    def _write_preamble(self, file_desc):
        prefix = FileType.get_comment_prefix(file_desc.file_type)
        suffix = FileType.get_comment_suffix(file_desc.file_type)

        # If there's no comment prefix, it means the file type doesn't support
        # comments, so we have to skip the preamble
        if not prefix:
            return

        lines = []

        # Add shebang
        shebang = FileType.get_shebang(file_desc.file_type)
        if shebang:
            lines.append(shebang)
            lines.append(prefix)

        # Add initial warning comment
        lines += [
            f"{prefix} This file has been autogenerated by PaiSetup.{suffix}",
            f"{prefix} Do not change it manually{suffix}",
            f"{prefix}{suffix}",
            f"",
        ]

        # Record the lines to the file descriptor
        file_desc.lines[LinePlacement.Preamble] += lines

    def write_section(self, path, section_comment, lines, *, file_type=FileType.PosixShell, **kwargs):
        prefix = FileType.get_comment_prefix(file_type)
        suffix = FileType.get_comment_suffix(file_type)
        if not prefix:
            raise InvalidFileTypeUsageException(f"Filetype {file_type.name} does not allow comments")

        lines = [f"{prefix} {section_comment}{suffix}"] + lines + [""]
        return self.write_lines(path, lines, file_type=file_type, **kwargs)

    def write_symlink(
        self,
        src,
        link,
        **kwargs,
    ):
        src = self.resolve_path(src)
        link = self.resolve_path(link)

        self._ensure_directory(link)
        self.remove_file(link)

        try:
            os.symlink(src, link)
        except PermissionError:
            run_command(f"sudo ln -s {src} {link}")

    def write_symlink_executable(self, src_path, dst_name):
        link = Path("/usr/local/bin") / dst_name
        self.write_symlink(src_path, link)

    def write_executable_script(self, file_name, lines):
        path = Path("/usr/local/bin") / file_name

        return self.write_lines(path, lines, file_type=FileType.PosixShell)

    def remove_file(self, path):
        path = self.resolve_path(path)
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except PermissionError:
            run_command(f"sudo rm {path}")

    def patch_dot_desktop_file(self, source_name, destination_name, patch_functions, must_exist=True):
        """
        Takes .desktop file from /usr/share/applications, applies patch functions to its
        contents and creates a new file in a user specific folder for .desktop files.

        Each line is matched to a zero or one patch function. Contents of a matched line is
        passed to the patch function, which returns a new value for the current line.

        Parameters:
            source_name - name of file in /usr/share/applications with .deskop suffix
            destination_name - name of file in ~/.local/share/applications with .deskop suffix
            patch_functions - a dictionary
                keys are names of values in .desktop file (e.g. "Exec")
                values are functions taking a section, base name (without square bracket modifiers) and value and returning a new value
        """
        source_file_path = f"/usr/share/applications/{source_name}"
        destination_file_path = self._home_path / ".local/share/applications" / destination_name

        if not must_exist and not Path(source_file_path).is_file():
            return

        lines = []
        with open(source_file_path, "r") as src:
            section = ""
            for untrimmed_line in src:
                line = untrimmed_line.strip()
                modified_line = untrimmed_line[:-1]  # Remove the newline

                if line.startswith("#"):
                    pass
                elif line.startswith("["):
                    section = line[1:-1]
                else:
                    # line is e.g. "Name[de]=Vim"
                    line_name = line.split("=")[0]  # e.g. "Name[de]"
                    line_base_name = line_name.split("[")[0]  # e.g. "Name"
                    line_value = "=".join(line.split("=")[1:])  # e.g. "Vim"

                    if line_base_name in patch_functions:
                        patch_function = patch_functions[line_base_name]
                        modified_line_value = patch_function(section, line_name, line_value)
                        modified_line = f"{line_name}={modified_line_value}"

                lines.append(modified_line)
        self.write_lines(destination_file_path, lines, file_type=FileType.ConfigFile)

    def patch_ini_file(self, file_path, patch_functions, must_exist=True):
        """
        Parses an .ini file, applies patch functions to its contents and saves it back to disc.

        Each line is matched to a zero or one patch function. Contents of a matched line is
        passed to the patch function, which returns a new value for the current line. The patch
        function is matched by section name and key name.

        Parameters:
            file_path - patch to the .ini file
            patch_functions - a dictionary
                keys are tuples of section name and key name used for matching the patch function, e.g. ("GraphicsSettings", "Resolution")
                values are functions taking a current value and returning a new value
        """

        file_path = self.resolve_path(file_path)

        if not must_exist and not Path(file_path).is_file():
            return

        with open(file_path, "r") as real_file:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, prefix=f"{file_path}.tmp_") as tmp_file:
                section = ""
                for line in real_file:
                    line = line[:-1]  # Remove the newline
                    line_content, line_comment = FileWriter._split_comment(line)

                    # Find out type of current line
                    if not line_content:  # Empty line
                        pass
                    elif line_content.startswith("[") and line_content.endswith("]"):  # Section line
                        section = line_content[1:-1]
                    elif assignement := FileWriter._split_assignment(line_content):  # Key-value, pair line
                        key, assignement, value = assignement

                        # Apply a patch function if it matches
                        try:
                            patch_function = patch_functions[(section, key)]
                            value = patch_function(value)
                            line_content = f"{key}{assignement}{value}"
                        except KeyError:
                            pass
                    else:
                        raise ParseFailureException("Unknown line type")

                    tmp_file.write(f"{line_content}{line_comment}\n")

        os.rename(tmp_file.name, str(file_path))

    @staticmethod
    def _split_comment(line, comment_signs=["#"]):
        comment_start = [line.find(comment_sign) for comment_sign in comment_signs]
        comment_start = min(comment_start)
        if comment_start == -1:
            return (line, "")

        while comment_start > 0 and line[comment_start - 1] == " ":
            comment_start -= 1

        return (
            line[:comment_start],
            line[comment_start:],
        )

    @staticmethod
    def _split_assignment(line):
        assignment_sign_start = line.find("=")
        assignment_sign_end = assignment_sign_start
        if assignment_sign_start == -1:
            return None

        while assignment_sign_start > 0 and line[assignment_sign_start - 1] == " ":
            assignment_sign_start -= 1
        while assignment_sign_end < len(line) - 2 and line[assignment_sign_end + 1] == " ":
            assignment_sign_end += 1

        key = line[:assignment_sign_start]
        assignement = line[assignment_sign_start : assignment_sign_end + 1]
        value = line[assignment_sign_end + 1 :]

        return key, assignement, value
