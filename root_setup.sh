#!/usr/bin/sh
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Configure time
timedatectl set-ntp true
ln -s /usr/share/zoneinfo/Europe/Warsaw /etc/localtime
hwclock --systohc

# Locale
echo "pl_PL.UTF-8 UTF-8" >> /etc/locale.gen
echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" >> /etc/locale.conf
loadkeys pl
localectl set-x11-keymap pl
setxkbmap pl
echo pl > /etc/vconsole.conf

# Create user
USERNAME=maciej
useradd -m $USERNAME
passwd $USERNAME
groupadd sudo
usermod -aG tty $USERNAME

# Enable sudo
pacman -Syu --noconfirm sudo
visudo
printf '\n# Allow sudoers to use sudo without password\n%%sudo ALL=(ALL) NOPASSWD: ALL\n' | sudo EDITOR='tee -a' visudo

# Login as the new user
su $USERNAME
