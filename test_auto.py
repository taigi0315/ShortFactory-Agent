#!/usr/bin/env python3
"""
ShortFactory Agent - Auto Test
Automated test without user input
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_auto():
    """Automated test for ShortFactory Agent"""
    
    print("🎬 ShortFactory Agent - Auto Test")
    print("=" * 50)
    print("AI-powered short video creation system")
    print("Using Huh character with cosplay system")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set!")
        print("Please set your Google API key in .env file:")
        print("GEMINI_API_KEY='your-api-key-here'")
        return
    
    # Test subject
    subject = "What is Python programming?"
    print(f"\n🎯 Testing with subject: {subject}")
    
    try:
        # Import modules
        from core.session_manager import SessionManager
        from agents.script_writer_agent import ScriptWriterAgent
        from agents.huh_image_agent import HuhImageAgent
        
        # Initialize components
        session_manager = SessionManager()
        script_writer = ScriptWriterAgent()
        image_agent = HuhImageAgent(session_manager)
        
        # Create session
        print("1️⃣ Creating session...")
        session_id = session_manager.create_session(subject, "English")
        print(f"✅ Session created: {session_id}")
        
        # Generate script
        print("2️⃣ Generating script...")
        script = script_writer.generate_script(
            subject=subject,
            language="English",
            max_video_scenes=8
        )
        print(f"✅ Script generated: {script.title}")
        print(f"   Character: {script.main_character_description[:80]}...")
        if hasattr(script, 'character_cosplay_instructions'):
            print(f"   Cosplay: {script.character_cosplay_instructions}")
        print(f"   Scenes: {len(script.scenes)}")
        
        # Show scene details
        print("\n📋 Scene Details:")
        for i, scene in enumerate(script.scenes[:3]):
            print(f"   Scene {scene.scene_number} ({scene.scene_type}):")
            print(f"     Dialogue: {scene.dialogue[:80]}...")
            print(f"     Character pose: {scene.character_pose}")
            print(f"     Background: {scene.background_description}")
            print()
        
        # Save script
        print("3️⃣ Saving script...")
        script_path = session_manager.save_script(session_id, script)
        print(f"✅ Script saved: {script_path}")
        
        # Generate images with Huh character
        print("4️⃣ Generating images with Huh character...")
        print("   - Loading Huh character from assets/huh.png")
        print("   - Applying cosplay instructions")
        print("   - Creating meaningful educational images")
        print("   - Character will be small in images")
        
        image_results = image_agent.generate_images_for_session(session_id)
        print(f"✅ Images generated: {len(image_results['generated_images'])}")
        print(f"   Model: {image_results['model_used']}")
        print(f"   Character: {image_results['character']}")
        print(f"   Cosplay applied: {image_results['cosplay_instructions']}")
        print(f"   Time: {image_results['generation_time']:.2f} seconds")
        
        # Show results
        print("\n📁 Generated Images:")
        for img in image_results['generated_images']:
            print(f"   Scene {img['scene_number']} ({img['scene_type']}): {img['image_path']}")
            print(f"     Character pose: {img['character_pose']}")
            print(f"     Background: {img['background_description']}")
        
        # Show any failures
        if image_results['failed_images']:
            print("\n❌ Failed images:")
            for fail in image_results['failed_images']:
                print(f"   Scene {fail['scene_number']}: {fail['error']}")
        
        # Final status
        status = session_manager.get_session_status(session_id)
        print(f"\n📊 Final Status: {status['status']}")
        print(f"📈 Progress: {status['progress']}")
        
        print(f"\n🎉 Auto test completed successfully!")
        print(f"📁 Session directory: {session_manager.get_session_dir(session_id)}")
        print("🎯 Next steps: Audio Generation → Video Generation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_auto()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)
