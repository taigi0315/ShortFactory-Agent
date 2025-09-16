"""
Test script for K-pop Demon Hunters subject
"""

import os
from dotenv import load_dotenv
from integrated_workflow import IntegratedWorkflow
from image_generate_agent import ImageGenerateAgent
from session_manager import SessionManager
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_kpop_demon_hunters():
    """Test the complete workflow with K-pop Demon Hunters subject"""
    
    print("🎤 Testing K-pop Demon Hunters Workflow")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set!")
        print("Please set your Google API key in .env file:")
        print("GEMINI_API_KEY='your-api-key-here'")
        return
    
    # Create integrated workflow
    workflow = IntegratedWorkflow()
    
    # Test subject
    test_subject = "What is all about K-pop demon hunters?"
    
    try:
        print(f"🎯 Creating project for: {test_subject}")
        
        # Create video project
        session_id = workflow.create_video_project(
            subject=test_subject,
            language="English"
        )
        
        print(f"✅ Project created with session ID: {session_id}")
        
        # Get project status
        status = workflow.get_project_status(session_id)
        print(f"📊 Project status:")
        print(f"   Subject: {status['subject']}")
        print(f"   Created: {status['created_at']}")
        print(f"   Status: {status['status']}")
        print(f"   Progress: {status['progress']}")
        
        # Get script details
        script = workflow.get_script(session_id)
        print(f"📄 Script details:")
        print(f"   Title: {script.title}")
        print(f"   Scenes: {len(script.scenes)}")
        print(f"   Character: {script.main_character_description[:80]}...")
        
        # Show first few scenes
        print(f"\n🎬 First 3 scenes:")
        for i, scene in enumerate(script.scenes[:3]):
            print(f"   Scene {scene.scene_number} ({scene.scene_type}):")
            print(f"     Dialogue: {scene.dialogue[:100]}...")
            print(f"     Image prompt: {scene.image_create_prompt[:80]}...")
            print()
        
        # Test image generation
        print(f"🖼️  Testing image generation...")
        session_manager = SessionManager()
        image_agent = ImageGenerateAgent(session_manager)
        
        # Generate images for the session
        results = image_agent.generate_images_for_session(session_id)
        
        print(f"✅ Image generation completed!")
        print(f"📊 Results:")
        print(f"   Total scenes: {results['total_scenes']}")
        print(f"   Generated images: {len(results['generated_images'])}")
        print(f"   Failed images: {len(results['failed_images'])}")
        print(f"   Generation time: {results['generation_time']:.2f} seconds")
        
        # Show generated images
        print(f"\n🖼️  Generated images:")
        for img in results['generated_images']:
            print(f"   Scene {img['scene_number']}: {img['image_path']}")
        
        # Get final status
        final_status = workflow.get_project_status(session_id)
        print(f"\n📈 Final project status:")
        print(f"   Status: {final_status['status']}")
        print(f"   Progress: {final_status['progress']}")
        
        print(f"\n🎯 Next steps:")
        print(f"   - Session directory: {workflow.session_manager.get_session_dir(session_id)}")
        print(f"   - Ready for Audio Generation Agent")
        print(f"   - Ready for Video Generation Agent")
        print(f"   - Ready for Google Flash 2.5 integration")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_kpop_demon_hunters()
