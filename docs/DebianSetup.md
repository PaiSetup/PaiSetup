# Debian installation
  - Install Debian
    - Boot ISO from https://www.debian.org/
    - Boot in UEFI mode
    - Use either "Graphical install" or "Install", doesn't matter
    - Select all the locales, timezones, partitioning, etc.
    - TODO: tasksel. Which stuff? Which key to untick? Enter proceeds further. Add a warning.
  - Root-level configuration
    - Log in as root
    - Run commands
        ```
        git clone https://github.com/PaiSetup/PaiSetup
        PaiSetup/pre_setup/debian.sh
        rm -rf PaiSetup
        exit
        reboot
        ```
  - User-level configuration
    - Log in as user
    - run commands
        ```
        git clone https://github.com/PaiSetup/PaiSetup
        PaiSetup/setup.py
        ```
    - Reboot
    - OS should boot into graphical interface
    - Run `setup.py` one more time. Some configuration (e.g. VSCode extensions) can be done only in graphical environment.
