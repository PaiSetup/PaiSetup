#!/bin/sh

address_to_ping="google.com"
ping $address_to_ping -c 1 >/dev/null 2>/dev/null
if [ "$?" != 0 ] ; then
    echo "Cannot ping $address_to_ping"
    exit 1
fi
