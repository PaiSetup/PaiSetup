#!/usr/bin/sh

[ -n "$1" ] && BUTTON="$1"

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
if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    if [ "$is_player_playing" = 0 ]; then
        $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 0 0
        is_player_playing=1
        is_player_running=0
    else
        $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 1 0
        is_player_playing=0
        is_player_running=0
    fi
fi
if [ "$BUTTON" = "$BUTTON_INFO" ]; then
    $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 5 0
fi
if [ "$BUTTON" = "$BUTTON_TERMINATE" ]; then
    $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 4 0
    is_player_playing=1
    is_player_running=1
fi

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
