#!/bin/bash

set -e

FSO_DIR="/opt/fso-agent"
VENV_DIR="$FSO_DIR/.venv"
SERVICE_FILE="/etc/systemd/system/fso-agent.service"

# Ensure the script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root." >&2
    exit 1
fi

echo "Installing FSO-Agent..."

# Create the directory if it doesn't exist
if [ ! -d "$FSO_DIR" ]; then
    mkdir -p "$FSO_DIR"
    echo "Created directory $FSO_DIR"
fi

# Copy project files to the target directory
cp -r . "$FSO_DIR"
echo "Copied project files to $FSO_DIR"

# Set permissions for the directory
chmod -R 755 "$FSO_DIR"
echo "Set permissions for $FSO_DIR"

# Create a virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment and install Poetry and dependencies
echo "Installing dependencies using Poetry..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install poetry
poetry install --no-dev
deactivate

echo "Dependencies installed."

# Create a systemd service file
echo "Creating systemd service file..."
cat <<EOF >"$SERVICE_FILE"
[Unit]
Description=FSO Agent Service
After=network.target

[Service]
Type=simple
ExecStart=$VENV_DIR/bin/python $FSO_DIR/agent.py
Restart=always
RestartSec=5
WorkingDirectory=$FSO_DIR
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

# Set permissions for the service file
chmod 644 "$SERVICE_FILE"
echo "Created service file at $SERVICE_FILE"

# Reload systemd, enable, and start the service
echo "Enabling and starting FSO-Agent service..."
systemctl daemon-reload
systemctl enable fso-agent
systemctl start fso-agent

echo "FSO-Agent installation completed successfully."
