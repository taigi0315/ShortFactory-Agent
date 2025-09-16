#!/usr/bin/env python3
"""
Test new prompt generation with different subject
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

async def test_new_prompts():
    """Test new prompt generation with different subject"""
    print("🧪 Testing New Educational Prompts...")
    
    try:
        # Initialize mock runner
        runner = MockADKShortFactoryRunner()
        
        # Test with different subject
        subject = "How does Machine Learning work?"
        
        print(f"📝 Testing with subject: {subject}")
        print("🎯 Focus: Educational content with character as guide")
        
        # Create video using mock agents
        result = await runner.create_video(
            subject=subject,
            language="English",
            max_scenes=6
        )
        
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
        
        # Close runner
        await runner.close()
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        print(f"\n❌ Test error: {str(e)}")

def main():
    """Main function"""
    print("🚀 Testing New Educational Prompt Generation")
    print("=" * 50)
    
    # Run async test
    asyncio.run(test_new_prompts())

if __name__ == "__main__":
    main()
