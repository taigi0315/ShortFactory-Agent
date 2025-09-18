"""
Test the improved prompts specifically for Texas subject

This script tests the enhanced prompts to ensure AI creates Texas-specific content.
"""

import os
import asyncio
import logging
import sys
sys.path.append('../src')

from agents.adk_script_writer_agent import ADKScriptWriterAgent
from core.shared_context import SharedContextManager

async def test_texas_prompts():
    """Test the improved prompts for Texas subject"""
    print("🚀 Testing Texas-Specific Prompts")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        return
    
    print("✅ API key found - proceeding with test")
    
    try:
        # Initialize
        print("\n🔧 Initializing components...")
        shared_context_manager = SharedContextManager()
        script_writer = ADKScriptWriterAgent(shared_context_manager)
        
        # Test Texas subject
        subject = "Texas"
        print(f"\n📝 Testing with subject: {subject}")
        print("🎯 Focus: Texas-specific story generation")
        
        # Generate story script
        print("\n📖 Generating story script...")
        story_script = await script_writer.generate_story_script(subject)
        
        print(f"✅ Story generated: {story_script.title}")
        print(f"📚 Overall story: {story_script.overall_story}")
        print(f"🎬 Scene plan: {len(story_script.scene_plan)} scenes")
        
        # Check if the story is actually about Texas
        if "texas" in story_script.title.lower() or "texas" in story_script.overall_story.lower():
            print("✅ Story is correctly about Texas!")
        else:
            print("❌ Story is NOT about Texas - prompt failed!")
            print(f"Title: {story_script.title}")
            print(f"Story: {story_script.overall_story}")
        
        # Show scene plan details
        print("\n📋 Scene Plan Details:")
        for scene in story_script.scene_plan:
            print(f"  Scene {scene.scene_number} ({scene.scene_type.value}):")
            print(f"    Purpose: {scene.scene_purpose}")
            print(f"    Content: {scene.key_content}")
            print(f"    Focus: {scene.scene_focus}")
        
        print("\n✅ Texas prompt test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_texas_prompts())
