#!/bin/bash

# Function to check if a command is available
check_for_command() {
  if ! command -v "$1" &> /dev/null; then
    echo "You need to install $1 to use this script."
    exit 1
  fi
}

# Check if the required commands are available
check_for_command "flatpak"
check_for_command "glib-compile-resources"
check_for_command "flatpak-builder"

echo "INFO: Installing org.gnome.Sdk//47 and org.gnome.Platform//47, if needed."
flatpak install flathub org.gnome.Sdk//47 org.gnome.Platform//47

echo "INFO: Compiling resources.gresource."
glib-compile-resources ./resources.gresource.xml --target=resources.gresource

echo "INFO: Creating desktop file."
appstreamcli make-desktop-file page.codeberg.ethicalhaquer.galaxyflasher.metainfo.xml page.codeberg.ethicalhaquer.galaxyflasher.desktop

sudo cp galaxy-flasher.sh ~/.local/bin/
sudo cp page.codeberg.ethicalhaquer.galaxyflasher.desktop ~/.local/share/applications/

echo "INFO: Cleaning up."
rm resources.gresource

