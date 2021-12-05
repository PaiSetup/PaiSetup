#!/bin/sh

while true; do
    mkdir -p ~/.log/
    dwm >/dev/null >~/.log/dwm 2>&1 || break
done
