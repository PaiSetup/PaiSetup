#!/usr/bin/sh
if [ "$(id -u)" -ne 0 ]; then
   echo "This script must be run as root"
   exit 1
fi

echo "Installing packages"
pacman -Syu --noconfirm grub efibootmgr os-prober

echo "Installing grub to /efi"
grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=GRUB
grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=GRUB --removable # This should not be needed, but my PC doesn't let me boot the grub without it

echo "Backing up default /etc/default/grub file"
grub_file=/etc/default/grub
cp "$grub_file" "$grub_file.backup"

echo "Installing grub theme"
git clone https://github.com/trueNAHO/grub2-theme-vimix-very-dark-blue /tmp/vimix
(cd /tmp/vimix && chown maciej . -R && su maciej -c "makepkg -si --noconfirm")

echo "Customizing grub"
sed -i 's/GRUB_TIMEOUT=.*/GRUB_TIMEOUT=1/g' "$grub_file"
sed -iE 's/[# ]*GRUB_DISABLE_OS_PROBER=.*/GRUB_DISABLE_OS_PROBER="false"/g' "$grub_file"
grub_theme_file="/usr/share/grub/themes/grub-theme-vimix-very-dark-blue/theme.txt"
if [ -f "$grub_theme_file" ]; then
    grub_theme_file_escaped="$(echo "$grub_theme_file" | sed "s/\//\\\\\//g")"
    sed -iE "s/[# ]*GRUB_THEME=.*/GRUB_THEME=\"$grub_theme_file_escaped\"/g" "$grub_file"
    sed -iE 's/[# ]*GRUB_BACKGROUND=.*/#GRUB_BACKGROUND="\/path\/to\/wallpaper"/g' "$grub_file"
fi
grep -E "^[# ]*GRUB_(TIMEOUT|DISABLE_OS_PROBER|THEME|BACKGROUND)=" "$grub_file" | sed "s/^/    /g"

echo "Generating /boot/grub/grub.cfg file"
os-prober
grub-mkconfig -o /boot/grub/grub.cfg
