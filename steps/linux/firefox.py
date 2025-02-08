import os
from pathlib import Path

from steps.step import Step
from utils.services.file_writer import FileType


class FirefoxStep(Step):
    def __init__(self, is_default_browser):
        super().__init__("Firefox")
        self._is_default_browser = is_default_browser

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("firefox")
        dependency_dispatcher.register_homedir_file(".mozilla")

    def perform(self):
        self._file_writer.write_section(
            ".profile",
            "Default browser",
            [
                "export BROWSER=firefox",
                'export BROWSER_PRIVATE="firefox --private-window"',
            ],
        )

        profile_dirs = self._get_profile_directories()
        css_content = self.get_css_content()
        for profile_dir in profile_dirs:
            css_file_path = profile_dir / "chrome/userChrome.css"
            self._logger.log(f"Installing custom css to {css_file_path}")
            self._file_writer.write_lines(
                css_file_path,
                [css_content],
                file_type=FileType.Css,
            )

            js_file_path = profile_dir / "user.js"
            self._logger.log(f"Setting up preferences")
            self._file_writer.write_lines(
                js_file_path,
                [
                    f'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);',
                    f'user_pref("general.autoScroll", true);',
                ],
                file_type=FileType.Javascript,
            )

    def _get_profile_directories(self):
        root = Path("/home/maciej/.mozilla/firefox/")
        result = []
        if root.is_dir():
            for child in root.iterdir():
                if "default-release" in child.name:
                    result.append(child)
        return result

    def get_css_content(self):
        return r"""
/* Everything but the page content */
window, #main-window, #toolbar-menubar, #TabsToolbar, #PersonalToolbar, #navigator-toolbox,#sidebar-box{
    background-color: rgba(49, 49, 58 , 0.5) !important;
    -moz-appearance: none !important;
    background-image: none !important;
}

/* Background around "Go back", "Go forward", "Refresh", "Home" buttons, the url bar the addons, etc.*/
window, #nav-bar{
    background: rgba(67, 67, 74 , 0.5) !important;
    -moz-appearance: none !important;
    background-image: none !important;
}

/* Tabs */
.tab-background[selected="true"] {
    background: rgba(82, 82, 88, 0.5) !important;
    -moz-appearance: none !important;
    background-image: none !important;
    border-radius: 30px !important;
}
tab.tabbrowser-tab:hover > stack > .tab-background {
    border-radius: 30px !important;
}

/* Shows up after clicking on url and seeing the suggestions */
#urlbar:not([open]) > #urlbar-background {
    background-color: transparent !important;
}
#urlbar[open] > #urlbar-background {
    background-color: rgba(70, 70, 76, 0.99) !important;
}

:root{
    background-color: transparent !important
}

#main-window, #tabbrowser-tabpanels {
    background-color: rgba(50, 50, 50, 0.5) !important
}
"""
