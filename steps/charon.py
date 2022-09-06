from steps.step import Step
import json
import os
from utils.file_writer import FileType
import utils.external_project as ext


class CharonStep(Step):
    def __init__(self, root_build_dir, fetch_git):
        super().__init__("Charon")
        self.charon_dir = root_build_dir / "charon"
        self.fetch_git = fetch_git

        self._config_file_path = f"{os.environ['HOME']}/.config/charon/config.json"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.register_bgchecher_daemon_check_script("Charon --config", "Charon")

    def _perform_impl(self):
        # Compile Charon
        ext.download(
            "git@github.com:DziubanMaciej/Charon.git",
            "b23facc",
            self.charon_dir,
            has_submodules=True,
            fetch=self.fetch_git,
            chmod_needed=False,
        )
        ext.cmake(self.charon_dir, cmake_args="-DCMAKE_BUILD_TYPE=Release -DCHARON_TESTS=OFF")
        ext.make(self.charon_dir / "build")

        # Generate Charon config and call it in xinitrc_base
        self._generate_charon_config()
        log_file_path = f"{os.environ['HOME']}/.log/charon"
        self._file_writer.write_section(
            ".config/LinuxSetup/xinitrc_base",
            "Run Charon",
            [
                "pkill Charon",
                f'Charon --config "{self._config_file_path}" --log "{log_file_path}" --daemon &',
            ],
        )

    def _generate_charon_config(self):
        watched_dir = f"{os.environ['HOME']}/Downloads/funnyportal"
        dst_dir = f"{os.environ['HOME']}/Multimedia/Funny/Internet"
        backup_dir = f"/run/media/{os.environ['USER']}/External/Backup/Multimedia/Funny/Internet/"
        config = [
            {
                "watchedFolder": watched_dir,
                "extensions": ["jpg", "jpeg", "gif", "png"],
                "actions": [
                    {
                        "type": "copy",
                        "destinationDir": dst_dir,
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
                "watchedFolder": watched_dir,
                "extensions": ["mp4", "webm"],
                "actions": [
                    {
                        "type": "copy",
                        "destinationDir": f"{dst_dir}/Video",
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
