from steps.step import Step
import json
import os
from utils.services.file_writer import FileType
import utils.external_project as ext


class CharonStep(Step):
    def __init__(self, root_build_dir, fetch_git):
        super().__init__("Charon")
        self.charon_dir = root_build_dir / "charon"
        self.fetch_git = fetch_git

        self._config_file_path = self._env.home() / ".config/charon/config.json"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.register_periodic_daemon_check("Charon --config", "Charon")

    def perform(self):
        # Compile Charon
        ext.download(
            "https://github.com/DziubanMaciej/Charon.git",
            "b23facc",
            self.charon_dir,
            has_submodules=True,
            fetch=self.fetch_git,
        )
        ext.cmake(self.charon_dir, cmake_args="-DCMAKE_BUILD_TYPE=Release -DCHARON_TESTS=OFF")
        ext.make(self.charon_dir / "build")

        # Generate Charon config and call it in xinitrc_base
        self._generate_charon_config()
        log_file_path = self._env.home() / ".log/charon"
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Run Charon",
            [
                "pkill Charon",
                f'Charon --config "{self._config_file_path}" --log "{log_file_path}" --daemon &',
            ],
        )

    def _generate_charon_config(self):
        watched_dir = self._env.home() / "downloads/funnyportal"
        dst_dir = self._env.home() / "multimedia/funny/Internet"
        backup_dir = f"/run/media/{self._env.get('USER')}/External/Backup/multimedia/Funny/Internet/"
        config = [
            {
                "watchedFolder": str(watched_dir),
                "extensions": ["jpg", "jpeg", "gif", "png"],
                "actions": [
                    {
                        "type": "copy",
                        "destinationDir": str(dst_dir),
                        "destinationName": "####",
                    },
                    {
                        "type": "move",
                        "destinationDir": backup_dir,
                        "destinationName": "${previousName}",
                    },
                ],
            },
            {
                "watchedFolder": str(watched_dir),
                "extensions": ["mp4", "webm"],
                "actions": [
                    {
                        "type": "copy",
                        "destinationDir": str(dst_dir / "Video"),
                        "destinationName": "###",
                    },
                    {
                        "type": "move",
                        "destinationDir": f"{backup_dir}/Video",
                        "destinationName": "${previousName}",
                    },
                ],
            },
        ]
        config = json.dumps(config, indent=4)
        config = [config]

        self._file_writer.write_lines(self._config_file_path, config, file_type=FileType.Json)
