# Arch Linux installation
  - Boot in UEFI mode
  - Install system according to https://wiki.archlinux.org/title/installation_guide and https://wiki.archlinux.org/title/GRUB#UEFI_systems
    - disregard all locales, keyboard configs, clocks, etc. They will be setup by the scripts
    - partition the drive
    - mount partitions and enable swap
    - pacstrap /mnt base linux linux-firmware networkmanager git
    - generate fstab
    - arch-chroot /mnt
  - Root-level configuration
    - Run commands
        ```
        git clone https://github.com/InternalMD/LinuxSetup
        LinuxSetup/grub_setup.sh
        LinuxSetup/root_setup.sh
        rm -rf LinuxSetup
        ```
    - If everything went correctly, you should be logged in as a normal user, not root. You can now reboot.
  - User-level configuration
    - Log in as user
    - run commands
        ```
        git clone https://github.com/InternalMD/LinuxSetup
        LinuxSetup/ssh_setup.sh
        LinuxSetup/setup.py
        ```
    - reboot

WARNING: only `setup.py` script can be run multiple times safely. Running other `.sh` scripts repeatedly can have unforseen consequences.
