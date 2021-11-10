#!/usr/bin/env python3

from pathlib import Path

from steps.dwm.dwm import DwmStep
from steps.st.st import StStep
from steps.git import GitStep


root_dir = Path(__file__)
build_dir = root_dir.parent / "build"

steps = [
    GitStep(),
    DwmStep(),
    StStep(),
]

for step in steps:
    step.perform(build_dir)
