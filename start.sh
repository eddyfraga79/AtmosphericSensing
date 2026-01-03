#!/bin/bash
# start.sh — Run your Python app inside the virtual environment

# Exit immediately if a command fails
set -e

# Go to script's directory
cd "$(~/Projects/AtmosphericSensing "$0")"

# Name of your virtual environment folder
VENV_DIR=".venv"

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"

    echo "[INFO] Activating virtual environment and installing dependencies..."
    source "$VENV_DIR/bin/activate"
    if [ -f "requirements.txt" ]; then
        pip3 install --upgrade pip
        pip3 install -r requirements.txt
    else
        echo "[WARN] requirements.txt not found. Skipping dependency install."
    fi
else
    echo "[INFO] Using existing virtual environment."
    source "$VENV_DIR/bin/activate"
fi

# Run your Python application
echo "[INFO] Starting application..."
python3 main.py >> app.log 2>&1