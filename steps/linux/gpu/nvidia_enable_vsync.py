#!/bin/python

from utils import command
from utils.log import log
import re


def main(warning_hub):
    def warning(message):
        if warning_hub is not None:
            warning_hub.push(message)
        else:
            log(f"WARNING: {message}")

    output = command.run_command("nvidia-settings --q CurrentMetaMode", return_stdout=True)
    output = [x for x in output.splitlines() if "Attribute" in x]  # One line per display
    for output_line in output:
        regex = re.search(":: ([0-9a-zA-Z-]+): (.*)", output_line)
        if regex is None:
            warning("could not parse nvidia-settings")
            continue
        display = regex[1]
        config = regex[2]
        if "ForceFullCompositionPipeline=On" in config:
            log(f"Vsync already enabled for {display}")
        else:
            log(f"Enabling vsync for {display}")
            config = config.replace("}", ", ForceFullCompositionPipeline=On}")
            command.run_command(f'nvidia-settings --assign "CurrentMetaMode[{display}]={config}"')


if __name__ == "__main__":
    main(None)
