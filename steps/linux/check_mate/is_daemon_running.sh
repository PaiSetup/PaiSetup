#!/bin/sh

# Format for each input line is as follows:
#  - last word is a human-readable name to be displayed in the notification
#  - the rest (before the last space) is a regex for command called
execute() {
    IFS='
'
    while read -r daemon; do
        daemon_name="${daemon##* }"
        daemon_regex="${daemon% *}"
        daemon_regex="${daemon_regex#"${daemon_regex%%[![:space:]]*}"}" # Strip whitespace
        count=$(ps -x -o pid= -o cmd= | grep -Ec "^\s*[0-9]+ $daemon_regex")
        if [ "$count" = 0 ]; then echo "$daemon_name is not running"; fi
        if [ "$count" -gt 1 ]; then echo "$count instances of $daemon_name are running"; fi
    done
}

if [ "$#" -gt 0 ]; then
    echo "$@" | execute
else
    execute
fi
