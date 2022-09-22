#!/bin/sh

cpu_idle="$(top -b -n 1 | grep Cpu | grep -oE "[0-9.]+ id" | cut -d' ' -f1)"
echo "100 - $cpu_idle" | bc | sed "s/^\./0\./g"
