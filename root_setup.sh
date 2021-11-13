#!/usr/bin/sh
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Basic packages
pacman -Syu --noconfirm sudo

# Create user
USERNAME=maciej
useradd -m $USERNAME
passwd $USERNAME
groupadd sudo
usermod -aG tty $USERNAME

# Enable sudo
visudo
printf '\n# Allow sudoers to use sudo without password\n%%sudo ALL=(ALL) NOPASSWD: ALL\n' | sudo EDITOR='tee -a' visudo

# Login as the new user
su $USERNAME
