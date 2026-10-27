import os
import shutil
from pathlib import Path

from steps.step import Step
from utils import external_project as ext
from utils.services.paths import KnownPath


class FontStep(Step):
    def __init__(self):
        super().__init__("IconFont")
        self._download_path = self._paths.get(KnownPath.BuildDir) / "icon_font"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "ttf-joypixels",
            "otf-font-awesome",
            "consolas-font",
        )

    def perform(self):
        self._logger.log("Downloading PaiSetup's icon font")
        ext.download_github_zip("PaiSetup", "IconFont", self._download_path, re_download=self._flags.strict_download)

        dst_font_dir = self._paths.get(KnownPath.DataHome) / "fonts"
        self._logger.log(f"Installing the font to {dst_font_dir}")
        dst_font_dir.mkdir(parents=True, exist_ok=True)

        src_font_file = self._download_path / "pai_setup_icon_font.ttf"
        dst_font_file = dst_font_dir / src_font_file.name
        shutil.copy(src_font_file, dst_font_file)
