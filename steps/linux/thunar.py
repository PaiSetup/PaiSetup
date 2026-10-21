from xml.dom import minidom

from steps.step import Step
from utils.dependency_dispatcher import push_dependency_handler
from utils.services.file_writer import FileType


class ThunarCustomAction:
    def __init__(
        self,
        name,
        command,
        spawn_terminal=False,
        directories=False,
        audio_files=False,
        image_files=False,
        text_files=False,
        video_files=False,
        other_files=False,
    ):
        self.name = name
        self.command = command
        self.spawn_terminal = spawn_terminal
        self.file_types = {
            "directories": directories,
            "audio-files": audio_files,
            "image-files": image_files,
            "text-files": text_files,
            "video-files": video_files,
            "other-files": other_files,
        }


class ThunarStep(Step):
    def __init__(self):
        super().__init__("Thunar")
        self.disable_suspending_command = ""
        self.actions = []
        self._bookmarks = []

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
        self._add_default_custom_actions()
        self._setup_bookmarks()
        self._generate_uca_xml()

    def _add_default_custom_actions(self):
        self.add_thunar_custom_action(
            ThunarCustomAction(
                name="Open terminal here",
                command=f"{self._env.get("TERMINAL")}",
                directories=True,
            )
        )
        self.add_thunar_custom_action(
            ThunarCustomAction(
                name="Set wallpaper and generate colors",
                command=f'bash -c "{self._env.get("PAI_SETUP_ROOT")}/steps/linux/gui/scripts/select_wallpaper.py --wallpaper_file %f --restart_wm"',
                image_files=True,
            )
        )
        self.add_thunar_custom_action(
            ThunarCustomAction(
                name="Copy contents to clipboard",
                command="cat %f | tr -d '\n' | xclip -selection CLIPBOARD",
                text_files=True,
            )
        )

    def _setup_bookmarks(self):
        self._bookmarks += [
            (self._env.home() / "downloads", "Downloads"),
            (self._env.get("PAI_SETUP_ROOT"), "PaiSetup"),
        ]

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
            command = action.command
            if action.spawn_terminal:
                command = f'{self._env.get("TERMINAL_CMD")} sh -c "{command}"'

            action_node = self._append_xml_node(document, root, "action", None)
            self._append_xml_node(document, action_node, "name", action.name)
            self._append_xml_node(document, action_node, "command", command)
            for file_type, enabled in action.file_types.items():
                if enabled:
                    self._append_xml_node(document, action_node, file_type, None)

        self._file_writer.write_lines(
            file_path,
            [document.toprettyxml(indent="    ")],
            file_type=FileType.Xml,
        )

    @staticmethod
    def _append_xml_node(document, parent, name, text):
        node = document.createElement(name)
        if text is not None:
            node.appendChild(document.createTextNode(text))
        parent.appendChild(node)
        return node
