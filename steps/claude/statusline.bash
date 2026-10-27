#!/bin/bash
# Claude Code statusline.
# Shows: model (name + medal + effort) · cwd · 5h usage + bar · 7d usage + bar · context + bar
#
# All percentages come straight from the statusline stdin JSON (no external tools), so they
# match what claude.ai shows:
#   Day = rate_limits.five_hour.used_percentage   (the 5-hour rolling plan window)
#   Wk  = rate_limits.seven_day.used_percentage
#   Ctx = context_window.used_percentage
# Requires: jq.

set -o pipefail

BAR_WIDTH=12

input=$(cat)
j() { jq -r "$1 // empty" <<<"$input"; }

model_id=$(j '.model.id')
model_name=$(j '.model.display_name')
effort=$(j '.effort.level')
cwd=$(j '.workspace.current_dir')
ctx_pct=$(j '.context_window.used_percentage');            [ -z "$ctx_pct" ] && ctx_pct=0
day_pct=$(j '.rate_limits.five_hour.used_percentage');     [ -z "$day_pct" ] && day_pct=0
week_pct=$(j '.rate_limits.seven_day.used_percentage');    [ -z "$week_pct" ] && week_pct=0

# ---- medal by model family -----------------------------------------------
case "$model_id" in
  *haiku*)  medal="🥉" ;;   # bronze
  *sonnet*) medal="🥈" ;;   # silver
  *opus*)   medal="🥇" ;;   # gold
  *)        medal="🤖" ;;
esac

# ---- colors ----------------------------------------------------------------
RESET="\033[0m"; DIM="\033[38;5;245m"; WHITE="\033[38;5;255m"; CYAN="\033[38;5;39m"
YELLOW="\033[38;5;220m"; BLUE="\033[38;5;33m"
color_for() { # pct -> green / yellow / red
  awk -v p="$1" 'BEGIN{ if(p<50) print "\033[38;5;82m"; else if(p<80) print "\033[38;5;220m"; else print "\033[38;5;196m" }'
}

# ---- progress bar ----------------------------------------------------------
bar() { # $1 = pct (0-100)
  awk -v p="$1" -v w="$BAR_WIDTH" 'BEGIN{
    if(p>100)p=100; if(p<0)p=0;
    f=int(p/100*w+0.5); e=w-f;
    for(i=0;i<f;i++)printf "\342\226\210";   # █
    for(i=0;i<e;i++)printf "\342\226\221";   # ░
  }'
}

# ---- assemble --------------------------------------------------------------
out="${WHITE}${medal} ${model_name}${RESET}"
[ -n "$effort" ] && out="$out ${DIM}(${effort})${RESET}"

disp_cwd="${cwd/#$HOME/\~}"
[ -n "$disp_cwd" ] && out="$out  ${CYAN}${disp_cwd}${RESET}"

out="$out  ${YELLOW}Day [$(bar "$day_pct")] ${day_pct}%${RESET}"
out="$out  $(color_for "$week_pct")Wk [$(bar "$week_pct")] ${week_pct}%${RESET}"
out="$out  ${BLUE}Ctx [$(bar "$ctx_pct")] ${ctx_pct}%${RESET}"

printf "%b" "$out"
