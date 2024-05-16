#!/bin/bash

# An interactive wrapper for Odin4, made for Galaxy Flasher.
# Eventually it may be it's own project.
# Odin4 Wrapper is a terrible name, any ideas?

# Aside from the prompt (">> ") and entered commands,
# anything white is output coming from odin4.

BASEDIR=$(dirname $0)

odin4_exec="$BASEDIR/flash-tools/odin4/linux/x64/odin4"

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

echo -e "${green}Welcome to Odin4 Wrapper!${end}"
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
            echo -e "${green}Odin4 Wrapper Version 0.0.0${end}"
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
                $odin4_exec $flash_cmd
            fi
            ;;
        *)            
            echo -e "${orange}Unknown command. Type 'help' to view available commands.${end}"
            ;;
    esac
done
