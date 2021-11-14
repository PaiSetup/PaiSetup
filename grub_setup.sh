#!/usr/bin/sh
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

echo "Installing packages"
pacman -Syu --noconfirm grub efibootmgr

echo "Installing grub to /efi"
grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=GRUB

echo "Generating /boot/grub/grub.cfg file"
grub-mkconfig -o /boot/grub/grub.cfg
