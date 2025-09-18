#!/usr/bin/env python3
"""
Test Gemini with simple structured JSON output
"""

import os
import sys
import json
import asyncio

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment
from dotenv import load_dotenv
load_dotenv()

async def test_simple_structured():
    """Test Gemini with simple JSON schema"""
    
    print("📋 Testing Simple Structured JSON Output")
    print("=" * 50)
    
    try:
        import google.genai as genai
        
        # Simple schema without $schema field
        simple_schema = {
            "type": "object",
            "required": ["scene_number", "title", "dialogue"],
            "properties": {
                "scene_number": {"type": "integer"},
                "title": {"type": "string"},
                "dialogue": {"type": "string"},
                "visuals": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "frame_id": {"type": "string"},
                            "image_prompt": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        test_prompt = """
Create a simple scene about "Digital Technology".

Return JSON with:
- scene_number: 1
- title: Scene title
- dialogue: What the narrator says
- visuals: Array of 2 visual frames with frame_id and image_prompt

Keep it simple and educational.
"""
        
        print("🚀 Testing with simple schema...")
        
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[test_prompt],
            config={
                "temperature": 0.7,
                "response_mime_type": "application/json",
                "response_schema": simple_schema
            }
        )
        
        if response.candidates and response.candidates[0].content.parts:
            response_text = response.candidates[0].content.parts[0].text
            
            print(f"📊 Response: {len(response_text)} chars")
            print(f"📄 Raw response: {response_text[:200]}...")
            
            # Parse JSON
            try:
                parsed = json.loads(response_text)
                print("✅ JSON parsing successful!")
                
                print(f"📋 Structure:")
                print(f"   Scene: {parsed.get('scene_number')}")
                print(f"   Title: {parsed.get('title')}")
                print(f"   Dialogue: {parsed.get('dialogue', '')[:50]}...")
                print(f"   Visuals: {len(parsed.get('visuals', []))} frames")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                return False
        else:
            print("❌ No response content")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_structured())
    
    if success:
        print("\n🎉 ✅ Structured output works!")
        print("\n💡 Solution:")
        print("   • Add response_schema to Scene Script Writer")
        print("   • Use schemas/ScenePackage.json (without $schema field)")
        print("   • This will eliminate JSON parsing errors")
    else:
        print("\n❌ Structured output failed - need different approach")
