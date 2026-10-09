#!/bin/sh

fetch="$1"
if [ -z "$fetch" ]; then
    fetch=0
fi

json_escape() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

# Prints one JSON object. Arguments: path vcs main_branch current_branch labels (space-separated)
print_repo() {
    path="$(json_escape "$1")"
    vcs="$2"
    main_branch="$(json_escape "$3")"
    current_branch="$(json_escape "$4")"

    labels_json=""
    old_ifs="$IFS"
    IFS=' '
    for label in $5; do
        labels_json="$labels_json${labels_json:+, }\"$label\""
    done
    IFS="$old_ifs"

    if [ "$first" = 1 ]; then first=0; else printf ',\n'; fi
    printf '  {"path": "%s", "vcs": "%s", "main_branch": "%s", "current_branch": "%s", "labels": [%s]}' \
        "$path" "$vcs" "$main_branch" "$current_branch" "$labels_json"
}

report_git() {
    path="$1"
    labels=""

    if [ "$fetch" != 0 ]; then
        echo "Fetching $path..." >&2
        git fetch >&2
    fi

    if git rev-parse master >/dev/null 2>&1; then
        main_branch="master"
    elif git rev-parse main >/dev/null 2>&1; then
        main_branch="main"
    else
        main_branch=""   # unknown
    fi

    current_branch="$(git branch --show-current)"
    if [ -z "$current_branch" ]; then
        current_branch="DETACHED"
    fi

    if [ -n "$(git status --porcelain)" ]; then
        labels="$labels uncommitted"
    fi

    if [ "$current_branch" != "DETACHED" ]; then
        if ! git merge-base --is-ancestor "$current_branch" "origin/$current_branch" 2>/dev/null; then
            labels="$labels unpushed"
        fi
        if ! git merge-base --is-ancestor "origin/$current_branch" "$current_branch" 2>/dev/null; then
            labels="$labels unpulled"
        fi
    fi

    print_repo "$path" "git" "$main_branch" "$current_branch" "$labels"
}

report_nogit() {
    path="$1"
    labels="no-git-repo"

    if [ "$(find . -maxdepth 0 -type d -empty | wc -l)" != 0 ]; then
        labels="$labels empty"
    fi

    print_repo "$path" "none" "" "" "$labels"
}

first=1
echo "["
IFS="
"
for path in $(find $PAI_SETUP_ROOT $DUSH_PATH $NOTES_PATH $PROJECT_DIR/* -maxdepth 0 -type d); do
    cd "$path" || continue
    path="$(realpath "$path")"
    path="$(echo "$path" | sed "s/\/home\/$USER/~/g")"

    if [ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" = "true" ]; then
        report_git "$path"
    else
        report_nogit "$path"
    fi
done
printf '\n]\n'
