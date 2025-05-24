#!/bin/bash
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
pushd frontend >/dev/null
npm install
popd >/dev/null

# Make test scripts executable (optional)
./setup_test_scripts.sh

echo "Setup complete. Activate the virtual environment with 'source venv/bin/activate'."
