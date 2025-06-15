from xml.dom import minidom

from steps.step import Step
from utils.dependency_dispatcher import push_dependency_handler
from utils.services.file_writer import FileType


class ThunarStep(Step):
    def __init__(self):
        super().__init__("Thunar")
        self.disable_suspending_command = ""
        self.actions = []
        self._bookmarks = [
            (self._env.home() / "downloads", "Downloads"),
            (self._env.get("PAI_SETUP_ROOT"), "PaiSetup"),
        ]

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
                "command": f'bash -c "{self._env.get("PAI_SETUP_ROOT")}/steps/linux/gui/scripts/select_wallpaper.py --wallpaper_file %f --restart_wm"',
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

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "thunar",
            "thunar-archive-plugin",
            "thunar-media-tags-plugin",
            "tumbler",  # needed for thumbnails
            "ffmpegthumbnailer",  # needed for video thumbnails
            "file-roller",
        )

    @push_dependency_handler
    def add_thunar_custom_action(self, action):
        self.actions.append(action)

    @push_dependency_handler
    def add_multimedia_directories(self, directories):
        self._bookmarks += directories

    def perform(self):
        self._setup_bookmarks()
        self._generate_uca_xml()

    def _setup_bookmarks(self):
        file_path = self._env.home() / ".config/gtk-3.0/bookmarks"
        self._logger.log(f"Generating bookmarks config - {file_path}")

        line = [f"file://{path} {name}" for path, name in self._bookmarks]
        self._file_writer.write_lines(
            file_path,
            line,
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
