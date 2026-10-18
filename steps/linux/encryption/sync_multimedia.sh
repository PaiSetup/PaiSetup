#!/bin/bash

# Parse options
command="$1"

# Prepare basic values
local_path="$HOME/multimedia"
remote_path="pc:multimedia"

# Prepare exclude string
encrypted_dirs=(climbing freestyle_football funny holidays presentations receipts) # keep this in sync with mount_multimedia.sh
not_synced_dirs=(music_to_rate movies tv_series .debris)
not_synced_files=(.megaignore)
exclude=""
for dir in "${encrypted_dirs[@]}" "${not_synced_dirs[@]}"; do
    exclude+="${exclude:+,}${dir}/**"
done
for file in "${not_synced_files[@]}"; do
    exclude+=",${file}"
done
exclude="{${exclude}}"

case "$command" in
    "query_debug")
echo '[
  {
    "caption": " Copies",
    "count": 5,
    "sizeMb": 123
  },
  {
    "caption": " Moves",
    "count": 0,
    "sizeMb": 0
  },
  {
    "caption": " Deletes",
    "count": 2,
    "sizeMb": 100
  }
]'
      ;;

    "query_raw")
        rclone sync "$local_path" "$remote_path" --exclude="$exclude" --fast-list --track-renames --dry-run --use-json-log 2>&1
        ;;

    "query")
        rclone sync "$local_path" "$remote_path" --exclude="$exclude" --fast-list --track-renames --dry-run --use-json-log 2>&1 | jq -s '
            def mb: . / 1048576 * 100 | round / 100;
            def summarize($caption; f):
              [.[] | select(.skipped != null and f)]
              | {caption: $caption, count: length, sizeMb: (map(.size) | add // 0 | mb)};

            [
                summarize(" Copies";  .skipped == "copy"),
                summarize(" Moves";   .skipped | startswith("move")),
                summarize(" Deletes"; .skipped == "delete")
            ]
      '
      ;;

    "download")
        rclone sync "$remote_path" "$local_path" --exclude="$exclude" --fast-list --track-renames --immutable --verbose
        ;;

    "upload")
        rclone sync "$local_path" "$remote_path" --exclude="$exclude" --fast-list --track-renames --immutable --verbose
        ;;

    *)
        echo "Unknown command: '$command'" >&2
        echo "Usage: $0 {download|upload|query|query_raw|query_debug}" >&2
        exit 1
        ;;
esac
