[ "$BUTTON" = "1" ] && notify-send "🧠 Memory hogs" "$(ps axch -o cmd:15,%mem --sort=-%mem | head)"

#free -h | awk '/^Mem/ { print $3"/"$2 }' | sed s/i//g
free | awk 'NR == 2 {printf("%.2f%% of "), $3/$2*100}'
free -h | awk 'NR == 2 {printf ($2)}'
