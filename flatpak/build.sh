#!/bin/bash
if ! command -v flatpak-builder &> /dev/null; then
  echo "You need to install flatpak-builder to use this script."
  exit 1
fi
# Create include dir.
mkdir include
cp -r ../locales ../odin4-wrapper.sh ../usb.ids ../icons/com.ethicalhaquer.galaxyflasher.svg include
# Build it.
flatpak-builder --user --install --force-clean build com.ethicalhaquer.galaxyflasher.yml
rm -r include
