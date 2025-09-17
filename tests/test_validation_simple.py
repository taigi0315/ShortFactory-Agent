"""
Test the validation system with simple mock data
"""

import os
import asyncio
import logging
import sys
sys.path.append('../src')

from agents.adk_script_validator_agent import ADKScriptValidatorAgent
from core.shared_context import SharedContextManager
from model.models import StoryScript, ScenePlan, SceneType

async def test_validation_simple():
    """Test validation with simple mock data"""
    print("🚀 Testing Validation System")
    print("=" * 30)
    
    try:
        # Initialize
        shared_context_manager = SharedContextManager()
        script_validator = ADKScriptValidatorAgent(shared_context_manager)
        
        # Test GOOD story (should pass)
        print("\n📖 Testing GOOD story...")
        good_story = StoryScript(
            title="The 3 AM Meeting: How Elon Musk Saved Tesla",
            main_character_description="Huh - a cute, blob-like cartoon character",
            character_cosplay_instructions="Dress Huh as Elon Musk",
            overall_style="educational",
            overall_story="The specific moment when Elon Musk made a 3 AM phone call to Larry Page in 2008, securing $50 million investment that saved Tesla from bankruptcy",
            story_summary="A detailed account of the critical 3 AM meeting where Elon Musk secured funding to save Tesla",
            scene_plan=[
                ScenePlan(
                    scene_number=1,
                    scene_type=SceneType.HOOK,
                    scene_purpose="Grab attention with the 3 AM crisis",
                    key_content="Tesla was 3 days away from bankruptcy in October 2008, with only $9 million left",
                    scene_focus="The desperate situation and time pressure"
                )
            ]
        )
        
        result = await script_validator.validate_story_script(good_story)
        print(f"✅ Good story result: {result.status.value} (score: {result.overall_score:.2f})")
        
        # Test BAD story (should fail)
        print("\n📖 Testing BAD story...")
        bad_story = StoryScript(
            title="Understanding Tesla",
            main_character_description="Huh - a cute, blob-like cartoon character",
            character_cosplay_instructions="Dress Huh as a car expert",
            overall_style="educational",
            overall_story="Let me explain what Tesla is and how it works. It's fascinating how electric cars have changed the world.",
            story_summary="A comprehensive overview of Tesla and electric vehicles",
            scene_plan=[
                ScenePlan(
                    scene_number=1,
                    scene_type=SceneType.HOOK,
                    scene_purpose="Introduce the topic",
                    key_content="Tesla is a company that makes electric cars",
                    scene_focus="Basic introduction to Tesla"
                )
            ]
        )
        
        result = await script_validator.validate_story_script(bad_story)
        print(f"❌ Bad story result: {result.status.value} (score: {result.overall_score:.2f})")
        print(f"   Issues: {len(result.issues)}")
        
        print("\n✅ Validation test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_validation_simple())
