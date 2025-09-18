#!/usr/bin/env python3
"""
Test Gemini with structured JSON output using schema
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment
from dotenv import load_dotenv
load_dotenv()

async def test_structured_output():
    """Test Gemini with JSON schema for structured output"""
    
    print("📋 Testing Gemini Structured Output with JSON Schema")
    print("=" * 60)
    
    try:
        import google.genai as genai
        
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found")
            return
        
        print(f"✅ API key found: {api_key[:10]}...")
        
        # Load ScenePackage schema
        schema_path = Path("schemas/ScenePackage.json")
        if not schema_path.exists():
            print(f"❌ Schema not found: {schema_path}")
            return
        
        with open(schema_path, 'r') as f:
            scene_schema = json.load(f)
        
        print(f"✅ Schema loaded: {schema_path}")
        
        # Simple test prompt
        test_prompt = """
Create a scene package for Scene 1 about "Digital Technology Basics".

REQUIREMENTS:
- scene_number: 1
- narration_script: Array of dialogue lines with timing
- visuals: Array of 3 visual frames
- tts: ElevenLabs settings
- timing: Scene timing info
- continuity: Callback tags

Make it educational and engaging. Follow the JSON schema exactly.
"""
        
        print("📝 Test prompt created")
        print("🚀 Calling Gemini with JSON schema...")
        
        # Initialize client
        client = genai.Client()
        
        # Make API call with schema
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[test_prompt],
            config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
                "response_schema": scene_schema  # 🎯 This enforces structure!
            }
        )
        
        print("✅ API call successful")
        
        # Extract response
        if response.candidates and response.candidates[0].content.parts:
            response_text = response.candidates[0].content.parts[0].text
            print(f"📊 Response length: {len(response_text)} characters")
            
            # Try to parse JSON
            try:
                parsed_json = json.loads(response_text)
                print("✅ JSON parsing successful!")
                
                # Check required fields
                required_fields = ['scene_number', 'narration_script', 'visuals', 'tts', 'timing', 'continuity']
                missing_fields = [field for field in required_fields if field not in parsed_json]
                
                if missing_fields:
                    print(f"⚠️ Missing fields: {missing_fields}")
                else:
                    print("✅ All required fields present")
                
                # Show structure
                print(f"\n📋 Generated structure:")
                print(f"   Scene number: {parsed_json.get('scene_number')}")
                print(f"   Narration lines: {len(parsed_json.get('narration_script', []))}")
                print(f"   Visual frames: {len(parsed_json.get('visuals', []))}")
                print(f"   TTS engine: {parsed_json.get('tts', {}).get('engine')}")
                
                # Save test output
                with open("test_structured_output.json", "w") as f:
                    json.dump(parsed_json, f, indent=2)
                
                print(f"💾 Output saved: test_structured_output.json")
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"Raw response: {response_text[:200]}...")
                return False
        else:
            print("❌ No response content")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_structured_output()
    
    print(f"\n🎯 Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if success:
        print("\n💡 Solution for JSON parsing issues:")
        print("   • Use response_schema parameter in Gemini API calls")
        print("   • Enforces strict JSON structure")
        print("   • Reduces parsing errors significantly")
        print("   • Can be integrated into Scene Script Writer")
    else:
        print("\n🔧 Need to investigate further...")

if __name__ == "__main__":
    asyncio.run(main())
