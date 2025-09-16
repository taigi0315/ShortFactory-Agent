#!/usr/bin/env python3
"""
Test new workflow with Story Writer and Scene Writer agents
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.adk_script_writer_agent import ADKScriptWriterAgent
from agents.adk_scene_writer_agent import ADKSceneWriterAgent
from core.session_manager import SessionManager
from core.shared_context import SharedContextManager, VisualStyle
from core.scene_continuity_manager import SceneContinuityManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_new_workflow():
    """Test new workflow with story and scene writers"""
    print("🧪 Testing New Workflow: Story Writer + Scene Writer...")
    
    try:
    # Initialize managers
    shared_context_manager = SharedContextManager()
    continuity_manager = SceneContinuityManager()
    
    # Initialize agents with shared context and continuity manager
    session_manager = SessionManager()
    story_writer = ADKScriptWriterAgent(shared_context_manager)
    scene_writer = ADKSceneWriterAgent(session_manager, shared_context_manager, continuity_manager)
        
        # Test subject
        subject = "Coca Cola"
        
        print(f"📝 Testing with subject: {subject}")
        print("🎯 Focus: Story development + detailed scene writing")
        
        # Step 1: Generate story script
        print("\n📖 Step 1: Generating story script...")
        story_script = await story_writer.generate_story_script(
            subject=subject, 
            target_audience="general",
            visual_style=VisualStyle.MODERN
        )
        
        print(f"✅ Story generated: {story_script.title}")
        print(f"📚 Overall story: {story_script.overall_story}")
        print(f"📋 Story summary: {story_script.story_summary}")
        print(f"🎬 Scene plan: {len(story_script.scene_plan)} scenes")
        
        # Show scene plan
        print("\n📋 Scene Plan:")
        for scene_plan in story_script.scene_plan:
            print(f"  Scene {scene_plan.scene_number} ({scene_plan.scene_type}):")
            print(f"    Purpose: {scene_plan.scene_purpose}")
            print(f"    Content: {scene_plan.key_content}")
            print(f"    Focus: {scene_plan.scene_focus}")
        
        # Step 2: Generate detailed scene script
        print(f"\n🎬 Step 2: Generating detailed scene script for scene 1...")
        
        # Create full script context for scene writer
        full_context = f"""
Title: {story_script.title}
Overall Story: {story_script.overall_story}
Story Summary: {story_script.story_summary}
Character: {story_script.main_character_description}
Cosplay: {story_script.character_cosplay_instructions}

Scene Plan:
"""
        for scene_plan in story_script.scene_plan:
            full_context += f"- Scene {scene_plan.scene_number}: {scene_plan.scene_purpose}\n"
        
        # Write detailed scene for scene 1
        scene_1_plan = story_script.scene_plan[0]
        # Get shared context for scene writing
        shared_context = shared_context_manager.get_context()
        
        detailed_scene = await scene_writer.write_scene_script(
            scene_number=scene_1_plan.scene_number,
            scene_type=scene_1_plan.scene_type,
            overall_story=story_script.overall_story,
            full_script_context=full_context,
            subject=subject,
            shared_context=shared_context
        )
        
        print(f"✅ Detailed scene generated for scene {detailed_scene['scene_number']}")
        print(f"📝 Dialogue: {detailed_scene['dialogue']}")
        print(f"🎨 Image prompt: {detailed_scene['image_create_prompt']}")
        print(f"🎬 Video prompt: {detailed_scene['video_prompt']}")
        
        # Generate continuity report
        continuity_report = scene_writer.get_continuity_report()
        print(f"\n📊 Continuity Report:")
        print(f"   Overall Score: {continuity_report.get('overall_continuity_score', 0):.2f}")
        print(f"   Total Issues: {continuity_report.get('total_issues', 0)}")
        
        if continuity_report.get('total_issues', 0) > 0:
            print(f"   Issues by Severity: {continuity_report.get('issues_by_severity', {})}")
            recommendations = continuity_report.get('recommendations', [])
            if recommendations:
                print(f"   Recommendations:")
                for rec in recommendations:
                    print(f"     - {rec}")
        
        # Show educational content
        if 'educational_content' in detailed_scene:
            print(f"\n📚 Educational Content:")
            for key, value in detailed_scene['educational_content'].items():
                print(f"  {key}: {value}")
        
        # Show visual elements
        if 'visual_elements' in detailed_scene:
            print(f"\n🎨 Visual Elements:")
            for key, value in detailed_scene['visual_elements'].items():
                print(f"  {key}: {value}")
        
        print("\n✅ New workflow test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        print(f"\n❌ Test error: {str(e)}")

def main():
    """Main function"""
    print("🚀 Testing New Story + Scene Writer Workflow")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No API key found!")
        print("Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable")
        return
    
    print("✅ API key found - proceeding with test")
    print()
    
    # Run async test
    asyncio.run(test_new_workflow())

if __name__ == "__main__":
    main()
