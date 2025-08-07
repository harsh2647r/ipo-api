#!/bin/bash

# Exit on error
set -e

# Install python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install --with-deps
