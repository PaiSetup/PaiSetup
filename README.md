# PaiSetup
This repository contains scripts to setup work environment on my computers in an automated manner. It includes software installation and configuration, GUI customization, keyboard, timezone, locale setting, uninstalling unneccessary preinstalled software and much more. Most of it is written in Python, although there are some parts written in Bash or Powershell, which I'm currently trying to avoid and port into Python if possible.

Currently there are scripts to setup [Arch Linux](docs/ArchLinuxSetup.md) and [Windows 10](docs/WindowsSetup.md). Other Linux distrubtions are **not** supported, because of different system paths, package managers, etc. I might port them to other distros in the future. Windows 10 scripts probably mostly work on Windows 11, but they have never been tested. I will have to do it someday before Windows 10 EOL.

Details of installing the systems are discussed in [docs](docs). In general, the scripts in [pre_setup](pre_setup) have to be called first to setup a foundation for the main *PaiSetup* machinery. Then, `setup.py` script can be called to configure every part of the system. The script is safe to be called multiple times.

NOTE: these are my private scripts, intended to use only for me, not for greater audience. I'm not even sure why I'm writing this *README*. Probably out of habit.
