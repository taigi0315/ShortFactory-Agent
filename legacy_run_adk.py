"""
ADK-based ShortFactory Runner
Simple script to run the ADK version of ShortFactory
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run ADK main program
from main_adk import main_adk

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='ADK-based ShortFactory Runner')
    parser.add_argument('subject', nargs='?', help='Subject for the video (e.g., "Space Exploration")')
    parser.add_argument('--cost', action='store_true', help='Use cost-saving mode (mock images instead of AI generation)')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    
    return parser.parse_args()

if __name__ == "__main__":
    import asyncio
    
    args = parse_arguments()
    
    # Check if test mode
    if args.test:
        from main_adk import test_adk_workflow
        print("🧪 Running ADK workflow test...")
        asyncio.run(test_adk_workflow())
    elif args.subject:
        # Run with subject parameter
        print(f"🎯 Running ADK with subject: {args.subject}")
        if args.cost:
            print("💰 Cost-saving mode enabled - using mock images")
        asyncio.run(main_adk(args.subject, cost_saving_mode=args.cost))
    else:
        # Run main ADK application
        if args.cost:
            print("💰 Cost-saving mode enabled - using mock images")
        asyncio.run(main_adk(cost_saving_mode=args.cost))
