#!/bin/bash
if ! command -v flatpak-builder &> /dev/null; then
  echo "You need to install flatpak-builder to use this script."
  exit 1
fi
echo "Compiling resources.gresource..."
glib-compile-resources ./resources.gresource.xml --target=resources.gresource
# Create include dir.
mkdir include
cp -r ../locales ../flash_tool_plugins ../odin4-wrapper.sh ../usb.ids ./icons/page.codeberg.ethicalhaquer.galaxyflasher.svg ./resources.gresource include
# Build it.
flatpak-builder --user --install --force-clean build page.codeberg.ethicalhaquer.galaxyflasher.yml
rm -r include
rm resources.gresource
