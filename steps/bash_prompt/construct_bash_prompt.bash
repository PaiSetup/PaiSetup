#!/bin/bash

# https://misc.flogisoft.com/bash/tip_colors_and_formatting
# \u - username
# \H - hostname
# \w - working directory
# \$ - prompt char

construct_bash_prompt() {
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
        echo -ne "\uE0B0"
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

    bg1=23
    bg2=29
    bg3=72
    bg4=27

    user_section="$(section $bg1 $bg2 "$(whoami)")"
    host_section="$(section $bg2 $bg3 $HOSTNAME)"
    
    git_branch="$(git branch --show-current 2>/dev/null)"
    if [ -z "$git_branch" ]; then
        cwd_section="$(section $bg3 "" "$(dirs +0)")"
        git_section=""
    else
        cwd_section="$(section $bg3 $bg4 "$(dirs +0)")"
        git_section="$(section $bg4 "" $git_branch)"
    fi

    PS1="$user_section$host_section$cwd_section$git_section \$ "
}

PROMPT_COMMAND="construct_bash_prompt"
