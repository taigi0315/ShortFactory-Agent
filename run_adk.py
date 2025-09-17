"""
ADK-based ShortFactory Runner
Simple script to run the ADK version of ShortFactory
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run ADK main program
from main_adk import main_adk

if __name__ == "__main__":
    import asyncio
    
    # Check if test mode
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        from main_adk import test_adk_workflow
        print("🧪 Running ADK workflow test...")
        asyncio.run(test_adk_workflow())
    elif len(sys.argv) > 1:
        # Run with subject parameter
        subject = sys.argv[1]
        print(f"🎯 Running ADK with subject: {subject}")
        asyncio.run(main_adk(subject))
    else:
        # Run main ADK application
        asyncio.run(main_adk())
