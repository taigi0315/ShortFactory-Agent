#!/usr/bin/env python3
"""
Quick JSON Parsing Test
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.json_parser import parse_scene_package

def test_broken_json():
    """Test the actual broken JSON from Scene 2"""
    
    print("🔧 Testing Broken JSON Repair")
    
    # The actual broken JSON from Scene 2 (truncated)
    broken_json = '''
    {
      "scene_number": 2,
      "narration_script": [
        {
          "line": "Test line",
          "at_ms": 0,
          "pause_ms": 500
        }
      ],
      "visuals": [
        {
          "frame_id": "2A",
          "shot_type": "wide",
          "character_pose": "happy",
          "image_prompt": "A detailed test prompt that is longer than 40 characters",
          "aspect_ratio": "16:9",
          "seed": 123
        }
      ],
      "tts": {
        "engine": "elevenlabs",
        "voice": "sarah"
      },
      "timing": {
        "total_ms": 5000
      },
      "model_hints": ["illustration'''
    
    try:
        result = parse_scene_package(broken_json, 2)
        print("✅ Broken JSON repair successful!")
        print(f"   Scene: {result.scene_number}")
        print(f"   Visuals: {len(result.visuals)}")
        return True
    except Exception as e:
        print(f"❌ Still failing: {e}")
        return False

if __name__ == "__main__":
    success = test_broken_json()
    if success:
        print("\n🎉 JSON repair is working!")
    else:
        print("\n❌ JSON repair needs more work")
