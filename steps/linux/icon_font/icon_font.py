import os
import shutil
from pathlib import Path

from steps.step import Step
from utils import external_project as ext


# TODO rename to FontStep
class IconFontStep(Step):
    def __init__(self, full):
        super().__init__("IconFont")
        self._current_step_dir = Path(__file__).parent
        self._full = full

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "ttf-joypixels",
            "ttf-font-awesome",
            "consolas-font",
        )

    def perform(self):
        self._logger.log("Downloading icon font")
        dst_dir = self._current_step_dir / "icon_font"
        ext.download_github_zip("PaiSetup", "IconFont", dst_dir, self._full)

        dst_font_dir = self._env.home() / ".local/share/fonts"
        dst_font_dir.mkdir(parents=True, exist_ok=True)

        src_font_file = dst_dir / "pai_setup_icon_font.ttf"
        dst_font_file = dst_font_dir / src_font_file.name
        shutil.copy(src_font_file, dst_font_file)
