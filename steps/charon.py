from steps.step import Step
import json
import os
from steps.dotfiles import FileType


class CharonStep(Step):
    def __init__(self):
        super().__init__("Charon")

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
        pass

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
                        "destinationName": "${name}.${extension}",
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
                        "destinationName": "${name}.${extension}",
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
