from steps.step import Step
from utils.file_writer import FileType


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
            (self._env.get("LINUX_SETUP_ROOT"), "Linux Setup"),
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
        linux_setup_root = self._env.get("LINUX_SETUP_ROOT")
        extensions = ["png", "jpg", "jpeg", "avif"]
        extensions = ";".join([f"*.{x}" for x in extensions])

        return f"""
<?xml version="1.0" encoding="UTF-8"?>
<actions>
<action>
    <icon>utilities-terminal</icon>
    <name>Open Terminal Here</name>
    <unique-id>1637948686926980-1</unique-id>
    <command>st</command>
    <description>Example for a custom action</description>
    <patterns>*</patterns>
    <startup-notify/>
    <directories/>
</action>
<action>
    <icon>preferences-desktop-wallpaper</icon>
    <name>Set wallpaper and generate colors</name>
    <unique-id>1638740948234297-1</unique-id>
    <command>bash -c  &quot;{linux_setup_root}/steps/gui/select_wallpaper.sh  %f 1&quot;</command>
    <description></description>
    <patterns>{extensions}</patterns>
    <image-files/>
</action>
<action>
    <icon></icon>
    <name>Copy contents to clipboard</name>
    <unique-id>1639403858591371-1</unique-id>
    <command>cat %f | tr -d &apos;\n&apos; | xclip -selection CLIPBOARD</command>
    <description></description>
    <patterns>*</patterns>
    <text-files/>
</action>
</actions>
"""
