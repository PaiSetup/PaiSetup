#!/bin/sh

perform_arch() {
    get_unmatching_packages() {
        file_expected="$(mktemp --suffix=".expected")"
        file_actual="$(mktemp --suffix=".actual")"

        printf "Gathering expected packages in $file_expected... "
        expected_packages="$($PAI_SETUP_ROOT/setup.py --list_packages)"
        if [ $? != 0 ]; then
            return 1
        fi
        echo "$expected_packages" | sort | uniq | tee "$file_expected" | wc -l

        printf "Gathering actual packages in $file_actual... "
        yay -Qeq | sort | tee "$file_actual" | wc -l

        echo "diff \"$file_expected\" \"$file_actual\""
        diff "$file_expected" "$file_actual" --side-by-side --color=auto --suppress-common-lines

        echo "Removing tmp files"
        rm "$file_actual"
        rm "$file_expected"
    }

    packages="$(get_unmatching_packages)"
    if [ $? = 0 ]; then
        packages="$(echo "$packages" | grep -E '<|>' | sed "s/\s//g")"
        if [ -n "$packages" ]; then
            echo "$(echo "$packages" | wc -l) packages do not match with PaiSetup"
            echo "$packages"
        fi
    else
        echo "Could not gather PaiSetup packages"
    fi
}



case $($PAI_SETUP_ROOT/steps/linux/gui/scripts/get_distro.sh) in
    arch)
        perform_arch ;;
    debian)
        ;; # This cannot be easily done in Debian... Best bet would be to dump installed packages right in presetup script and diff against that.
    *)
        echo "ERROR: invalid distro"
        exit 1
esac
