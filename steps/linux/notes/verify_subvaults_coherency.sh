#!/bin/bash

perform_copy="${1:-0}"

meaningful_files=(
    .obsidian/app.json
    .obsidian/appearance.json
    .obsidian/community-plugins.json
    .obsidian/core-plugins.json
    .obsidian/hotkeys.json
    .gitignore
)

result=0
while read -r sub_vault; do
    # Skip empty directories
    if ! find "$sub_vault" -mindepth 1 -print -quit | grep -q .; then
        continue
    fi

    sub_valut_name="${sub_vault##*/}"

    # Perform the action on all files that we care about: either copy from parent vault
    # or complain that they are different.
    for file in "${meaningful_files[@]}"; do
        if [ "$perform_copy" = "1" ]; then
            cp "$NOTES_PATH/$file" "$sub_vault/$file"
        else
            if ! cmp -s "$sub_vault/$file" "$NOTES_PATH/$file"; then
                echo "$sub_valut_name/$file doesn't match parent vault"
                result=1
            fi
        fi
    done
done <<< "$(find $NOTES_PATH -maxdepth 1 -type d -name "_*")"

exit $result
