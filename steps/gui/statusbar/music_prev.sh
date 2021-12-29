#!/usr/bin/sh

if [ "$BUTTON" = "$BUTTON_ACTION" ]; then    $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 3 1 ; fi
if [ "$BUTTON" = "$BUTTON_INFO" ]; then      $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 5 1 ; fi
if [ "$BUTTON" = "$BUTTON_TERMINATE" ]; then $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh 4 1 ; fi
printf ""
