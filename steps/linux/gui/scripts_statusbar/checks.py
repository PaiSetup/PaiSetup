#!/bin/python


from utils import command
import os
import sys
import time

def get_current_button():
    try:
        return os.environ["BUTTON"]
    except KeyError:
        try:
            return sys.argv[1]
        except IndexError:
            return ""
current_button = get_current_button()

def is_button(name):
    try:
        return os.environ[name] == current_button
    except KeyError:
        return false

def is_info_button():
    return is_button("BUTTON_INFO")

def is_action_button():
    return is_button("BUTTON_ACTION")

def is_terminate_button():
    return is_button("BUTTON_TERMINATE")


show_popup = False
show_detailed = False
if is_info_button():
    show_popup = True
elif is_action_button():
    show_popup = True
    check_mate_command = "check_mate_client refresh_all -p 50198 -r 1"
    warnings = command.run_command(check_mate_command)
    time.sleep(0.1) # This is a hack to make some quicker checks finish before the read
elif is_terminate_button():
    show_popup = True
    show_detailed = True

# Run CheckMate and see what warnings we have
check_mate_command = "check_mate_client read -p 50198 -r 1"
warnings = command.run_command(check_mate_command, stdout=command.Stdout.return_back())
warnings = warnings.split("\n\n") # Warnings from different clients are separated by an empty line
warnings = (x.strip().split("\n") for x in warnings if x) # Split output from each client into lines
warnings = ([x for x in y if x] for y in warnings) # Eliminate empty lines
warnings = list(warnings)

if len(warnings) == 0:
    if show_popup:
        command.run_command('notify-send "✅ No warnings" ""')
    print("", end='')
else:
    if show_popup:
        headers = [x[0] for x in warnings]
        headers = '\n'.join(headers)
        command.run_command(f'notify-send "⚠️ Warnings" "{headers}"')

        if show_detailed:
            for warning in warnings:
                if len(warning) > 1:
                    header = warning[0]
                    details = '\n'.join(warning[1:])
                    command.run_command(f'notify-send "{header}" "{details}"')

    print("⚠️ ", end='')
