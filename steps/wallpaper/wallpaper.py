from steps.step import Step
from utils import command
import os
from pathlib import Path
from utils.log import log
import itertools
import random


class WallpaperStep(Step):
    def __init__(self):
        super().__init__("wallpaper")

    def _perform_impl(self):
        linux_setup_wallpapers_path = Path(__file__).parent
        wallpapers_path = Path(f"{os.environ['HOME']}") / "Wallpapers"
        active_wallpaper_path = wallpapers_path / "active"

        if active_wallpaper_path.is_file():
            log(f"File {active_wallpaper_path} already exists. Skipping")
        else:
            log(f"Copying example wallpapers to {wallpapers_path}")
            command.run_command(f"mkdir {wallpapers_path} -p")
            command.run_command(f"cp {linux_setup_wallpapers_path}/*.jpg {wallpapers_path}", run_in_sh=True)
            command.run_command(f"cp {linux_setup_wallpapers_path}/*.png {wallpapers_path}", run_in_sh=True)

            paths = list(itertools.chain(wallpapers_path.glob("*.jpg"), wallpapers_path.glob("*.png")))
            path = random.choice(paths)
            log(f"Creating symlink {active_wallpaper_path} -> {path}")
            active_wallpaper_path.symlink_to(path)
