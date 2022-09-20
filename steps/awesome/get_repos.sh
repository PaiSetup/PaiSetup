#!/bin/sh

fetch="$1"
if [ -z "$fetch" ]; then
    fetch=0
fi

IFS="
"
for line in $(find $LINUX_SETUP_ROOT $SCRIPTS_PATH/.. $NOTES_PATH $PROJECT_DIR/* -mindepth 1 -maxdepth 1 -name ".git" -type d); do
    flags=""

    # Go to repo
    path="$(realpath "$line/..")"
    cd "$path"

    # Fetch
    if [ "$fetch" != 0 ]; then
        echo "Fetching $path..." >&2
        git fetch
    fi

    # Get master branch
    if git rev-parse master >/dev/null 2>&1; then
        master_branch="master"
    elif git rev-parse main >/dev/null 2>&1; then
        master_branch="main"
    else
        echo "ERROR: could not get master branch for $path"
        continue
    fi

    # Check for uncomitted changes
    if [ -n "$(git status --porcelain)" ]; then
        flags="$flags uncomitted"
    fi

    # Check for unpushed commits
    if ! git merge-base --is-ancestor $master_branch origin/$master_branch; then
        flags="$flags unpushed"
    fi

    # Check for unpulled commits
    if ! git merge-base --is-ancestor origin/$master_branch $master_branch; then
        flags="$flags unpulled"
    fi

    # Return results
    path="${path/\/home\/$USER\//~\/}"
    echo "$path $master_branch$flags"
done
