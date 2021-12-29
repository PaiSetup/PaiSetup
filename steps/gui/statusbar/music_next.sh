#!/usr/bin/sh

[ "$BUTTON" = "$BUTTON_ACTION" ]    && $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 2 1
[ "$BUTTON" = "$BUTTON_INFO" ]      && $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 5 1
[ "$BUTTON" = "$BUTTON_TERMINATE" ] && $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 4 1
printf ""
