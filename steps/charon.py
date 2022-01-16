from steps.step import Step
import json
import os
from steps.dotfiles import FileType
import utils.external_project as ext


class CharonStep(Step):
    def __init__(self, root_build_dir, fetch_git):
        super().__init__("Charon")
        self.charon_dir = root_build_dir / "charon"
        self.fetch_git = fetch_git

    def express_dependencies(self, dependency_dispatcher):
        config_file_path = f"{os.environ['HOME']}/.config/charon/config.json"
        log_file_path = f"{os.environ['HOME']}/.log/charon"
        config = self._generate_charon_config()

        dependency_dispatcher.add_dotfile_lines(
            config_file_path,
            [config],
            file_type=FileType.Json,
            prepend_home_dir=False,
        )
        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Run Charon",
            [f'Charon --config "{config_file_path}" --log "{log_file_path}" --daemon &'],
        )

    def _perform_impl(self):
        ext.download(
            "git@github.com:DziubanMaciej/Charon.git",
            "1.2",
            self.charon_dir,
            has_submodules=True,
            fetch=self.fetch_git,
        )
        ext.cmake(self.charon_dir, cmake_args="-DCMAKE_BUILD_TYPE=Release -DCHARON_TESTS=OFF")
        ext.make(self.charon_dir / "build")

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
                        "destinationName": "###",
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
        return json.dumps(config, indent=4)
