#!/bin/sh

actual_files="$(mktemp)"
expected_files="$(mktemp)"

find ~ -maxdepth 1 -mindepth 1 -printf "%f\n" | sort > "$actual_files"
sort < "$LINUX_SETUP_ROOT/steps/home_directory/homedir_whitelist" > "$expected_files"

extra_files="$(diff "$actual_files" "$expected_files" | grep "^<" | sed "s/^< //g")"
if [ -n "$extra_files" ]; then
    count="$(echo "$extra_files" | wc -l)"
    echo "$count unexpected files found in ~"
    echo "$extra_files"
fi
