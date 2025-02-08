from pathlib import Path

from steps.step import Step
from utils.command import *


class PlexStep(Step):
    """
    Currently we have to setup Plex libraries by hand. It might be possible to do it in script, but for now
    it's left like this. See:
    https://support.plex.tv/articles/201638786-plex-media-server-url-commands/
    https://support.plex.tv/articles/201242707-plex-media-scanner-via-command-line/
    """

    def __init__(self):
        super().__init__("Plex")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("plex-media-server")

    def perform(self):
        plex_home = self._find_plex_home()

        plex_movies_dir = plex_home / "Movies"
        plex_tv_series_dir = plex_home / "TvShows"
        self._create_symlinks_for_libraries(plex_movies_dir, plex_tv_series_dir)

        plex_dirs = f"{plex_movies_dir} {plex_tv_series_dir}"
        self._setup_permissions(plex_dirs)

    def _find_plex_home(self):
        self._logger.log("Discovering Plex home directory")
        result = run_command("sudo su -l plex -s /usr/bin/sh -c '/usr/bin/echo $HOME'", stdout=Stdout.return_back()).stdout
        result = result.strip()
        self._logger.log(f"Plex home is {result}")
        return Path(result)

    def _create_symlinks_for_libraries(self, plex_movies_dir, plex_tv_series_dir):
        self._logger.log("Creating symlinks for Plex libraries")

        movies_dir = self._env.home() / "multimedia" / "movies"  # TODO get this from HomedirStep
        self._file_writer.write_symlink(movies_dir, plex_movies_dir)

        tv_series_dir = self._env.home() / "multimedia" / "tv_series"
        self._file_writer.write_symlink(tv_series_dir, plex_tv_series_dir)

    def _setup_permissions(self, plex_dirs):
        self._logger.log("Setting permissions")

        run_command(f"sudo chown -R plex:plex {plex_dirs}")
        run_command(f"sudo usermod -aG plex {self._env.get('USER')}")
