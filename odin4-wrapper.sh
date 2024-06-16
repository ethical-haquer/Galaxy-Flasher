#!/bin/bash

# Interactive Odin4 - An interactive wrapper for Odin4
# Copyright (C) 2024 ethical_haquer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Aside from the prompt (">> ") and entered commands,
# anything not colored is output coming from Odin4.

BASEDIR=$(dirname $0)

odin4_exec="$BASEDIR/flash-tools/odin4/linux/x86_64/odin4"

end="\033[0m"
green="\033[38;2;38;162;105m"
yellow="\033[38;2;233;173;12m"
cyan="\033[38;2;51;199;222m"
orange="\033[38;2;233;173;12m"

# If UMS really is the same as Userdata, simplify it to just "Userdata file".
flash_help() {
    echo -e "${cyan}flash [args...]    Flash a device${end}"
    echo -e "${green}Valid flash args:${end}"
    echo -e "${cyan}    -b             Bootloader file${end}"
    echo -e "${cyan}    -a             AP file${end}"
    echo -e "${cyan}    -c             CP file${end}"
    echo -e "${cyan}    -s             CSC file${end}"
    echo -e "${cyan}    -u             UMS (Userdata) file${end}"
    echo -e "${cyan}    -d             Set a device path (detects automatically otherwise)${end}"
    echo -e "${cyan}    -V             Validate home binary with pit file${end}"
}

echo -e "${green}Welcome to Interactive Odin4!${end}"
echo -e "${green}Type \"help\" to view available commands.${end}"

while IFS=""; read -r -e -d $'\n' -p '>> ' cmd; do 
    history -s "$cmd"

    case $cmd in
        list)
            $odin4_exec -l
            ;;
        help)
            echo -e "${green}Available commands:${end}"
            echo -e "${cyan}exit               Exit this program"
            echo -e "${cyan}help               Display this help${end}"
            echo -e "${cyan}list               List connected devices${end}"
            echo -e "${cyan}reboot             Reboot the device${end}"
            echo -e "${cyan}reboot-download    Reboot the device to Download Mode (typically not working)${end}"
            flash_help
            ;;
        version)
            $odin4_exec -v
            ;;
        license)
            $odin4_exec -w
            ;;
        exit)
            echo -e "${green}Goodbye!${end}"
            exit 0
            ;;
        reboot)
            $odin4_exec --reboot
            ;;
        reboot-download)
            $odin4_exec --redownload
            ;;
        flash*)
            flash_cmd=${cmd#flash }
            if [ "$flash_cmd" = "flash" ]; then
                echo -e "${orange}No args were passed.${end}"
                echo -e "${green}Type 'flash help' to get help.${end}"
            elif [ "$flash_cmd" = "help" ]; then
                flash_help
            else
                eval "$odin4_exec $flash_cmd"
            fi
            ;;
        *)            
            echo -e "${orange}Unknown command. Type 'help' to view available commands.${end}"
            ;;
    esac
done
