"""
Test script for Huh-Based Workflow
Tests the complete workflow with Huh character and cosplay instructions
"""

import os
import sys
sys.path.append('..')

from dotenv import load_dotenv
from src.core.huh_workflow import HuhWorkflow
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_huh_workflow():
    """Test the complete Huh-based workflow"""
    
    print("🤖 Testing Huh-Based Workflow")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set!")
        print("Please set your Google API key in .env file:")
        print("GEMINI_API_KEY='your-api-key-here'")
        return
    
    # Create Huh-based workflow
    workflow = HuhWorkflow()
    
    # Test subject
    test_subject = "Do you know Elon Musk was not CEO of Tesla?"
    
    try:
        print(f"🎯 Creating complete Huh-based project for: {test_subject}")
        
        # Create complete project
        results = workflow.create_complete_project(
            subject=test_subject,
            language="English"
        )
        
        session_id = results["session_id"]
        print(f"✅ Complete project created with session ID: {session_id}")
        
        # Show project details
        print(f"📊 Project details:")
        print(f"   Subject: {results['subject']}")
        print(f"   Language: {results['language']}")
        print(f"   Script completed: {results['script_completed']}")
        print(f"   Images completed: {results['images_completed']}")
        
        # Get script details
        script = workflow.get_script(session_id)
        print(f"📄 Script details:")
        print(f"   Title: {script.title}")
        print(f"   Character: {script.main_character_description[:80]}...")
        print(f"   Cosplay instructions: {script.character_cosplay_instructions}")
        print(f"   Scenes: {len(script.scenes)}")
        
        # Show first few scenes
        print(f"\n🎬 First 3 scenes:")
        for i, scene in enumerate(script.scenes[:3]):
            print(f"   Scene {scene.scene_number} ({scene.scene_type}):")
            print(f"     Dialogue: {scene.dialogue[:100]}...")
            print(f"     Image prompt: {scene.image_create_prompt[:80]}...")
            print()
        
        # Show image generation results
        image_results = results["image_results"]
        print(f"🖼️  Image generation results:")
        print(f"   Model: {image_results['model_used']}")
        print(f"   Character: {image_results['character']}")
        print(f"   Cosplay instructions: {image_results['cosplay_instructions']}")
        print(f"   Total scenes: {image_results['total_scenes']}")
        print(f"   Generated images: {len(image_results['generated_images'])}")
        print(f"   Failed images: {len(image_results['failed_images'])}")
        print(f"   Generation time: {image_results['generation_time']:.2f} seconds")
        
        # Show generated images
        print(f"\n🖼️  Generated Huh-based images:")
        for img in image_results['generated_images']:
            print(f"   Scene {img['scene_number']}: {img['image_path']}")
            print(f"     Character: {img['character']}")
            print(f"     Cosplay applied: {img['cosplay_applied']}")
        
        # Show any failures
        if image_results['failed_images']:
            print(f"\n❌ Failed images:")
            for fail in image_results['failed_images']:
                print(f"   Scene {fail['scene_number']}: {fail['error']}")
        
        # Get final project status
        final_status = workflow.get_project_status(session_id)
        print(f"\n📈 Final project status:")
        print(f"   Status: {final_status['status']}")
        print(f"   Progress: {final_status['progress']}")
        
        print(f"\n🎯 Next steps:")
        print(f"   - Session directory: {workflow.session_manager.get_session_dir(session_id)}")
        print(f"   - Ready for Audio Generation Agent")
        print(f"   - Ready for Video Generation Agent")
        print(f"   - Huh character with cosplay successfully integrated!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_huh_workflow()
