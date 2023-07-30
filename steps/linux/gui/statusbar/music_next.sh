#!/usr/bin/sh

[ -n "$1" ] && BUTTON="$1"
if [ "$BUTTON" = "$BUTTON_ACTION" ]; then    $PAI_SETUP_ROOT/steps/linux/gui/access_rhythmbox.sh 2 1 ; fi
if [ "$BUTTON" = "$BUTTON_INFO" ]; then      $PAI_SETUP_ROOT/steps/linux/gui/access_rhythmbox.sh 5 1 ; fi
if [ "$BUTTON" = "$BUTTON_TERMINATE" ]; then $PAI_SETUP_ROOT/steps/linux/gui/access_rhythmbox.sh 4 1 ; fi
printf ""
