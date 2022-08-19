from steps.step import Step
from pathlib import Path
from shutil import copyfile
import os
from steps.dotfiles import FileType, LinePlacement
from utils.log import log
import utils.external_project as ext
from utils import command
from steps.gui.gui import GuiStep


class AwesomeStep(GuiStep):
    def __init__(self, root_build_dir, fetch_git):
        super().__init__("Awesome")
        self.root_build_dir = root_build_dir
        self.fetch_git = fetch_git
        self._current_step_dir = Path(__file__).parent
        self._xresources_path = f".config/LinuxSetup/awesome/Xresources"
        self._xinitrc_path = f".config/LinuxSetup/awesome/xinitrc"
        self._app_keybindings_path = f"{self._current_step_dir}/config/utils/app_keybindings.lua"
        self._keybindings = []

    def add_keybindings(self, *keybindings, **kwargs):
        self._keybindings += keybindings

    def perform(self):
        self._setup_app_keybindings_code()


    def register_as_dependency_listener(self, dependency_dispatcher):
        dependency_dispatcher.register_listener(self.add_keybindings)

    def express_dependencies(self, dependency_dispatcher):
        super().express_dependencies(dependency_dispatcher)

        dependency_dispatcher.add_packages("awesome")

        dependency_dispatcher.add_dotfile_symlink(
            src=self._current_step_dir / "config",
            link=".config/awesome",
            prepend_home_dir_src=False,
            prepend_home_dir_link=True,
        )

        self._setup_xinitrc_awesome(dependency_dispatcher)
        self._setup_xresources(dependency_dispatcher)

    def _setup_xinitrc_awesome(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Call base script",
            [". ~/.config/LinuxSetup/xinitrc_base"],
        )
        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Load Xresources",
            [
                "rm ~/.config/Xresources 2>/dev/null",
                f"ln -sf ~/{self._xresources_path} ~/.config/Xresources",
                f"xrdb ~/.config/Xresources",
            ],
        )
        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Define mouse button values for statusbar scripts",
            [
                "export BUTTON_ACTION=1",
                "export BUTTON_TERMINATE=2",
                "export BUTTON_INFO=3",
                "export BUTTON_SCROLL_UP=4",
                "export BUTTON_SCROLL_DOWN=5",
            ],
        )
        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Run picom",
            ["picom -b --no-fading-openclose  &"],
        )
        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Run AwesomeWM",
            ["exec awesome"],
            line_placement=LinePlacement.End,
        )

        # TODO pass some value like "is_default_wm" to the step and run this
        # dependency_dispatcher.add_dotfile_symlink(src=".config/LinuxSetup/xinitrc_awesome", link=".xinitrc")

    def _setup_xresources(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_section(
            self._xresources_path,
            "Apps styles",
            [f'#include "{os.environ["HOME"]}/.config/XresourcesApp"'],
            file_type=FileType.XResources,
        )
        dependency_dispatcher.add_dotfile_section(
            self._xresources_path,
            "Theme colors",
            [
                f'#include "{os.environ["HOME"]}/.config/Xresources.theme"',
                "#define COL_THEME2 #878787",
                "#define COL_THEME3 #555555",
            ],
            file_type=FileType.XResources,
        )
        dependency_dispatcher.add_dotfile_section(
            self._xresources_path,
            "Colors readable by AwesomeWM",
            [
                "color1: COL_THEME1",
                "color2: COL_THEME2",
                "color3: COL_THEME3",
                "color4: #ffffff",
            ],
            file_type=FileType.XResources,
        )

    def _setup_app_keybindings_code(self):
        lines = [
            'local awful = require("awful")',
            'local gears = require("gears")',
            "local function get_keybindings(modkey)",
        ]

        if len(self._keybindings) > 0:
            lines.append("    return gears.table.join(")
            for keybinding in self._keybindings:
                for key in keybinding.keys:
                    modifiers = []
                    if keybinding.hold_mod:
                        modifiers.append("modkey")
                    if keybinding.hold_shift:
                        modifiers.append('"Shift"')
                    if keybinding.hold_ctrl:
                        modifiers.append('"Control"')

                    modifiers = f"{{{', '.join(modifiers)}}}"
                    lines.append(f'        awful.key({modifiers}, "{key}", function () awful.spawn("{keybinding.command}") end, {{description = "", group = "App launching"}}),')
            lines[-1] = lines[-1][:-1] # Remove trailing comma from last line
        else:
            lines.append("    return {}")

        lines += [
            ")",
            "end",
            "return {",
            "    get_keybindings = get_keybindings,",
            "}",
        ]
        self._file_writer.write_lines(self._app_keybindings_path, lines, file_type=FileType.Lua, prepend_home_dir=False)
