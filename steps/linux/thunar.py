from steps.step import Step, dependency_listener
from utils.services.file_writer import FileType
from xml.dom import minidom


class ThunarStep(Step):
    def __init__(self, is_main_machine):
        super().__init__("Thunar")
        self._is_main_machine = is_main_machine
        self.disable_suspending_command = ""
        self.actions = []

        self.add_thunar_custom_action(
            {
                "name": "Open terminal here",
                "command": "st",
                "directories": None,
            }
        )
        self.add_thunar_custom_action(
            {
                "name": "Set wallpaper and generate colors",
                "command": f'bash -c "{self._env.get("PAI_SETUP_ROOT")}/steps/linux/gui/select_wallpaper.sh  %f 1"',
                "image-files": None,
            }
        )
        self.add_thunar_custom_action(
            {
                "name": "Copy contents to clipboard",
                "command": "cat %f | tr -d '\n' | xclip -selection CLIPBOARD",
                "text-files": None,
            }
        )

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "thunar",
            "thunar-archive-plugin",
            "thunar-media-tags-plugin",
            "tumbler",  # needed for thumbnails
            "ffmpegthumbnailer",  # needed for video thumbnails
        )

    @dependency_listener
    def add_thunar_custom_action(self, action):
        self.actions.append(action)

    def perform(self):
        self._setup_bookmarks()
        self._generate_uca_xml()

    def _setup_bookmarks(self):
        file_path = self._env.home() / ".config/gtk-3.0/bookmarks"
        self._logger.log(f"Generating bookmarks config - {file_path}")

        dirs = [
            (self._env.home() / "downloads", "Downloads"),
            (self._env.get("PAI_SETUP_ROOT"), "PaiSetup"),
        ]
        if self._is_main_machine:
            dirs += [
                (self._env.home() / "multimedia/wallpapers", "Wallpapers"),
                (self._env.home() / "multimedia/funny", "Multimedia/Funny"),
                (self._env.home() / "multimedia/tv_series", "Multimedia/TvSeries"),
            ]
        dirs = [f"file:///{path} {name}" for path, name in dirs]

        self._file_writer.write_lines(
            file_path,
            dirs,
            file_type=FileType.ConfigFileNoComments,
        )

    def _generate_uca_xml(self):
        file_path = self._env.home() / ".config/Thunar/uca.xml"
        self._logger.log(f"Generating custom actions config - {file_path}")

        document = minidom.Document()
        root = document.createElement("actions")
        document.appendChild(root)
        for action in self.actions:
            action_node = document.createElement("action")
            root.appendChild(action_node)
            for property_name, property_value in action.items():
                property_node = document.createElement(property_name)
                action_node.appendChild(property_node)

                if property_value is not None:
                    property_value_node = document.createTextNode(property_value)
                    property_node.appendChild(property_value_node)

        self._file_writer.write_lines(
            file_path,
            [document.toprettyxml(indent="    ")],
            file_type=FileType.Xml,
        )
