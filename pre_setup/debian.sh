#!/usr/bin/sh
if [ "$(id -u)" -ne 0 ]; then
   echo "This script must be run as root"
   exit 1
fi

PATH=/usr/sbin:$PATH

USERNAME="${1:-maciej}"
echo "Username: $USERNAME"

echo "Adding user to tty group"
usermod -aG tty $USERNAME

echo "Enabling sudo"
usermod -aG sudo $USERNAME
printf '\n# Allow sudoers to use sudo without password\n%%sudo ALL=(ALL) NOPASSWD: ALL\n' | sudo EDITOR='tee -a' visudo

echo "Installing essential packages"
apt-get install --yes git python3 curl

echo "Making symlinks for python"
ln -s /usr/bin/python3 /usr/bin/python
