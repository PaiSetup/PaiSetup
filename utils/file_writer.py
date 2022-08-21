from steps.step import Step
from utils import command
import os
from utils.log import log
from enum import Enum
from pathlib import Path


class FileType(Enum):
    PosixShell = 1
    XResources = 2
    Bash = 3
    Json = 4
    ConfigFile = 5
    Lua = 6

    _properties = {
        PosixShell: ("#", "#!/usr/bin/sh", True),
        XResources: ("!", None, False),
        Bash: ("#", "#!/usr/bin/bash", False),
        Json: (None, None, False),
        ConfigFile: ("#", None, False),
        Lua: ("--", None, False),
    }

    @classmethod
    def _get_properties(cls, file_type):
        return cls._properties.value[file_type.value]

    @classmethod
    def get_comment_prefix(cls, file_type):
        return cls._get_properties(file_type)[0]

    @classmethod
    def get_shebang(cls, file_type):
        return cls._get_properties(file_type)[1]

    @classmethod
    def is_executable(cls, file_type):
        return cls._get_properties(file_type)[2]


class InvalidFileTypeUsageException(Exception):
    pass


class ChangedFileTypeException(Exception):
    pass


class LinePlacement(Enum):
    Normal = 1
    End = 2


class FileDesc:
    def __init__(self, path, file_type):
        self.path = path
        self.preamble_written = False
        self.file_type = file_type
        self.end_lines = []


class FileWriter(Step):
    def __init__(self):
        self._files = dict()

    def _resolve_path(self, path, prepend_home_dir):
        if prepend_home_dir:
            return f'{os.environ["HOME"]}/{path}'
        else:
            return path

    def _ensure_file_is_deleted(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    def finalize(self):
        for file_desc in self._files.values():
            if file_desc.end_lines:
                self.write_lines(
                    file_desc.path,
                    file_desc.end_lines,
                    prepend_home_dir=False,
                    file_type=file_desc.file_type,
                    line_placement=LinePlacement.Normal,
                )

            if FileType.is_executable(file_desc.file_type):
                command.run_command(f"sudo chmod +x {file_desc.path}")

    def write_lines(
        self,
        path,
        lines,
        *,
        prepend_home_dir=True,
        file_type=FileType.PosixShell,
        line_placement=LinePlacement.Normal,
    ):
        path = self._resolve_path(path, prepend_home_dir)

        # Get description of the file
        if path in self._files:
            file_desc = self._files[path]
        else:
            file_desc = FileDesc(path, file_type)
            self._files[path] = file_desc

        # Validate if file type changed
        if file_type != file_desc.file_type:
            raise ChangedFileTypeException()

        # Requests with LinePlacement.End will be processed later
        if line_placement == LinePlacement.End:
            file_desc.end_lines += lines
            return

        # If we're seeing this file for the first time
        if not file_desc.preamble_written:
            file_desc.preamble_written = True

            # Ensure directory is created and the file is empty
            self._ensure_file_is_deleted(path)

            # Insert initial comments, if the filetype supports them
            prefix = FileType.get_comment_prefix(file_type)
            if prefix:
                init_lines = []

                # Add shebang
                shebang = FileType.get_shebang(file_type)
                if shebang:
                    init_lines.append(shebang)
                    init_lines.append(prefix)

                # Add initial warning comment
                init_lines += [
                    f"{prefix} This file has been autogenerated by LinuxSetup.",
                    f"{prefix} Do not change it manually",
                    f"{prefix}",
                    f"",
                ]

                lines = init_lines + lines

        # Write lines to the end of the file
        with open(path, "a") as file:
            file.writelines("\n".join(lines + [""]))

    def write_section(self, path, section_comment, lines, *, file_type=FileType.PosixShell, **kwargs):
        prefix = FileType.get_comment_prefix(file_type)
        if not prefix:
            raise InvalidFileTypeUsageException(f"Filetype {file_type.name} does not allow comments")

        lines = [f"{prefix} {section_comment}"] + lines + [""]
        self.write_lines(path, lines, file_type=file_type, **kwargs)

    def write_symlink(
        self,
        src,
        link,
        *,
        prepend_home_dir_src=True,
        prepend_home_dir_link=True,
        **kwargs,
    ):
        src = self._resolve_path(src, prepend_home_dir_src)
        link = self._resolve_path(link, prepend_home_dir_link)
        self._ensure_file_is_deleted(link)
        os.symlink(src, link)
