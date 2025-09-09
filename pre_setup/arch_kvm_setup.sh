#!/usr/bin/sh

# This is by far the most cursed thing I had to do on my Linux setup. If we want the display to work correctly via KVM,
# we need to config A LOT. Problems encountered:
#  0. Can't restore GUI. When we have a working Xorg display and switch to another VT (ctrl+alt+F1) and then go back, the screen
#     is blank. Only cursor is visible. This turned out to be a non-KVM problem, mainly related to Spieven.
#  1. Slow VT switching. Switching between different VTs, even text-only ones takes a few seconds. I cannot reproduce this in
#     any was now, but I saw it.
#  2. Can't switch to text VT. Switching between text VTs works, but as soon as display is created, we cannot switch to a text VT,
#     the screen goes blank. We can go back to GUI VT. This is fixed by xorg config disabling EDID on direct monitor connection.
#     For KVM we need fake EDID binary planted into initramfs, xorg config and kernel params.
#  3. Nothing visible via KVM. This can be fixed by kernel parameters to NVIDIA drivers.
#  4. Display not visible via KVM. Text VT is visible, but when startx is launched, there's blank screen. This requires kernel
#     parameters AND xorg config.
#
# This is really, really, really messed up. I cannot imagine going through the freaking hell of debuggin this madness once again,
# so I'm writing this script and these instructions. The amount of reboots, messages with chatgpt, tried combinations are unthinkable.
# Normally I stand firmly on Linux side, but this is insane. Windows works without a single hiccup for this setup. To be fair, it's
# probably a fault of proprietary NVIDIA drivers and not Linux ecosystem itself. I'm not sure why I haven't tried nouveau. Maybe it
# would work. I have to try it someday. Or maybe not.
#
# Do not touch this trash. Just run the script, hope it succeeds and be happy. If I ever have to go back to debugging this, maybe it
# would be good idea to just throw the KVM out of the window and connect monitor to PC directly. Buy a second desk, quit job, dunno.
# It's just too much.

# ---------------------------------------------------------------------------------------------------------------------
logfile=kvm_setup.errorlog
rm -f $logfile
touch $logfile
failure() {
    cat $logfile
    echo "ERROR: $1"
    exit 1
}



# ---------------------------------------------------------------------------------------------------------------------
echo "1. Generating fake EDID binary"
#  The modeline line was generated with "cvt 2560 1440 60". Hardcoding it here, because I'm not sure whether it will be
#  installed on clean Arch (too lazy to check). Also, I had to edit the modeline name, because cvt generated too long one
#  and edid-generator complained.
if ! [ -d "edid-generator" ]; then
    git clone https://github.com/akatrevorjay/edid-generator.git >$logfile 2>&1 || failure "Cannot download edid-generator"
fi
cd edid-generator    || failure "cd edid-generator"
echo "Modeline "2K_60Hz"  312.25  2560 2752 3024 3488  1440 1443 1448 1493 -hsync +vsync" | ./modeline2edid >$logfile 2>&1 - || failure "edid-generator modeline2edid failed"
[ -f "2K_60Hz.S" ]   || failure "generated EDID .S file was not found"
make >$logfile 2>&1  || failure "edid-generator make failed"
[ -f "2K_60Hz.bin" ] || failure "generated EDID .bin file was not found"



# ---------------------------------------------------------------------------------------------------------------------
echo "2. Installing fake EDID binary to firmware directory (/usr/lib/firmware/edid/)"
edid_dir=/usr/lib/firmware/edid/
edid_path=/usr/lib/firmware/edid/2K_60Hz.bin
mkdir -p $edid_dir          || failure "mkdir $edid_dir"
cp ./2K_60Hz.bin $edid_path || failure "copying fake edid to $edid_dir failed"



# ---------------------------------------------------------------------------------------------------------------------
echo "3. Applying fake EDID to initramfs (/etc/mkinitcpio.conf)"
[ -f /etc/mkinitcpio.conf ]                       || failure "no /etc/mkinitcpio.conf. Is this different distro than arch?"
echo "FILES=($edid_path)" >> /etc/mkinitcpio.conf || failure "failed to edit /etc/mkinitcpio.conf"
mkinitcpio -P >$logfile 2>&1                      || failure "mkinitcpio failed"



# ---------------------------------------------------------------------------------------------------------------------
echo "4. Applying fake EDID to NVIDIA kernel parameters (/etc/default/grub)"
#  Note we're hardcoding DP-1 here. It corresponds to a specific physical display port output of the GPU as seen by the DRM.
#  This is hardcoded to left-most port on my RTX 2070 Super. This madness won't work if I ever plug the cable into a different
#  port in In order to check how a port is named, boot in a sane setup (without KVM) and run below command:
#     for f in /sys/class/drm/card?-*/status; do echo -n "$f: "; cat ""; done
grub_file=/etc/default/grub
sed -ie 's/GRUB_CMDLINE_LINUX_DEFAULT="\(.*\)"/GRUB_CMDLINE_LINUX_DEFAULT="\1 nvidia-drm.modeset=1 video=DP-1:2560x1440@60D drm.edid_firmware=DP-1:edid\/2K_60Hz.bin"/g' $grub_file  || failure "grub config insertion failed"
grub-mkconfig -o /boot/grub/grub.cfg >$logfile 2>&1 || failure "grub-mkconfig failed"



# ---------------------------------------------------------------------------------------------------------------------
echo "5. Applying fake EDID to Xorg (/etc/X11/xorg.conf.d/10-nvidia-forced-output.conf)"
#  Note we're hardcoding DFP-0 here, similarly to kernel parameters. This is a different naming then in point 4. It's a NVIDIA
#  internal abstraction that somehow maps to the DRM port names. We can query it on a sane setup with:
#    grep  " connected" /home/maciej/.local/share/xorg/Xorg.0.log
#  or:
#    nvidia-settings -q dpys
cat <<EOF > /etc/X11/xorg.conf.d/10-nvidia-forced-output.conf || failure "failed writing xorg config"
Section "Monitor"
    Identifier     "Monitor0"
    Option         "PreferredMode" "2560x1440"
    HorizSync      30.0 - 144.0
    VertRefresh    50.0 - 75.0
    Option         "DPMS" "false"
EndSection

Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    Option         "AllowEmptyInitialConfiguration" "true"
    #Option         "UseEDID" "false"
    Option         "UseDisplayDevice" "DFP-0"
    Option         "ConnectedMonitor" "DFP-0"
    Option         "CustomEDID" "DFP-0:/usr/lib/firmware/edid/2K_60Hz.bin"
    Option         "UseNvKmsCompositionPipeline" "true"
EndSection

Section "Screen"
    Identifier     "Screen0"
    Device         "Device0"
    Monitor        "Monitor0"
    DefaultDepth   24
    SubSection "Display"
        Depth     24
        Modes     "2560x1440"
    EndSubSection
EndSection
EOF
