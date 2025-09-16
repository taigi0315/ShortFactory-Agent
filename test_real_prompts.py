#!/usr/bin/env python3
"""
Test real ADK agents with new educational prompts
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main_adk import main_adk
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_real_prompts():
    """Test real ADK agents with new educational prompts"""
    print("🧪 Testing Real ADK Agents with New Educational Prompts...")
    
    try:
        # Test with different subject
        subject = "How does Machine Learning work?"
        
        print(f"📝 Testing with subject: {subject}")
        print("🎯 Focus: Educational content with character as guide")
        print("💰 This will use real API calls!")
        
        # Create video using real ADK agents
        result = await main_adk(subject=subject)
        
        if result["success"]:
            print("\n✅ Test completed successfully!")
            print(f"📁 Session ID: {result['session_id']}")
            print(f"📝 Script: {result['script'].title}")
            
            # Show generated prompts
            session_path = Path("sessions") / result['session_id']
            prompts_path = session_path / "prompts" / "image"
            
            print("\n📋 Generated Educational Prompts:")
            for i in range(1, 7):
                prompt_file = prompts_path / f"scene_{i}.txt"
                if prompt_file.exists():
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        prompt = f.read().strip()
                    print(f"\nScene {i}:")
                    print(f"  {prompt}")
            
            # Show script image prompts
            print("\n📝 Script Image Prompts:")
            for i, scene in enumerate(result['script'].scenes, 1):
                print(f"\nScene {i} ({scene.scene_type}):")
                print(f"  {scene.image_create_prompt}")
        else:
            print(f"\n❌ Test failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        print(f"\n❌ Test error: {str(e)}")

def main():
    """Main function"""
    print("🚀 Testing Real ADK Educational Prompt Generation")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No API key found!")
        print("Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable")
        return
    
    print("✅ API key found - proceeding with real test")
    print()
    
    # Run async test
    asyncio.run(test_real_prompts())

if __name__ == "__main__":
    main()
