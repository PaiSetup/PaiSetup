import utils.external_project as ext
from steps.step import Step
from utils.services.file_writer import FileType


class GuildWars2Step(Step):
    def __init__(self, root_build_dir):
        super().__init__("GuildWars2")
        self._root_build_dir = root_build_dir

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("steam")

    def perform(self):
        self._install_burrito()
        self._write_desktop_file()

    def _install_burrito(self):
        burrito_version = "1.1.0"
        dst_dir = self._root_build_dir / f"burrito-{burrito_version}"

        downloaded = ext.download_github_release(
            "AsherGlick",
            "Burrito",
            dst_dir,
            f"burrito-{burrito_version}",
            f"burrito-{burrito_version}.zip",
            re_download=False,
        )
        if downloaded:
            self._file_writer.write_symlink_executable(dst_dir / "burrito.x86_64", "burrito")

    def _write_desktop_file(self):
        path = self._env.home() / ".local/share/applications/gw2.desktop"
        self._file_writer.write_lines(
            path,
            [
                "[Desktop Entry]",
                "Name=Guild Wars 2",
                "Comment=Play this game on Steam",
                "Exec=steam -silent steam://rungameid/1284210",
                "Icon=steam_icon_1284210",
                "Terminal=false",
                "Type=Application",
                "Categories=Game;",
            ],
            file_type=FileType.ConfigFile,
            flush=True,
        )
