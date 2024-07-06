#!/bin/sh

df "$1" --output=used,size,pcent -h | tail +2 | awk "{printf(\"%s %s %s %s\n\", \$3, \$2, \$1, \"$1\")}" | tr '%' ' '
