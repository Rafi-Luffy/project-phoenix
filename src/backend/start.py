#!/usr/bin/env python3.11
"""
Backend startup script with proper path configuration
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Now import and run
from main import app
import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Autonomous Self-Healing System Backend")
    print("=" * 70)
    print(f"📁 Working directory: {backend_dir}")
    print(f"🐍 Python path includes: {backend_dir}")
    print("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
