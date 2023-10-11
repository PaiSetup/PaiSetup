from steps.step import Step
import json
import os
from utils.services.file_writer import FileType
from pathlib import Path
import utils.external_project as ext


class ImmediateCharonCall:
    def __init__(self, config_name, name, counter_start, dst_name, dst_dir, dst_backup_dir, use_for_images):
        self.config_path = f".config/charon/{config_name}"
        self.name = name
        self.counter_start = counter_start
        self.dst_dir = dst_dir
        self.dst_name = dst_name
        self.dst_backup_dir = dst_backup_dir
        self.use_for_images = use_for_images


class CharonStep(Step):
    def __init__(self, root_build_dir, fetch_git):
        super().__init__("Charon")
        self.charon_dir = root_build_dir / "charon"
        self.fetch_git = fetch_git
        self._log_file_path = self._env.home() / ".log/charon"

        funny_normal_path = self._env.home() / "multimedia/funny"
        funny_backup_path = Path(f"/run/media/{self._env.get('USER')}/External/Backup/multimedia/Funny")

        self._immediate_charon_calls = [
            ImmediateCharonCall(
                config_name="immediate_internet.json",
                name="Transfer to Funny/Internet",
                dst_name="####",
                counter_start=1,
                dst_dir=funny_normal_path / "Internet",
                dst_backup_dir=funny_backup_path / "Internet",
                use_for_images=True,
            ),
            ImmediateCharonCall(
                config_name="immediate_life.json",
                name="Transfer to Funny/Life",
                dst_name="###",
                counter_start=1,
                dst_dir=funny_normal_path / "Life",
                dst_backup_dir=funny_backup_path / "Life",
                use_for_images=True,
            ),
        ]

    def express_dependencies(self, dependency_dispatcher):
        for call in self._immediate_charon_calls:
            action = {
                "name": call.name,
                "command": f"Charon --config {self._file_writer.resolve_path(call.config_path)} --log {self._log_file_path} --immediate --immediate-files %F",
            }
            if call.use_for_images:
                action["image-files"] = None
            dependency_dispatcher.add_thunar_custom_action(action)

    def perform(self):
        self._compile_charon()
        self._generate_charon_configs()

    def _compile_charon(self):
        self._logger.log("Compiling Charon")
        ext.download(
            "https://github.com/DziubanMaciej/Charon.git",
            "583047b",
            self.charon_dir,
            logger=self._logger,
            has_submodules=True,
            fetch=self.fetch_git,
        )
        ext.cmake(self.charon_dir, cmake_args="-DCMAKE_BUILD_TYPE=Release -DCHARON_TESTS=OFF", logger=self._logger)
        ext.make(self.charon_dir / "build", logger=self._logger)

    def _generate_charon_configs(self):
        for call in self._immediate_charon_calls:
            config = [
                {
                    "type": "copy",
                    "destinationDir": str(call.dst_dir),
                    "destinationName": str(call.dst_name),
                    "counterStart": call.counter_start,
                },
                {
                    "type": "move",
                    "destinationDir": str(call.dst_backup_dir),
                    "destinationName": "${previousName}",
                },
            ]
            config = json.dumps(config, indent=4)
            config = [config]
            self._file_writer.write_lines(call.config_path, config, file_type=FileType.Json)
