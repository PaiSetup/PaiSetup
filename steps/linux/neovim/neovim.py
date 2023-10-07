from steps.step import Step
from pathlib import Path


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

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "vim",  # TODO do we need this?
            "neovim",
        )
        dependency_dispatcher.register_homedir_file(self._vim_dir_path)

    def perform(self):
        self._symlink_config_files()
        self._remove_legacy_config_files()

    def _symlink_config_files(self):
        self._file_writer.write_symlink(self._nvim_dir_physical_path, self._nvim_dir_path)

    def _remove_legacy_config_files(self):
        legacy_vimrc = self._env.home() / ".vimrc"
        legacy_vimrc.unlink(missing_ok=True)




"""
    def perform(self):
        # Move .vimrc and .viminfo to ~/.config/vim. There might be more to it when installing extensions, but I don't care now.
        # If anything changes, this seems like a good start: https://vi.stackexchange.com/a/20067
        self._file_writer.write_section(
            ".profile",
            "Move vimrc to .config directory",
            [f'export VIMINIT="source ~/.config/vim/vimrc"'],
        )
        self._file_writer.write_section(
            ".config/vim/vimrc",
            "Move viminfo to ~/.config/vim",
            ["set viminfo+=n~/.config/vim/viminfo"],
            file_type=FileType.Vimrc,
        )

    def register_env_variables(self):
        self._env.set("VIMINIT", "source ~/.vim/vimrc")

"""