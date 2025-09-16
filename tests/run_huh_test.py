"""
End-to-End Test for Huh-Based Workflow
Tests: Script Generation → Character Cosplay → Image Generation
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from core.huh_workflow import HuhWorkflow
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run end-to-end test for Huh-based workflow"""
    
    print("🤖 Huh-Based End-to-End Test")
    print("=" * 60)
    print("Testing: Script Generation → Character Cosplay → Image Generation")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set!")
        print("Please set your Google API key in .env file:")
        print("GEMINI_API_KEY='your-api-key-here'")
        return
    
    # Test subject
    test_subject = "Do you know Elon Musk was not CEO of Tesla?"
    
    try:
        print(f"🎯 Testing subject: {test_subject}")
        print()
        
        # Create Huh-based workflow
        print("1️⃣ Initializing Huh-based workflow...")
        workflow = HuhWorkflow()
        print("✅ Workflow initialized")
        print()
        
        # Create complete project
        print("2️⃣ Creating complete project...")
        results = workflow.create_complete_project(
            subject=test_subject,
            language="English"
        )
        
        session_id = results["session_id"]
        print(f"✅ Project created with session ID: {session_id}")
        print()
        
        # Show results
        print("3️⃣ Project Results:")
        print(f"   Subject: {results['subject']}")
        print(f"   Script completed: {results['script_completed']}")
        print(f"   Images completed: {results['images_completed']}")
        print()
        
        # Get script details
        script = workflow.get_script(session_id)
        print("4️⃣ Script Details:")
        print(f"   Title: {script.title}")
        print(f"   Character: {script.main_character_description[:80]}...")
        print(f"   Cosplay instructions: {script.character_cosplay_instructions}")
        print(f"   Total scenes: {len(script.scenes)}")
        print()
        
        # Show first few scenes
        print("5️⃣ First 3 scenes:")
        for i, scene in enumerate(script.scenes[:3]):
            print(f"   Scene {scene.scene_number} ({scene.scene_type}):")
            print(f"     Dialogue: {scene.dialogue[:100]}...")
            print(f"     Image prompt: {scene.image_create_prompt[:80]}...")
            print()
        
        # Show image generation results
        image_results = results["image_results"]
        print("6️⃣ Image Generation Results:")
        print(f"   Model: {image_results['model_used']}")
        print(f"   Character: {image_results['character']}")
        print(f"   Cosplay instructions: {image_results['cosplay_instructions']}")
        print(f"   Generated images: {len(image_results['generated_images'])}")
        print(f"   Failed images: {len(image_results['failed_images'])}")
        print(f"   Generation time: {image_results['generation_time']:.2f} seconds")
        print()
        
        # Show generated images
        print("7️⃣ Generated Images:")
        for img in image_results['generated_images']:
            print(f"   Scene {img['scene_number']}: {img['image_path']}")
            print(f"     Character: {img['character']}")
            print(f"     Cosplay applied: {img['cosplay_applied']}")
        print()
        
        # Show any failures
        if image_results['failed_images']:
            print("❌ Failed images:")
            for fail in image_results['failed_images']:
                print(f"   Scene {fail['scene_number']}: {fail['error']}")
            print()
        
        # Final status
        final_status = workflow.get_project_status(session_id)
        print("8️⃣ Final Status:")
        print(f"   Status: {final_status['status']}")
        print(f"   Progress: {final_status['progress']}")
        print()
        
        print("🎉 End-to-End Test Completed Successfully!")
        print(f"📁 Session directory: {workflow.session_manager.get_session_dir(session_id)}")
        print("🎯 Ready for next steps: Audio Generation → Video Generation")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
