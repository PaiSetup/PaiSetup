#!/bin/sh

# Our color palette
COLOR_THEME="$(xrdb -get color1 | tr -d '#')"
COLOR_GRAY_LIGHT="$(xrdb -get color2 | tr -d '#')"
COLOR_GRAY_DARK="$(xrdb -get color3 | tr -d '#')"
COLOR_FONT="$(xrdb -get color4 | tr -d '#')"
COLOR_WTF=FFFF00

# Oomox variables
oomox_config="$(mktemp -u)"
cat << HEREDOC > $oomox_config
NAME=PaiSetupWidgetTheme
BG=$COLOR_THEME
BTN_BG=$COLOR_GRAY_DARK
BTN_FG=$COLOR_FONT
FG=$COLOR_FONT
GRADIENT=0.0
HDR_BTN_BG=$COLOR_WTF
HDR_BTN_FG=$COLOR_WTF
HDR_BG=$COLOR_THEME
HDR_FG=$COLOR_FONT
ROUNDNESS=4
SEL_BG=$COLOR_GRAY_LIGHT
SEL_FG=$COLOR_FONT
SPACING=3
TXT_BG=$COLOR_GRAY_DARK
TXT_FG=$COLOR_FONT
WM_BORDER_FOCUS=$COLOR_WTF
WM_BORDER_UNFOCUS=$COLOR_WTF
HEREDOC

oomox-cli -o PaiSetupWidgetTheme "$oomox_config"
rm "$oomox_config"
