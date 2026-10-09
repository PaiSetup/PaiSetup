#!/bin/sh

df --output=target,source,avail,size \
| grep -vE "^(Mounted|/dev|/tmp|/efi|/sys|/run |/run/credentials|/run/user)" \
| grep -v Cryptomator \
| LC_ALL=C awk '
function esc(s) {
    gsub(/\\/, "\\\\\\\\", s)
    gsub(/"/, "\\\"", s)
    return s
}
BEGIN { printf "["; first = 1 }
{
    avail_gb = $3 / 1024 / 1024
    total_gb = $4 / 1024 / 1024
    used_gb  = total_gb - avail_gb
    if (!first) printf ","
    first = 0
    printf "{\"mount_path\":\"%s\",\"device_path\":\"%s\",\"used_gb\":%.2f,\"avail_gb\":%.2f,\"total_gb\":%.2f}", esc($1), esc($2), used_gb, avail_gb, total_gb
}
END { print "]" }'
