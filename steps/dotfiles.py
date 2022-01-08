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

    _properties = {
        PosixShell: ("#", "#!/usr/bin/sh"),
        XResources: ("!", None),
        Bash: ("#", "#!/usr/bin/bash"),
        Json: (None, None),
        ConfigFile: ("#", None),
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


class InvalidFileTypeUsageException(Exception):
    pass


class LinePlacement(Enum):
    Normal = 1
    End = 2


class DotFilesStep(Step):
    def __init__(self, root_dir):
        super().__init__("Dotfiles")
        self.root_dir = root_dir
        self.files_map = dict()
        self.symlinks = []

    def register_as_dependency_listener(self, dependency_dispatcher):
        dependency_dispatcher.register_listener(self.add_dotfile_lines)
        dependency_dispatcher.register_listener(self.add_dotfile_section)
        dependency_dispatcher.register_listener(self.add_dotfile_symlink)

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_lines(
            ".config/bpython/config",
            [
                "[general]",
                "arg_spec = False",
            ],
            file_type=FileType.ConfigFile,
        )

        dependency_dispatcher.add_dotfile_section(
            ".profile",
            "Some constants",
            [
                f"export LINUX_SETUP_ROOT={self.root_dir}",
                "export EDITOR=vim",
                "export BROWSER=firefox",
                "export FILE_MANAGER=thunar",
            ],
        )
        dependency_dispatcher.add_dotfile_section(
            ".profile",
            "Allow attaching debugger to a running process",
            [
                "echo 0 | sudo tee '/proc/sys/kernel/yama/ptrace_scope' > /dev/null",
            ],
        )
        dependency_dispatcher.add_dotfile_section(
            ".profile",
            "ls aliases",
            [
                "alias ls='ls --color=auto'",
                "alias ll='ls -la'",
                "alias xo='xdg-open'",
            ],
        )
        dependency_dispatcher.add_dotfile_section(
            ".profile",
            "Move .lesshist file into .config",
            [
                "export LESSHISTFILE=~/.config/lesshst",
            ],
        )

        dependency_dispatcher.add_dotfile_lines(
            ".config/pulse/client.conf",
            [
                "autospawn = no",
                "cookie-file = /tmp/pulse-cookie",
            ],
        )

        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Start in home directory",
            ["cd || exit"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Automounting daemon",
            ["udiskie &"],
        )

        dependency_dispatcher.add_dotfile_section(
            ".bash_profile",
            "Call .bashrc, if it exists",
            ["[ -f ~/.bashrc ] && . ~/.bashrc"],
            file_type=FileType.Bash,
            line_placement=LinePlacement.End,
        )
        dependency_dispatcher.add_dotfile_section(
            ".bashrc",
            "Infinite history",
            [
                "export HISTFILESIZE=-1",
                "export HISTSIZE=-1",
            ],
            file_type=FileType.Bash,
        )
        dependency_dispatcher.add_dotfile_section(
            ".bashrc",
            "Call .profile",
            [
                "source ~/.profile",
            ],
            file_type=FileType.Bash,
            line_placement=LinePlacement.End,
        )
        dependency_dispatcher.add_dotfile_section(
            ".profile",
            "Automatically startup GUI only on tty1",
            [
                '[ -z "$DISPLAY" ] && [ "$(tty)" = /dev/tty1 ] && startx',
            ],
            line_placement=LinePlacement.End,
        )

    def _perform_impl(self):
        for dotfile, line_groups in self.files_map.items():
            Path(dotfile).parent.mkdir(parents=True, exist_ok=True)
            with open(dotfile, "w") as file:
                lines_count = 0
                for lines in line_groups.values():
                    file.writelines((f"{x}\n" for x in lines))
                    lines_count += len(lines)
            log(f"Setting up {dotfile} with {lines_count} lines")

        for src, link in self.symlinks:
            log(f"Creating symlink {link} -> {src}")
            try:
                os.remove(link)
            except FileNotFoundError:
                pass
            Path(link).parent.mkdir(parents=True, exist_ok=True)
            os.symlink(src, link)

    def add_dotfile_lines(
        self,
        dotfile,
        lines,
        *,
        prepend_home_dir=True,
        file_type=FileType.PosixShell,
        line_placement=LinePlacement.Normal,
    ):
        if prepend_home_dir:
            dotfile = f'{os.environ["HOME"]}/{dotfile}'

        if dotfile not in self.files_map:
            init_lines = []

            # Insert initial comments, if the filetype supports them
            prefix = FileType.get_comment_prefix(file_type)
            if prefix:
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
            self.files_map[dotfile] = {
                LinePlacement.Normal: init_lines,
                LinePlacement.End: [],
            }
        self.files_map[dotfile][line_placement] += lines

    def add_dotfile_section(self, dotfile, section_comment, lines, *, file_type=FileType.PosixShell, **kwargs):
        prefix = FileType.get_comment_prefix(file_type)
        if not prefix:
            raise InvalidFileTypeUsageException(f"Filetype {file_type.name} does not allow comments")

        lines = [f"{prefix} {section_comment}"] + lines + [""]
        self.add_dotfile_lines(dotfile, lines, file_type=file_type, **kwargs)

    def add_dotfile_symlink(self, src, link, *, prepend_home_dir_src=True, prepend_home_dir_link=True):
        if prepend_home_dir_src:
            src = f'{os.environ["HOME"]}/{src}'
        if prepend_home_dir_link:
            link = f'{os.environ["HOME"]}/{link}'
        self.symlinks.append((src, link))
