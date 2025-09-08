#!/bin/python

import json
import os
import sys
import time
from enum import Enum, auto

from utils.command import *

spieven_bin = "spieven"


class SpievenMessage:
    def __init__(self, title, description=""):
        self.title = title.strip()
        self.description = description.strip()
        self.short_description = self.description.split("\n")[0]

    @staticmethod
    def gui_log_summary(messages):
        if messages:
            lines = "\n".join((msg.short_description or msg.title for msg in messages))
            run_command(f'notify-send "⚠️ Spieven warnings" "{lines}"')
        else:
            run_command(f'notify-send "✅ No warnings"')

    @staticmethod
    def gui_log_detailed(messages):
        for msg in messages:
            run_command(f'notify-send "{msg.title}" "{msg.description}"')

    @staticmethod
    def console_log(messages):
        for msg in messages:
            print(f"{msg.title} {msg.description}")


class ScriptMode(Enum):
    Console = auto()
    GuiStatusOnly = auto()
    GuiInfo = auto()
    GuiAction = auto()
    GuiTerminate = auto()

    @staticmethod
    def get():
        try:
            button_info = os.environ["BUTTON_INFO"]
            button_action = os.environ["BUTTON_ACTION"]
            button_terminate = os.environ["BUTTON_TERMINATE"]
        except KeyError:
            return ScriptMode.Console

        try:
            current_button = os.environ["BUTTON"]
        except KeyError:
            try:
                current_button = sys.argv[1]
            except IndexError:
                current_button = ""

        if current_button == 0:
            return ScriptMode.Console
        elif current_button == button_info:
            return ScriptMode.GuiInfo
        elif current_button == button_action:
            return ScriptMode.GuiAction
        elif current_button == button_terminate:
            return ScriptMode.GuiTerminate
        else:
            return ScriptMode.GuiStatusOnly

    def is_gui(self):
        return self in [ScriptMode.GuiStatusOnly, ScriptMode.GuiInfo, ScriptMode.GuiTerminate, ScriptMode.GuiAction]


def query_task_names():
    task_names = None
    errors = []
    try:
        task_names = os.environ["PAI_SETUP_SPIEVEN_TASKS"]
        task_names = task_names.split(",")
    except KeyError:
        errors.append(SpievenMessage("Spieven error", "Could not find a list of spieven tasks. PAI_SETUP_SPIEVEN_TASKS env is missing."))
    return task_names, errors


def query_spieven_state(task_names):
    task_names_str = ",".join(task_names)
    # TODO sometimes Spieven hangs with multi-xorg VT switching. Install a debug version in the system and debug why
    # TODO add --no-auto-run parameter and pass it here
    command = f"{spieven_bin} list --tags PaiSetup --names {task_names_str} --unique-names --include-deactivated --json"
    output = None
    errors = []
    try:
        output = run_command(command, stdout=Stdout.return_back(), stderr=Stdout.ignore())
    except CommandError as e:
        errors.append(SpievenMessage("Spieven error", "Could not query spieven tasks"))

    if not errors:
        try:
            output = json.loads(output.stdout)
        except:
            errors.append(SpievenMessage("Spieven error", "Could not parse spieven output"))

    return output, errors


def find_task(spieven_state, task_name):
    for task in spieven_state:
        if task["FriendlyName"] == task_name:
            return task
    return None


def validate_tasks(spieven_state, task_names):
    errors = []

    for task_name in task_names:
        task = find_task(spieven_state, task_name)
        if task is None:
            errors.append(SpievenMessage(f"Spieven {task_name} isn't running"))
            continue

        tags = task["Tags"]
        is_periodic_check = "PaiSetupPeriodicCheck" in tags
        is_periodic_action = "PaiSetupPeriodicAction" in tags
        is_daemon = "PaiSetupDaemon" in tags

        if task["IsDeactivated"]:
            reason = task["DeactivationReason"]
            w = "daemon" if is_daemon else "task"
            errors.append(SpievenMessage(f"Spieven {w} {task_name} is deactivated", f"Reason: {reason}"))
            continue

        if is_periodic_check:
            exit_value = task["LastExitValue"]
            if exit_value != 0:
                stdout = task["LastStdout"]
                errors.append(SpievenMessage(f"{task_name} failed", stdout))
        elif is_periodic_action:
            pass
        elif is_daemon:
            if task["RunCount"] > 100:
                errors.append(
                    SpievenMessage(
                        f"{task_name} ran over 100 times",
                        "This is not strictly an error, but it's suspicious. Isn't it early exiting?",
                    )
                )
        else:
            errors.append(SpievenMessage(f"{task_name} has unknown task type"))

    return errors


icon = "⚠️ "
task_names, errors = query_task_names()
if not errors:
    spieven_state, errors = query_spieven_state(task_names)
if not errors:
    errors = validate_tasks(spieven_state, task_names)
if not errors:
    icon = ""

script_mode = ScriptMode.get()
match script_mode:
    case ScriptMode.GuiStatusOnly:
        pass
    case ScriptMode.GuiAction:
        run_command(f"{spieven_bin} refresh --tags PaiSetup")
        SpievenMessage.gui_log_detailed([SpievenMessage("Spieven tasks refreshed")])
        time.sleep(0.2)  # This is a hack to make some quicker checks finish before the read
        SpievenMessage.gui_log_summary(errors)
    case ScriptMode.GuiInfo:
        SpievenMessage.gui_log_summary(errors)
    case ScriptMode.GuiTerminate:
        SpievenMessage.gui_log_summary(errors)
        SpievenMessage.gui_log_detailed(errors)
    case ScriptMode.Console:
        SpievenMessage.console_log(errors)


if script_mode.is_gui():
    print(icon, end="")
