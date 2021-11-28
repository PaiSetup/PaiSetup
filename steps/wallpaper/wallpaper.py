from steps.step import Step
from utils import command
import os
from pathlib import Path
from utils.log import log
import itertools
import random


class WallpaperStep(Step):
    def __init__(self):
        super().__init__("Wallpaper")

    def _perform_impl(self):
        linux_setup_wallpapers_path = Path(__file__).parent
        wallpapers_path = Path(f"{os.environ['HOME']}") / "Wallpapers"
        arch_wallpaper = wallpapers_path / "arch1.jpg"

        if arch_wallpaper.is_file():
            log(f"File {arch_wallpaper} already exists. Skipping")
        else:
            log(f"Copying example wallpapers to {wallpapers_path}")
            command.run_command(f"mkdir {wallpapers_path} -p")
            command.run_command(f"cp {linux_setup_wallpapers_path}/*.jpg {wallpapers_path}", shell=True)
            command.run_command(f"cp {linux_setup_wallpapers_path}/*.png {wallpapers_path}", shell=True)
