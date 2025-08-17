import os
import shutil
from pathlib import Path

from steps.step import Step
from utils import external_project as ext


class FontStep(Step):
    def __init__(self, root_build_dir, full):
        super().__init__("IconFont")
        self._download_path = root_build_dir / "icon_font"
        self._full = full

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "ttf-joypixels",
            "otf-font-awesome",
            "consolas-font",
        )

    def perform(self):
        self._logger.log("Downloading icon font")
        ext.download_github_zip("PaiSetup", "IconFont", self._download_path, re_download=self._full)

        dst_font_dir = self._env.home() / ".local/share/fonts"
        dst_font_dir.mkdir(parents=True, exist_ok=True)

        src_font_file = self._download_path / "pai_setup_icon_font.ttf"
        dst_font_file = dst_font_dir / src_font_file.name
        shutil.copy(src_font_file, dst_font_file)
