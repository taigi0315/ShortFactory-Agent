#!/usr/bin/env python3
"""
Test Gemini Nano Banana image generation - FIXED VERSION
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment
from dotenv import load_dotenv
load_dotenv()

async def test_nano_banana_fixed():
    """Test Gemini Nano Banana with proper data handling"""
    
    print("🍌 Testing Gemini Nano Banana - FIXED VERSION")
    print("=" * 60)
    
    try:
        import google.genai as genai
        from PIL import Image
        from io import BytesIO
        
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found")
            return
        
        print(f"✅ API key found: {api_key[:10]}...")
        
        # Test prompt
        prompt = "A cute blob-like cartoon character named Glowbie, digital art style, high quality"
        
        print(f"📝 Prompt: {prompt}")
        print("🚀 Calling Gemini API...")
        
        # Initialize client and make call
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt]
        )
        
        print("✅ API response received")
        
        # Process response
        if not response.candidates:
            print("❌ No candidates in response")
            return
        
        candidate = response.candidates[0]
        print(f"📊 Parts in response: {len(candidate.content.parts)}")
        
        # Find and save image
        for i, part in enumerate(candidate.content.parts):
            print(f"\n📋 Part {i}:")
            
            # Check for text
            if hasattr(part, 'text') and part.text:
                print(f"   📝 Text: {part.text[:100]}...")
            
            # Check for image data
            if hasattr(part, 'inline_data') and part.inline_data:
                print(f"   🖼️ Image data found!")
                print(f"   📊 Data length: {len(part.inline_data.data)} chars")
                print(f"   📄 MIME type: {getattr(part.inline_data, 'mime_type', 'unknown')}")
                
                try:
                    # Method 1: Direct bytes (if already decoded)
                    if isinstance(part.inline_data.data, bytes):
                        image_bytes = part.inline_data.data
                        print("   ✅ Using direct bytes")
                    else:
                        # Method 2: Base64 decode
                        import base64
                        image_bytes = base64.b64decode(part.inline_data.data)
                        print("   ✅ Base64 decoded")
                    
                    print(f"   📊 Image bytes: {len(image_bytes)} bytes")
                    
                    # Save image
                    output_path = Path("test_nano_banana_fixed.png")
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                    
                    # Verify image
                    if output_path.stat().st_size > 1000:  # At least 1KB
                        img = Image.open(output_path)
                        print(f"\n🎉 SUCCESS!")
                        print(f"   📁 File: {output_path}")
                        print(f"   📊 Size: {output_path.stat().st_size / 1024:.1f} KB")
                        print(f"   📐 Dimensions: {img.size}")
                        print(f"   🎨 Mode: {img.mode}")
                        return True
                    else:
                        print(f"   ❌ File too small: {output_path.stat().st_size} bytes")
                        
                except Exception as e:
                    print(f"   ❌ Image processing error: {e}")
        
        print("\n❌ No valid image found in response")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_nano_banana_fixed())
    if success:
        print("\n✅ Nano Banana test PASSED - Ready for integration!")
    else:
        print("\n❌ Nano Banana test FAILED - Need to fix implementation")
