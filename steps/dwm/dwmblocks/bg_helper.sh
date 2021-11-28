#!/usr/bin/sh

col_barstart="\x04"
col_status1="\x05"
col_status2="\x06"

if [ "$2" = "1" ]; then
    a="$col_status1"
    b="$col_status2"
else
    a="$col_status2"
    b="$col_status1"
fi

case "$1" in
    "barstart") printf "$col_barstart\UE0B2$b" ;;
	"start") printf "$a\uE0B2$b " ;;
    "end") printf " $a" ;;
    "barend") printf " " ;;
esac
