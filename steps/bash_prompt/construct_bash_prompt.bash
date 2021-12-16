#!/bin/bash

# https://misc.flogisoft.com/bash/tip_colors_and_formatting
# \u - username
# \H - hostname
# \w - working directory
# \$ - prompt char

construct_bash_prompt() {
    is_fancy="$(tty | grep -qv /dev/tty ; echo $?)"

    colorfg() {
        echo -ne "\[\e[38;5;$1m\]"
    }

    colorbg() {
        #echo -e "\e[48;5;$1m"
        echo -ne "\[\e[48;5;$1m\]"
    }

    resetfg() {
        echo -ne "\[\e[0m\]"
    }

    triangle() {
        if [ "$is_fancy" = "0" ]; then
            echo -ne "\uE0B0"
        fi
    }

    section() {
        bg="$1"
        next_bg="$2"
        content="$3"

        colorbg $bg
        echo -n " $content "
        if [ -n "$next_bg" ]; then
            colorbg $next_bg
        else
            resetfg
        fi
        colorfg $bg
        triangle
        resetfg
    }

    if [ "$is_fancy" = "0" ]; then
        bg1=23
        bg2=29
    else
        bg1=4
        bg2=6
    fi
    bg3=0

    user_section="$(section $bg1 $bg2 "$(whoami)")"
    
    git_branch="$(git branch --show-current 2>/dev/null)"
    if [ -z "$git_branch" ]; then
        cwd_section="$(section $bg2 "" "$(dirs +0)")"
        git_section=""
    else
        cwd_section="$(section $bg2 $bg3 "$(dirs +0)")"
        git_section="$(section $bg3 "" $git_branch)"
    fi

    PS1="$user_section$cwd_section$git_section \$ "
}

PROMPT_COMMAND="construct_bash_prompt"
