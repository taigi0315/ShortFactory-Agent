#!/usr/bin/env python3
"""
Mock Test Runner for ShortFactory Agent
Uses pre-generated test data to avoid API costs
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.mock_adk_agents import MockADKShortFactoryRunner
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def run_mock_test():
    """Run mock test with pre-generated data"""
    print("🧪 Running Mock ADK Test (No API Calls)...")
    
    try:
        # Initialize mock runner
        runner = MockADKShortFactoryRunner()
        
        # Test subject
        subject = "What is K-pop?"
        
        print(f"📝 Testing with subject: {subject}")
        print("💰 No API costs - using pre-generated test data!")
        
        # Create video using mock agents
        result = await runner.create_video(
            subject=subject,
            language="English",
            max_scenes=6
        )
        
        if result["success"]:
            print("\n✅ Mock test completed successfully!")
            print(f"📁 Session ID: {result['session_id']}")
            print(f"📝 Script: {result['script'].title}")
            print(f"🖼️  Images: {result['images']['total_images']}")
            print(f"⏱️  Total time: {result['total_time']:.2f} seconds")
            print(f"🤖 Model used: {result['model_used']}")
            
            # Show session directory
            session_path = Path("sessions") / result['session_id']
            print(f"📂 Session directory: {session_path}")
            
            # List generated files
            if session_path.exists():
                print("\n📋 Generated files:")
                for file_path in session_path.rglob("*"):
                    if file_path.is_file():
                        print(f"  - {file_path.relative_to(session_path)}")
        else:
            print(f"\n❌ Mock test failed: {result.get('error', 'Unknown error')}")
        
        # Close runner
        await runner.close()
        
    except Exception as e:
        logger.error(f"Mock test error: {str(e)}")
        print(f"\n❌ Mock test error: {str(e)}")

def main():
    """Main function"""
    print("🚀 ShortFactory Agent - Mock Test Mode")
    print("=" * 50)
    
    # Check if test_output exists
    test_output_path = Path("test_output")
    if not test_output_path.exists():
        print("❌ test_output directory not found!")
        print("Please ensure you have copied test data to test_output/")
        return
    
    # Check required files
    required_files = [
        "test_output/script.json",
        "test_output/images/scene_1.png",
        "test_output/images/scene_2.png"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required test files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return
    
    print("✅ Test data found - proceeding with mock test")
    print()
    
    # Run async test
    asyncio.run(run_mock_test())

if __name__ == "__main__":
    main()
