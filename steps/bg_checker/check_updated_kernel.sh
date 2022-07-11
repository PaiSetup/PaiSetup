if [ -z "$(find /lib/modules -maxdepth 1 -type d -name "$(uname -a | cut -d' ' -f3)")" ]; then
    echo "Possible kernel update detected. Some kernel modules may not work."
fi
