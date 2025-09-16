"""
Test Script for Script Writer Agent
This script allows you to test the Script Writer Agent with different subjects
"""

from script_writer_agent import ScriptWriterAgent
import json

def test_script_agent():
    """Test the Script Writer Agent with various subjects"""
    
    # Create agent instance
    agent = ScriptWriterAgent()
    
    # Test subjects
    test_subjects = [
        "Photosynthesis",
        "Gravity",
        "The Water Cycle",
        "How Computers Work",
        "The Solar System"
    ]
    
    print("🎬 Script Writer Agent Test Suite")
    print("=" * 50)
    
    for i, subject in enumerate(test_subjects, 1):
        print(f"\n📝 Test {i}: {subject}")
        print("-" * 30)
        
        try:
            # Generate script
            script = agent.generate_script(
                subject=subject,
                language="English",
                max_video_scenes=5
            )
            
            # Validate script
            validation = agent.validate_script(script)
            
            # Display results
            print(f"✅ Script generated successfully!")
            print(f"   Title: {script.title}")
            print(f"   Scenes: {len(script.scenes)}")
            print(f"   Hook Scene: {'Yes' if validation['has_hook_scene'] else 'No'}")
            print(f"   Animation Scenes: {validation['animation_scenes']}")
            print(f"   Validation: {'✅ Valid' if validation['is_valid'] else '❌ Invalid'}")
            
            if validation['warnings']:
                print(f"   Warnings: {', '.join(validation['warnings'])}")
            
            # Show first scene details
            first_scene = script.scenes[0]
            print(f"   First Scene: {first_scene.scene_type.value} - {first_scene.dialogue[:50]}...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Interactive Testing")
    print("Enter a subject to test (or 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\nSubject: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                print("Please enter a subject.")
                continue
            
            print(f"\n🎬 Generating script for: {user_input}")
            print("-" * 40)
            
            # Generate script
            script = agent.generate_script(
                subject=user_input,
                language="English",
                max_video_scenes=6
            )
            
            # Validate
            validation = agent.validate_script(script)
            
            # Display results
            print(f"✅ Success! Generated {len(script.scenes)} scenes")
            print(f"📺 Title: {script.title}")
            print(f"🎭 Character: {script.main_character_description[:100]}...")
            
            # Show all scenes
            print(f"\n📋 Scenes Overview:")
            for scene in script.scenes:
                animation_indicator = "🎬" if scene.needs_animation else "🖼️"
                hook_indicator = "🎣" if scene.hook_technique else ""
                print(f"   {scene.scene_number}. {animation_indicator} {hook_indicator} {scene.scene_type.value}: {scene.dialogue[:60]}...")
            
            # Ask if user wants to see full details
            show_details = input(f"\nShow full script details? (y/n): ").strip().lower()
            if show_details in ['y', 'yes']:
                print(f"\n📄 Full Script:")
                print(agent.export_script(script, format="text"))
            
            # Ask if user wants to save JSON
            save_json = input(f"\nSave as JSON file? (y/n): ").strip().lower()
            if save_json in ['y', 'yes']:
                filename = f"script_{user_input.replace(' ', '_').lower()}.json"
                with open(filename, 'w') as f:
                    f.write(agent.export_script(script, format="json"))
                print(f"💾 Saved as: {filename}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_specific_subject(subject: str):
    """Test with a specific subject and show detailed output"""
    
    agent = ScriptWriterAgent()
    
    print(f"🎬 Testing Script Writer Agent with: {subject}")
    print("=" * 60)
    
    try:
        # Generate script
        script = agent.generate_script(
            subject=subject,
            language="English",
            max_video_scenes=6
        )
        
        # Validate
        validation = agent.validate_script(script)
        
        # Display full results
        print(f"✅ Script Generated Successfully!")
        print(f"📺 Title: {script.title}")
        print(f"🎭 Style: {script.overall_style}")
        print(f"📊 Validation: {validation}")
        
        print(f"\n📋 Full Script:")
        print(agent.export_script(script, format="text"))
        
        print(f"\n🔧 JSON Output:")
        print(agent.export_script(script, format="json"))
        
        return script
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Run interactive test
    test_script_agent()
    
    # Uncomment to test specific subject
    # test_specific_subject("Artificial Intelligence")
