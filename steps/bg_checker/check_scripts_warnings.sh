#!/bin/sh
. ~/.profile # for scc command

warnings="$(scc | grep -E " SC[0-9]+")"
if [ -n "$warnings" ]; then
    echo "$(echo "$warnings" | wc -l) shell script warnings detected"
fi
