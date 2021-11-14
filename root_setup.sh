#!/usr/bin/sh
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

echo "Configuring time"
timedatectl set-ntp true
ln -s /usr/share/zoneinfo/Europe/Warsaw /etc/localtime
hwclock --systohc

echo "Setting up locales"
echo "pl_PL.UTF-8 UTF-8" >> /etc/locale.gen
echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" >> /etc/locale.conf
loadkeys pl
localectl set-x11-keymap pl
setxkbmap pl
echo pl > /etc/vconsole.conf

echo "Configuring root passwd"
passwd

USERNAME=maciej
echo "Creating user: $USERNAME"
useradd -m $USERNAME
passwd $USERNAME
groupadd sudo
usermod -aG tty $USERNAME

echo "Setting up network"
pacman -Syu --noconfirm networkmanager
systemctl enable NetworkManager
echo $USERNAME_arch > /etc/hostname

echo "Enabling sudo"
pacman -Syu --noconfirm sudo
visudo
printf '\n# Allow sudoers to use sudo without password\n%%sudo ALL=(ALL) NOPASSWD: ALL\n' | sudo EDITOR='tee -a' visudo

echo "Switching to user $USERNAME"
su $USERNAME
