#!/bin/sh

fetch="$1"
if [ -z "$fetch" ]; then
    fetch=0
fi

report_git() {
    path="$1"
    flags=""

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
        master_branch="?"
    fi

    # Check for uncomitted changes
    if [ -n "$(git status --porcelain)" ]; then
        flags="$flags uncomitted"
    fi

    if [ "$master_branch" != "?" ]; then
        # Check for unpushed commits
        if ! git merge-base --is-ancestor $master_branch origin/$master_branch; then
            flags="$flags unpushed"
        fi

        # Check for unpulled commits
        if ! git merge-base --is-ancestor origin/$master_branch $master_branch; then
            flags="$flags unpulled"
        fi
    fi

    # Return results
    echo "git $path $master_branch$flags"
}

report_nogit() {
    flags=""

    flags="$flags no-git-repo"

    if [ "$(find . -maxdepth 0 -type d -empty | wc -l)" != 0 ]; then
        flags="$flags empty"
    fi

    echo "nogit $path $flags"
}

IFS="
"
for path in $(find $LINUX_SETUP_ROOT $SCRIPTS_PATH/.. $NOTES_PATH $PROJECT_DIR/* -maxdepth 0 -type d); do
    # Go to repo
    cd "$path" || continue
    path="$(realpath "$path")"
    path="$(echo "$path" | sed "s/\/home\/$USER/~/g")"

    if [ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" = "true" ]; then
        report_git "$path"
    else
        report_nogit "$path"
    fi
done
