#!/bin/sh

free  | awk 'NR == 2 { print $3, $2 }' | sed -E "s/([0-9]+) /scale=2; 100 * \1\//g" | bc | sed "s/^\./0./g"
