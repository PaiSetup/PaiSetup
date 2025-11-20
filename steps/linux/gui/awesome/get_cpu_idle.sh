#!/bin/bash

line_index=-1
while IFS= read -r line; do
    # Skip first 2 lines
    line_index=$((line_index + 1))
    if [ "$line_index" -lt 3 ]; then
        continue
    fi

    # Split fields into positional parameters
    set -- $line
    cpu=$2
    idle=${12}

    # Create CPU string
    if [ "$cpu" = "all" ]; then
        cpu="All"
    else
        cpu="Cpu$cpu"
    fi

    # Compute non-idle CPU time (TODO merge this to one bc process)
    nonidle=$(printf "%.2f" "$idle")

    # Output the line
    echo "$cpu $nonidle"
done < <(mpstat -P ALL)
