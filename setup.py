#!/usr/bin/env python3

from pathlib import Path

from steps.dwm.dwm import DwmStep
from steps.st.st import StStep
from steps.git import GitStep
from steps.packages import PackagesStep
from steps.dotprofile import DotProfileStep


root_dir = Path(__file__)
build_dir = root_dir.parent / "build"

steps = [
    PackagesStep(build_dir),  # This must be the first step
    DotProfileStep(),
    GitStep(),
    DwmStep(build_dir, True),
    StStep(build_dir, True),
]

for step in steps:
    if hasattr(steps[0], "add_packages"):
        steps[0].add_packages(step.get_required_packages())

for step in steps:
    step.perform()
