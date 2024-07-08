class WidgetDefaultsConfig:
    def __init__(self):
        self.widget_defaults = dict(
            font="sans",
            fontsize=12,
            padding=3,
        )
        self.extension_defaults = self.widget_defaults.copy()
