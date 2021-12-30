from steps.step import Step
from utils import command
import os
from pathlib import Path
from steps.dotfiles import FileType


class GitStep(Step):
    def __init__(self):
        super().__init__("Git")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("git")
        dependency_dispatcher.add_dotfile_section(
            ".bashrc",
            "Enable git commands completion",
            [". /usr/share/git/completion/git-completion.bash"],
            file_type=FileType.Bash,
        )

    def _perform_impl(self):
        gitconfig_dir = Path(os.environ["HOME"]) / ".config" / "git"
        gitconfig_path = gitconfig_dir / "config"
        gitconfig_dir.mkdir(parents=True, exist_ok=True)
        gitconfig_path.touch(exist_ok=True)

        command.run_command("git config --global user.name MaciejDziuban")
        command.run_command("git config --global user.email dziuban.maciej@gmail.com")
