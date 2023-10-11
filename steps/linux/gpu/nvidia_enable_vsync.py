#!/bin/python

from utils import command
import re


def main(logger):
    output = command.run_command("nvidia-settings --q CurrentMetaMode", stdout=command.Stdout.return_back())
    output = [x for x in output.splitlines() if "Attribute" in x]  # One line per display
    for output_line in output:
        regex = re.search(":: ([0-9a-zA-Z-]+): (.*)", output_line)
        if regex is None:
            logger.push_warning("could not parse nvidia-settings")
            continue
        display = regex[1]
        config = regex[2]
        if "ForceFullCompositionPipeline=On" in config:
            logger.log(f"Vsync already enabled for {display}")
        else:
            logger.log(f"Enabling vsync for {display}")
            config = config.replace("}", ", ForceFullCompositionPipeline=On}")
            command.run_command(f'nvidia-settings --assign "CurrentMetaMode[{display}]={config}"')


if __name__ == "__main__":
    class BackupLogger:
        def push_warning(self, message):
            print(f"WARNING: {message}")

        def log(self, message):
            print(message)

    main(BackupLogger())
