#!/usr/bin/env python3
"""
Automated test script for ShortFactory-Agent
Tests the complete workflow without user input
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_auto():
    """Run automated test with predefined subject"""
    try:
        # Import main function
        from main import main
        
        # Test subject
        subject = "What is all about K-pop demon hunters?"
        
        print(f"🚀 Starting automated test with subject: '{subject}'")
        print("=" * 60)
        
        # Run main function
        main(subject)
        
        print("=" * 60)
        print("✅ Automated test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_auto()
    sys.exit(0 if success else 1)
