from steps.step import Step
from utils.services.file_writer import FileType
from xml.dom import minidom


class ThunarStep(Step):
    def __init__(self, is_main_machine):
        super().__init__("Thunar")
        self._is_main_machine = is_main_machine
        self.disable_suspending_command = ""

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "thunar",
            "thunar-archive-plugin",
            "thunar-media-tags-plugin",
            "tumbler",  # needed for thumbnails
            "ffmpegthumbnailer",  # needed for video thumbnails
        )

    def perform(self):
        self._setup_bookmarks()
        self._file_writer.write_lines(
            ".config/Thunar/uca.xml",
            [self._get_uca_xml_contents()],
            file_type=FileType.Xml,
        )

    def _setup_bookmarks(self):
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
            ".config/gtk-3.0/bookmarks",
            dirs,
            file_type=FileType.ConfigFileNoComments,
        )

    def _get_uca_xml_contents(self):
        pai_setup_root = self._env.get("PAI_SETUP_ROOT")
        image_extensions = ["png", "jpg", "jpeg", "avif"]
        image_extensions = ";".join([f"*.{x}" for x in image_extensions])

        actions = [
            {
                "name": "Open terminal here",
                "command": "st",
                "description": "Example for a custom action",
                "patterns": "*",
                "directories": None,
            },
            {
                "name": "Set wallpaper and generate colors",
                "command": f'bash -c "{pai_setup_root}/steps/linux/gui/select_wallpaper.sh  %f 1"',
                "patterns": image_extensions,
                "image-files": None,
            },
            {
                "name": "Copy contents to clipboard",
                "command": "cat %f | tr -d '\n' | xclip -selection CLIPBOARD",
                "patterns": "*",
                "text-files": None,
            },
        ]

        document = minidom.Document()
        root = document.createElement("actions")
        document.appendChild(root)
        for action in actions:
            action_node = document.createElement("action")
            root.appendChild(action_node)
            for property_name, property_value in action.items():
                property_node = document.createElement(property_name)
                action_node.appendChild(property_node)

                if property_value is not None:
                    property_value_node = document.createTextNode(property_value)
                    property_node.appendChild(property_value_node)

        return document.toprettyxml(indent="    ")
