#!/usr/bin/sh
if [ "$(id -u)" -eq 0 ]; then
   echo "This script must not be run as root"
   exit 1
fi

# Get parameters
ssh_key_path="$1"
user_name="$2"
if [ -z "$ssh_key_path" ] || [ ! -f "$ssh_key_path" ]; then
    echo "ERROR: specify path to ssh key"
    exit 1
fi
if [ -z "$user_name" ]; then
    user_name="DziubanMaciej"
fi
ssh_key_name=$(basename "$ssh_key_path")

# Create ssh folder
mkdir ~/.ssh -p

echo "Copying $ssh_key_path to ~/.ssh/$ssh_key_name"
cp "$ssh_key_path" "$HOME/.ssh/$ssh_key_name"
ssh-keygen -f "$HOME/.ssh/$ssh_key_name" -y > "$HOME/.ssh/$ssh_key_name.pub"

echo "Creating ssh config"
cat > ~/.ssh/config << EOM
IdentityFile ~/.ssh/$ssh_key_name

Host github.com bitbucket.org
    User $user_name

EOM

echo "Setting up known_hosts for typical sites"
ssh-keyscan github.com 2>/dev/null >> ~/.ssh/known_hosts

echo "Redirecting all traffic to github.com to SSH"
git config --global url."ssh://git@github.com".insteadOf https://github.com

echo "Setting permissions (read-write only for the user $(whoami))"
sudo chmod 700 ~/.ssh
sudo chmod 600 ~/.ssh/*
