#!/bin/sh

df --output=target,source,avail,size | grep -vE "^(Mounted|/dev|/tmp|/efi|/sys|/run |/run/credentials|/run/user)"
