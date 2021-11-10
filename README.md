Arch Linux installation
  - Boot in UEFI mode
  - https://wiki.archlinux.org/title/installation_guide
  - Remember to install networkmanager in pacstrap
  - https://wiki.archlinux.org/title/GRUB#UEFI_systems

After installation
  1. create user
```
useradd -m maciej
passwd maciej
groupadd sudo
usermod -aG sudo maciej
usermod -aG tty maciej
visudo # Add line: sudo   ALL=(ALL) NOPASSWD: ALL
```
  2. tbd