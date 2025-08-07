#!/usr/bin/env bash

# Activate the virtual environment (created by Render)
source .venv/bin/activate

# Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install --with-deps
