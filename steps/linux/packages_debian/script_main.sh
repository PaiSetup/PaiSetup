#!/bin/sh

case "$1" in
    get_name)
        get_name ;;
    install_package)
        set -e
        install_package ;;
    is_installed)
        set -e
        is_installed ;;
    *)
        echo "ERROR: invalid invocation"
        exit 1 ;;
esac
