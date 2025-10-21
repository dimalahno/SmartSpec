#!/bin/bash
set -e

echo "Installing system dependencies..."
apt-get update
apt-get install -y imagemagick libmagickwand-dev
echo "System dependencies installed."