#!/bin/bash

# Parse options (supports -q and --query)
query=false
query_debug=false
for arg in "$@"; do
    case "$arg" in
        --query) query=true ;;
        --query-debug) query_debug=true ;;
        *) echo "Usage: $0 [--query]" >&2; exit 1 ;;
    esac
done

# Prepare basic values
src_path="$HOME/multimedia"
dst_path="pc:multimedia"

# Prepare exclude string
encrypted_dirs=(climbing freestyle_football funny) # keep this in snc with mount_multimedia.sh
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

# Execute
if [ "$query_debug" = true ]; then
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
  sleep 2
elif [ "$query" = true ]; then
    rclone sync "$src_path" "$dst_path" --exclude="$exclude" --delete-excluded --track-renames --dry-run --use-json-log 2>&1 | jq -s '
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
else
    rclone sync "$src_path" "$dst_path" --exclude="$exclude" --delete-excluded --track-renames --immutable --verbose
fi
