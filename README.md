# Arch Linux installation
  - Boot in UEFI mode
  - Install system according to https://wiki.archlinux.org/title/installation_guide and https://wiki.archlinux.org/title/GRUB#UEFI_systems
    - disregard all locales, keyboard configs, clocks, etc. They will be setup by the scripts
    - partition the drive (`fdisk /dev/sda`)
      - EFI partition: 512MB, type *EFI System* (1)
      - Swap partition: 4-8GB, type *Linux Swap* (19)
      - Root partition: Minimum 15GB, type *Linux root x86-64* (23)
    - format partitions:
      ```
      mkfs.fat -F32 /dev/sda1
      mkswap /dev/sda2
      mkfs.ext4 /dev/sda3
      ```
    - mount partitions and enable swap
      ```
      mount /dev/sda3 /mnt
      mkdir /mnt/efi
      mount /dev/sda1 /mnt/efi
      swapon /dev/sda2
      ```
    - install os and basic tools `pacstrap /mnt base linux-lts linux-firmware git python base-devel`
    - generate fstab
      ```
      genfstab -U /mnt >> /mnt/etc/fstab
      ```
    - arch-chroot /mnt
  - Root-level configuration
    - Run commands
        ```
        git clone https://github.com/InternalMD/LinuxSetup
        LinuxSetup/root_setup.sh
        LinuxSetup/grub_setup.sh
        rm -rf LinuxSetup
        exit
        reboot
        ```
    - Machine should reboot and enter GRUB, which should boot the Arch Linux and allow you to login as user
  - User-level configuration
    - Log in as user
    - run commands
        ```
        git clone https://github.com/InternalMD/LinuxSetup
        LinuxSetup/ssh_setup.sh <private_key_path> <git_user_name>
        LinuxSetup/setup.py
        ```
    - Reboot
    - OS should boot into graphical interface
    - Run `setup.py` one more time. Some configuration (e.g. VSCode extensions) can be done only in graphical environment.
  - Manual configuration
    - Automatic mounts in `/etc/fstab`
    - MEGA
      - Sync exclusions:
        - */home/maciej/Multimedia/Movies*
        - */home/maciej/Multimedia/Music*
        - */home/maciej/Multimedia/MusicToRate*
        - */home/maciej/Multimedia/TvSeries*
      - Syncs:
        - */home/maciej/Multimedia* <-> *Backup/Multimedia*

WARNING: only `setup.py` script can be run multiple times safely. Running other `.sh` scripts repeatedly can have unforseen consequences.
