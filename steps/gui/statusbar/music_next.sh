#!/usr/bin/sh

[ "$BUTTON" = "1" ] && $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 2 1
[ "$BUTTON" = "2" ] && $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 5 1
[ "$BUTTON" = "3" ] && $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 4 1
printf ""
