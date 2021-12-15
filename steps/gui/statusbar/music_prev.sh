#!/usr/bin/sh

[ "$BUTTON" = "1" ] && {
    (rhythmbox-client --play ; rhythmbox-client --seek 1 ; rhythmbox-client --previous ; pkill -RTMIN+18 dwmblocks) >/dev/null 2>&1 &
}

printf ""
