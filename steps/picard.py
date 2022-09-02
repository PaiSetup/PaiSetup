from steps.step import Step
import json
import os
from steps.dotfiles import FileType
import utils.external_project as ext


class PicardStep(Step):
    def __init__(self):
        super().__init__("Picard")

    def express_dependencies(self, dependency_dispatcher):
        config_file_path = f"{os.environ['HOME']}/.config/MusicBrainz/Picard.ini"
        config = self._get_picard_config()

        dependency_dispatcher.add_dotfile_lines(
            config_file_path,
            [config],
            file_type=FileType.Json,
            prepend_home_dir=False,
        )
        dependency_dispatcher.add_packages("picard")

    def _get_picard_config(self):
        return r"""
[profiles]
user_profile_settings=@Variant(\0\0\0\b\0\0\0\0)

[setting]
file_renaming_scripts=@Variant(\0\0\0\b\0\0\0\x1\0\0\0H\0\x66\0\x61\0\x30\0\x37\0\x39\0\x35\0\x61\0\x37\0-\0\x61\0\x63\0\x39\0\x38\0-\0\x34\0\x36\0\x62\0\x65\0-\0\x38\0\x36\0\x35\0\x30\0-\0\x34\0\x33\0\x33\0\x63\0\x31\0\x63\0\x37\0\x36\0\x62\0\x64\0\x37\0\x65\0\0\0\b\0\0\0\v\0\0\0\xe\0v\0\x65\0r\0s\0i\0o\0n\0\0\0\n\0\0\0\0\0\0\0\n\0t\0i\0t\0l\0\x65\0\0\0\n\0\0\0\x1c\0\x41\0r\0t\0i\0s\0t\0 \0-\0 \0T\0i\0t\0l\0\x65\0\0\0.\0s\0\x63\0r\0i\0p\0t\0_\0l\0\x61\0n\0g\0u\0\x61\0g\0\x65\0_\0v\0\x65\0r\0s\0i\0o\0n\0\0\0\n\0\0\0\x6\0\x31\0.\0\x31\0\0\0\f\0s\0\x63\0r\0i\0p\0t\0\0\0\n\0\0\0$\0%\0\x61\0r\0t\0i\0s\0t\0%\0 \0-\0 \0%\0t\0i\0t\0l\0\x65\0%\0\0\0\x10\0r\0\x65\0\x61\0\x64\0o\0n\0l\0y\0\0\0\x1\0\0\0\0\xe\0l\0i\0\x63\0\x65\0n\0s\0\x65\0\0\0\n\0\0\0\0\0\0\0\x18\0l\0\x61\0s\0t\0_\0u\0p\0\x64\0\x61\0t\0\x65\0\x64\0\0\0\n\0\0\0.\0\x32\0\x30\0\x32\0\x32\0-\0\x30\0\x33\0-\0\x32\0\x36\0 \0\x31\0\x34\0:\0\x34\0\x33\0:\0\x35\0\x33\0 \0U\0T\0\x43\0\0\0\x4\0i\0\x64\0\0\0\n\0\0\0H\0\x66\0\x61\0\x30\0\x37\0\x39\0\x35\0\x61\0\x37\0-\0\x61\0\x63\0\x39\0\x38\0-\0\x34\0\x36\0\x62\0\x65\0-\0\x38\0\x36\0\x35\0\x30\0-\0\x34\0\x33\0\x33\0\x63\0\x31\0\x63\0\x37\0\x36\0\x62\0\x64\0\x37\0\x65\0\0\0\x16\0\x64\0\x65\0s\0\x63\0r\0i\0p\0t\0i\0o\0n\0\0\0\n\0\0\0\0\0\0\0\x12\0\x64\0\x65\0l\0\x65\0t\0\x61\0\x62\0l\0\x65\0\0\0\x1\x1\0\0\0\f\0\x61\0u\0t\0h\0o\0r\0\0\0\n\0\0\0\0)
load_image_behavior=replace
rename_files=true
selected_file_naming_script_id=fa0795a7-ac98-46be-8650-433c1c76bd7e
"""
