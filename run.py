#!/usr/bin/env python3
"""
ShortFactory Agent - Main Entry Point
AI-powered short video creation system with Huh character
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run main program
from main import main

if __name__ == "__main__":
    main()
