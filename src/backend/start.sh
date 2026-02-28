#!/bin/bash
# Phoenix Chess Demo — Backend Start Script
# Requires Python 3.12+

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting Phoenix backend on http://localhost:8000"
python3.12 -m uvicorn chess_app:app --host 0.0.0.0 --port 8000 --reload
