#!/usr/bin/sh

# Get current state
rhythmbox-client --no-present --no-start --check-running
is_player_running="$?"  # 0 means running
if [ "$is_player_running" = 0 ]; then
    gdbus call                                                                                    \
        --session                                                                                 \
        --dest org.mpris.MediaPlayer2.rhythmbox                                                   \
        --object-path /org/mpris/MediaPlayer2                                                     \
        --method org.freedesktop.DBus.Properties.Get org.mpris.MediaPlayer2.Player PlaybackStatus \
        | grep -q Playing
    is_player_playing="$?"  # 0 means playing
else
    is_player_playing="1"
fi

# Override current state on button
[ "$BUTTON" = "1" ] && {
    if [ "$is_player_playing" = 0 ]; then
        rhythmbox-client --pause >/dev/null 2>&1 &
        is_player_playing=1
        is_player_running=0
    else
        rhythmbox-client --play --shuffle >/dev/null 2>&1 &
        is_player_playing=0
        is_player_running=0
    fi
}
[ "$BUTTON" = "3" ] && {
    pkill rhythmbox
    is_player_playing=1
    is_player_running=1
}

# Print state icon
if [ "$is_player_running" = 0 ]; then
    if [ "$is_player_playing" = 0 ]; then
        printf ""
    else
        printf ""
    fi
else
    printf ""
fi
