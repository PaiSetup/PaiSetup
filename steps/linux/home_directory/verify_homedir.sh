#!/bin/sh

actual_files="$(mktemp)"
expected_files="$(mktemp)"

find ~ -maxdepth 1 -mindepth 1 -printf "%f\n" | sort > "$actual_files"
sort < ~/.config/PaiSetup/homedir_whitelist > "$expected_files"

exit_value=0
extra_files="$(diff "$actual_files" "$expected_files" | grep "^<" | sed "s/^< //g")"
if [ -n "$extra_files" ]; then
    count="$(echo "$extra_files" | wc -l)"
    echo "$count unexpected files found in ~"
    echo "$extra_files"
    exit_value=1
fi

rm "$actual_files"
rm "$expected_files"
exit $exit_value
