from steps.step import SucklessSoftwareStep
from pathlib import Path


class StStep(SucklessSoftwareStep):
    def __init__(self):
        super().__init__(
            "st",
            "https://git.suckless.org/st",
            "0.8.2",
            Path(__file__).parent,
        )
