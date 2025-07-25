#!/bin/bash

set -e

# Absolute path to project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[BUILD] Creating virtual environment..."
python3 -m venv "$PROJECT_DIR/venv"

echo "[BUILD] Activating virtual environment and installing requirements..."
"$PROJECT_DIR/venv/bin/pip" install --upgrade pip
"$PROJECT_DIR/venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

echo "[BUILD] Creating /usr/local/bin/device-finder launcher..."

LAUNCHER_PATH="/usr/local/bin/device-finder"

sudo tee "$LAUNCHER_PATH" > /dev/null <<EOF
#!/bin/bash
DIR="$PROJECT_DIR"
"\$DIR/venv/bin/python3" "\$DIR/device_finder.py"
EOF

sudo chmod +x "$LAUNCHER_PATH"

echo "[BUILD] Done. You can now run 'device-finder' from anywhere."
