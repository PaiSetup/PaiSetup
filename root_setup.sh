#!/usr/bin/sh
if [ "$(id -u)" -ne 0 ]; then
   echo "This script must be run as root" 
   exit 1
fi

echo "Configuring time"
timedatectl set-ntp true
ln -s /usr/share/zoneinfo/Europe/Warsaw /etc/localtime
hwclock --systohc

echo "Setting up locales"
echo "pl_PL.UTF-8 UTF-8" >> /etc/locale.gen
echo "en_GB.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
echo "LANG=en_GB.UTF-8" >> /etc/locale.conf
loadkeys pl
echo pl > /etc/vconsole.conf

echo "Configuring root passwd"
passwd

USERNAME=maciej
echo "Creating user: $USERNAME"
useradd -m $USERNAME
passwd $USERNAME
usermod -aG tty $USERNAME

echo "Setting up network"
pacman -Syu --noconfirm networkmanager
systemctl enable NetworkManager
echo "$USERNAME"_arch > /etc/hostname

echo "Enabling sudo"
pacman -Syu --noconfirm sudo
groupadd sudo
usermod -aG sudo $USERNAME
printf '\n# Allow sudoers to use sudo without password\n%%sudo ALL=(ALL) NOPASSWD: ALL\n' | sudo EDITOR='tee -a' visudo
