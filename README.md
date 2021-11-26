# Arch Linux installation
  - Boot in UEFI mode
  - Install system according to https://wiki.archlinux.org/title/installation_guide and https://wiki.archlinux.org/title/GRUB#UEFI_systems
    - disregard all locales, keyboard configs, clocks, etc. They will be setup by the scripts
    - partition the drive
    - format partitions:
      ```
      mkfs.fat -F32 /dev/sda1
      mkswap /dev/sda2
      mkfs.ext4 /dev/sda3
      ```
    - mount partitions and enable swap
      ```
      mount /dev/sda3 /mnt`
      mkdir /mnt/efi
      mount /dev/sda1 /mnt/efi
      swapon /dev/sda2
      ```
    - install os and basic tools `pacstrap /mnt base linux linux-firmware git python base-devel`
    - generate fstab
      ```
      genfstab -U /mnt >> /mnt/etc/fstab
      ```
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
    - Reboot
    - OS should boot into graphical interface

WARNING: only `setup.py` script can be run multiple times safely. Running other `.sh` scripts repeatedly can have unforseen consequences.
