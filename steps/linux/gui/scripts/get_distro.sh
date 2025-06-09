#!/bin/sh

. /etc/os-release
case $ID in
    arch)
        echo arch
        exit 0
        ;;
    debian|ubuntu|mint)
        echo debian
        exit 0
        ;;
    *)
        echo unknown
        exit 1
        ;;
esac

