#!/usr/bin/sh

# Get arguments
module_index="$1"
module_count="$2"
submodule_index="$3"
submodule_count="$4"
module_name="$5"

# Prepare color indices
col_barstart="\x04"
col_status1="\x05"
col_status2="\x06"
if [ "$((module_index % 2))" = "1" ]; then
    a="$col_status1"
    b="$col_status2"
else
    a="$col_status2"
    b="$col_status1"
fi

# Module beginning
if [ "$submodule_index" = 0 ]; then
    if [ "$module_index" = 0 ]; then
        printf "$col_barstart\UE0B2$b"
    else
        printf "$a\uE0B2$b "
    fi
else
    printf " "
fi

# Module content
$LINUX_SETUP_ROOT/steps/gui/statusbar/$module_name

# Module ending
if [ "$submodule_index" = "$((submodule_count - 1))" ]; then
    if [ "$module_index" = "$((module_count - 1))" ]; then
        printf " "
    else
        printf " $a"
    fi
fi
