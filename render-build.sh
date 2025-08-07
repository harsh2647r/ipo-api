#!/usr/bin/env bash
# This script runs during Render's build process

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install --with-deps

# Proceed with rest of setup (if any)
