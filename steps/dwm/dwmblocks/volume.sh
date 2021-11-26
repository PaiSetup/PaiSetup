#!/bin/sh

volume=$(amixer get Master | grep -E "[0-9]+%" -o | sed 's/%//g' | head -1 | tr -d '\n')
is_enabled=$(amixer get Master | grep -c "\[on\]")
[ "$volume" = 0 ] || [ "$is_enabled" = 0 ] && icon="🔈" || icon="🔊"

printf "$icon %3s%%" $volume
