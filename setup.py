#!/usr/bin/env python3

from pathlib import Path

from steps.dwm.dwm import DwmStep
from steps.st.st import StStep
from steps.git import GitStep
from steps.packages import PackagesStep


root_dir = Path(__file__)
build_dir = root_dir.parent / "build"

steps = [
    PackagesStep(build_dir),  # This must be the first step
    GitStep(),
    DwmStep(build_dir, True),
    StStep(build_dir, True),
]

for step in steps:
    steps[0].add_packages(step.get_required_packages())

for step in steps:
    step.perform()
