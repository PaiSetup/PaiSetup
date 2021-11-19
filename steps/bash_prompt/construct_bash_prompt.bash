#!/bin/bash

# https://misc.flogisoft.com/bash/tip_colors_and_formatting
# \u - username
# \H - hostname
# \w - working directory
# \$ - prompt char

construct_bash_prompt() {
    colorfg() {
        echo -e "\[\e[38;5;$1m\]"
    }

    colorbg() {
        #echo -e "\e[48;5;$1m"
        echo -e "\[\e[48;5;$1m\]"
    }

    resetfg() {
        echo -e "\[\e[0m\]"
    }

    triangle() {
        echo -e "\uE0B0"
    }

    section() {
        bg="$1"
        next_bg="$2"
        content="$3"

        echo -n "$(colorbg $bg) $content $(colorfg $bg)$(colorbg $next_bg)$(triangle)$(resetfg)"
    }

    bg1=23
    bg2=29
    bg3=72
    bg4=27

    user_section="$(section $bg1 $bg2 "$(whoami)")"
    host_section="$(section $bg2 $bg3 $HOSTNAME)"
    
    git_branch="$(git branch 2>/dev/null | grep \* | cut -d' ' -f2)"
    if [ -z "$git_branch" ]; then
        cwd_section="$(section $bg3 0 "$(pwd)")"
        git_section=""
    else
        cwd_section="$(section $bg3 $bg4 "$(pwd)")"
        git_section="$(section $bg4 0 $git_branch)"
    fi

    PS1="$user_section$host_section$cwd_section$git_section \$ "
}

PROMPT_COMMAND="construct_bash_prompt"
