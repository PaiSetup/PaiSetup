#!/bin/sh
. ~/.profile # for get_unmatching_packages command

packages="$(get_unmatching_packages)" # TODO move this into PaiSetup
if [ $? = 0 ]; then
    packages="$(echo "$packages" | grep -E '<|>')"
    if [ -n "$packages" ]; then
        echo "$(echo "$packages" | wc -l) packages do not match with PaiSetup"
        echo $packages
    fi
else
    echo "Could not gather PaiSetup packages"
fi
