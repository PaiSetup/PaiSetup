. ~/.profile
packages="$(get_unmatching_packages | grep -E "<|>")"
if [ -n "$packages" ]; then
    echo "$(echo "$packages" | wc -l) packages do not match with LinuxSetup"
fi
