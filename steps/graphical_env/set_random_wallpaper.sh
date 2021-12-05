#!/bin/sh

find ~ -name "Wallpapers" -type d | xargs -I{} find "{}" |  shuf -n 1 | xargs nitrogen --set-zoom-fill
