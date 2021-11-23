#!/bin/sh

screen=$(xrandr | grep " connected" | cut -d' ' -f1)
brightness=$(xrandr --verbose | grep Brightness | awk '{ print $2 }')
increment=0.08
min_value=0.2
max_value=1.0

case "$1" in
  "0")
    brightness=$(echo "x=$brightness-$increment; if(x<$min_value) {x=$min_value}; x" | bc)
    ;;
  "1")
    brightness=$(echo "x=$brightness+$increment; if(x>$max_value) {x=$max_value}; x" | bc)
    ;;
    *)
    exit 1
    ;;
esac

xrandr --output $screen --brightness $brightness
