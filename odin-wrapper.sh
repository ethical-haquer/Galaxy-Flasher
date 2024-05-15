#!/bin/bash

while true; do
    read -p "odin4> " cmd

    case $cmd in
        list)
            ./odin4 -l
            ;;
        help)
            ./odin4 -h
            ;;
        *)
            echo "Unknown command. Type 'help' for available commands."
            ;;
    esac
done
