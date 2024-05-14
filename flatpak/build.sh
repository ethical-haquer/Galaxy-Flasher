#!/bin/bash
if ! command -v flatpak-builder &> /dev/null; then
  echo "You need to install flatpak-builder to use this script."
  exit 1
fi
# Create includes dir
mkdir include
cp -r ../Thor ../locales include
# Build it.
flatpak-builder --user --install --force-clean build com.ethicalhaquer.galaxyflasher.yml
rm -r include
