from pathlib import Path

from steps.step import Step

"""
Neovim configuration
    ~/.vimrc - legacy vim path
    ~/.vim/vimrc - vim path
    ~/.config/nvim/init.lua - main config file
    VIMINIT - can point to vimrc. Do not set it. It should be empty

Plug 'ThePrimeagen/vim-be-good'

Vim options https://vimdoc.sourceforge.net/htmldoc/options.html

Reloading configuration in neovim after change:
    - save the file
    - source %

"""


class NeovimStep(Step):
    def __init__(self):
        super().__init__("neovim")
        self._vim_dir_path = self._env.home() / ".vim"
        self._vimrc_path = self._vim_dir_path / "vimrc"

        self._nvim_dir_physical_path = Path(__file__).parent / "config"
        self._nvim_dir_path = self._env.home() / ".config/nvim"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("neovim")
        dependency_dispatcher.register_homedir_file(self._vim_dir_path)

    def perform(self):
        self._symlink_config_files()
        self._remove_legacy_config_files()
        self._create_terminal_nvim_desktop_file()

    def _symlink_config_files(self):
        self._file_writer.write_symlink(self._nvim_dir_physical_path, self._nvim_dir_path)

    def _remove_legacy_config_files(self):
        legacy_vimrc = self._env.home() / ".vimrc"
        legacy_vimrc.unlink(missing_ok=True)

    def _create_terminal_nvim_desktop_file(self):
        self._file_writer.patch_dot_desktop_file(
            "nvim.desktop",
            "terminal_nvim.desktop",
            {
                "Exec": lambda *args,: "terminal nvim %F",
                "Terminal": lambda *args: "false",
                "Name": lambda *args: "Neovim in new terminal",
            },
        )
