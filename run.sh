#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 device_finder.py
deactivate
