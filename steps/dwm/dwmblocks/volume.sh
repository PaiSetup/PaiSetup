volume=$(amixer get Master | grep -E "[0-9]+%" -o | sed 's/%//g' | head -1 | tr -d '\n')
is_enabled=$(amixer get Master | grep "\[on\]" | wc -l)
[ "$volume" = 0 -o "$is_enabled" = 0 ] && icon="🔈" || icon="🔊"

printf "$icon $volume%%"
