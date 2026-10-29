class SetupFlags:
    def __init__(self, *, install_packages, strict_download, strict_build, strict_install, strict_config, strict_explorer):
        self.install_packages = install_packages
        self.strict_download = strict_download
        self.strict_build = strict_build
        self.strict_install = strict_install
        self.strict_config = strict_config
        self.strict_explorer = strict_explorer
