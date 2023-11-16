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
        git clone https://github.com/PaiSetup/PaiSetup
        PaiSetup/pre_setup/arch.sh
        PaiSetup/pre_setup/arch_grub.sh
        rm -rf PaiSetup
        exit
        reboot
        ```
    - Machine should reboot and enter GRUB, which should boot the Arch Linux and allow you to login as user
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
  - Manual configuration
    - Windows partition mount in `/etc/fstab`
      - Run `lsblk` to find out which partition contains user files from dual-booted Windows
      - Run `pre_setup/arch_generate_fstab_for_ntfs.sh /dev/nvme0n1p4` (assuming `/dev/nvme0n1p4` contains the partition)
      - Append script outputs to */etc/fstab*
    - MEGA
      - Sync exclusions:
        - */home/maciej/multimedia/movies*
        - */home/maciej/multimedia/music*
        - */home/maciej/multimedia/music_to_rate*
        - */home/maciej/multimedia/tv_series*
      - Syncs:
        - */home/maciej/multimedia* <-> *Backup/multimedia*
    - Plex
      - Plex home should be in `/usr/lib/plexmediaserver`, but it could be different. It is auto-discovered in setup, see logs.
      - Libraries
        - *<PLEX_HOME>/Movies*
        - *<PLEX_HOME>/TvShows*





# Useful links
## Ricing
1. DWM patches organized https://coggle.it/diagram/X9IiSSM6PTWOM9Wz/t/dwm-patches-last-tallied-2021-09-28
2. Awesome fonts (monochromatic) - https://fontawesome.com/v5/cheatsheet
3. Colored emoji - https://www.emojicopy.com/
4. Terminal colors - https://terminal.sexy

## XDG Configuration paths for various apps
https://wiki.archlinux.org/title/XDG_Base_Directory#Supported

## Searching Linux tree
https://livegrep.com/search/linux
https://mariadb.com/kb/en/operating-system-error-codes/





# Notes
NOTE: Audio may not work on first boot, due to some drivers not being enabled. Maybe I could enable them with modprobe, but it's just easier to reboot.

TODO: merge arch.sh and arch_grub.sh scripts into one
