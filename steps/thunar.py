from steps.step import Step
from utils.file_writer import FileType


class ThunarStep(Step):
    def __init__(self):
        super().__init__("Thunar")
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
        self._file_writer.write_lines(
            ".config/Thunar/uca.xml",
            [self.get_uca_xml_contents()],
            file_type=FileType.Xml,
        )

    def get_uca_xml_contents(self):
        return """
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
    <command>bash -c  &quot;/home/maciej/LinuxSetup/steps/gui/select_wallpaper.sh  %f 1&quot;</command>
    <description></description>
    <patterns>*.png</patterns>
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
