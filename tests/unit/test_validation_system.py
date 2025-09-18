"""
Test the 2-Stage Validation System

This script tests the new validation system with Script Validator and Scene Script Validator agents.
"""

import os
import asyncio
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
import sys
sys.path.append('src')

# Import agents and components
from agents.adk_script_writer_agent import ADKScriptWriterAgent
from agents.adk_scene_writer_agent import ADKSceneWriterAgent
from agents.adk_script_validator_agent import ADKScriptValidatorAgent
from agents.adk_scene_script_validator_agent import ADKSceneScriptValidatorAgent
from core.workflow_state_manager import ValidationWorkflowOrchestrator
from core.shared_context import SharedContextManager
from core.scene_continuity_manager import SceneContinuityManager
from core.image_style_selector import ImageStyleSelector
from core.educational_enhancer import EducationalEnhancer
from core.session_manager import SessionManager

async def test_validation_system():
    """Test the complete 2-stage validation system"""
    print("🚀 Testing 2-Stage Validation System")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        return
    
    print("✅ API key found - proceeding with test")
    
    try:
        # Initialize managers and components
        print("\n🔧 Initializing components...")
        shared_context_manager = SharedContextManager()
        continuity_manager = SceneContinuityManager()
        style_selector = ImageStyleSelector()
        educational_enhancer = EducationalEnhancer()
        session_manager = SessionManager()
        
        # Initialize agents
        print("🤖 Initializing agents...")
        script_writer = ADKScriptWriterAgent(shared_context_manager)
        scene_writer = ADKSceneWriterAgent(session_manager, shared_context_manager, 
                                         continuity_manager, style_selector, educational_enhancer)
        script_validator = ADKScriptValidatorAgent(shared_context_manager)
        scene_validator = ADKSceneScriptValidatorAgent(shared_context_manager, continuity_manager)
        
        # Initialize workflow orchestrator
        session_id = "test_validation_session"
        orchestrator = ValidationWorkflowOrchestrator(session_id)
        
        # Test subject
        subject = "Texas"
        print(f"\n📝 Testing with subject: {subject}")
        print("🎯 Focus: 2-stage validation system")
        
        # Step 1: Generate story script
        print("\n📖 Step 1: Generating story script...")
        story_script = await script_writer.generate_story_script(subject)
        print(f"✅ Story generated: {story_script.title}")
        print(f"📚 Overall story: {story_script.overall_story}")
        print(f"🎬 Scene plan: {len(story_script.scene_plan)} scenes")
        
        # Step 2: Validate story script
        print("\n🔍 Step 2: Validating story script...")
        script_validation_result = await script_validator.validate_story_script(story_script)
        
        print(f"📊 Script Validation Result:")
        print(f"   Status: {script_validation_result.status.value}")
        print(f"   Overall Score: {script_validation_result.overall_score:.2f}")
        print(f"   Fun Score: {script_validation_result.fun_score:.2f}")
        print(f"   Interest Score: {script_validation_result.interest_score:.2f}")
        print(f"   Uniqueness Score: {script_validation_result.uniqueness_score:.2f}")
        print(f"   Educational Score: {script_validation_result.educational_score:.2f}")
        print(f"   Coherence Score: {script_validation_result.coherence_score:.2f}")
        print(f"   Issues: {len(script_validation_result.issues)}")
        print(f"   Feedback: {script_validation_result.feedback}")
        
        if script_validation_result.status.value == "revise":
            print(f"   Revision Instructions: {script_validation_result.revision_instructions}")
        
        # Step 3: Generate scene scripts (if story passed)
        if script_validation_result.status.value == "pass":
            print("\n🎬 Step 3: Generating scene scripts...")
            
            # Generate detailed scene scripts for first 2 scenes
            scenes = []
            for i in range(1, 3):  # Test first 2 scenes
                scene_data = await scene_writer.write_scene_script(
                    scene_number=i,
                    scene_type=story_script.scene_plan[i-1].scene_type.value,
                    overall_story=story_script.overall_story,
                    full_script_context=f"Story: {story_script.overall_story}",
                    subject=subject
                )
                scenes.append(scene_data)
                print(f"✅ Scene {i} generated")
            
            # Step 4: Validate scene scripts
            print("\n🔍 Step 4: Validating scene scripts...")
            scene_validation_summary = await scene_validator.validate_all_scenes(scenes)
            
            print(f"📊 Scene Validation Summary:")
            print(f"   Total Scenes: {scene_validation_summary.total_scenes}")
            print(f"   Passed Scenes: {scene_validation_summary.passed_scenes}")
            print(f"   Failed Scenes: {scene_validation_summary.failed_scenes}")
            print(f"   Connection Score: {scene_validation_summary.overall_connection_score:.2f}")
            print(f"   Needs Revision: {scene_validation_summary.needs_revision}")
            print(f"   Revision Scenes: {scene_validation_summary.revision_scenes}")
            
            # Show individual scene results
            for result in scene_validation_summary.scene_results:
                print(f"\n   Scene {result.scene_number}:")
                print(f"     Status: {result.status.value}")
                print(f"     Overall Score: {result.overall_score:.2f}")
                print(f"     Scene Quality: {result.scene_quality_score:.2f}")
                print(f"     Visual Potential: {result.visual_potential_score:.2f}")
                print(f"     Educational Density: {result.educational_density_score:.2f}")
                print(f"     Character Utilization: {result.character_utilization_score:.2f}")
                print(f"     Connection Score: {result.connection_score:.2f}")
                print(f"     Issues: {len(result.issues)}")
                if result.issues:
                    for issue in result.issues:
                        print(f"       - {issue.category}: {issue.description}")
        
        # Step 5: Show workflow state
        print("\n📋 Step 5: Workflow State Summary...")
        workflow_summary = orchestrator.get_workflow_summary()
        print(f"   Session ID: {workflow_summary['session_id']}")
        print(f"   Current Stage: {workflow_summary['current_stage']}")
        print(f"   Script State: {workflow_summary['script_state']}")
        print(f"   Total Validations: {workflow_summary['total_validations']}")
        print(f"   Total Revisions: {workflow_summary['total_revisions']}")
        print(f"   Is Complete: {workflow_summary['is_complete']}")
        
        print("\n✅ 2-stage validation system test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_validation_system())
