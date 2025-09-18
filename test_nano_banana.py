#!/usr/bin/env python3
"""
Test Gemini Nano Banana (2.5 Flash Image) generation
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

async def test_nano_banana_generation():
    """Test single image generation with Gemini Nano Banana"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("🍌 Testing Gemini Nano Banana Image Generation")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return
    
    print(f"✅ GEMINI_API_KEY found: {api_key[:10]}...")
    
    try:
        # Test direct Gemini image generation
        import google.genai as genai
        from PIL import Image
        from io import BytesIO
        import base64
        
        print("✅ Required modules imported successfully")
        
        # Create test prompt
        test_prompt = "A cute blob-like cartoon character named Glowbie learning about digital technology, educational scene, high quality, detailed, professional"
        
        print(f"📝 Test prompt: {test_prompt}")
        print("🚀 Calling Gemini 2.5 Flash Image API...")
        
        # Initialize client
        client = genai.Client()
        
        # Make API call
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[test_prompt],
            config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
            }
        )
        
        print("✅ API call successful, processing response...")
        
        # Check response structure
        if not response.candidates:
            print("❌ No candidates in response")
            return
        
        candidate = response.candidates[0]
        if not candidate.content.parts:
            print("❌ No parts in response content")
            return
        
        print(f"📊 Response parts: {len(candidate.content.parts)}")
        
        # Extract image
        image_saved = False
        output_path = Path("test_nano_banana_output.png")
        
        for i, part in enumerate(candidate.content.parts):
            print(f"📋 Part {i}: {type(part)}")
            
            if hasattr(part, 'text') and part.text:
                print(f"   Text: {part.text[:100]}...")
            
            if hasattr(part, 'inline_data') and part.inline_data:
                print(f"   Image data found: {len(part.inline_data.data)} characters")
                
                try:
                    # Decode base64 image
                    image_data = base64.b64decode(part.inline_data.data)
                    print(f"   Decoded size: {len(image_data)} bytes")
                    
                    # Save image
                    with open(output_path, "wb") as f:
                        f.write(image_data)
                    
                    print(f"✅ Image saved: {output_path}")
                    print(f"📊 File size: {output_path.stat().st_size} bytes")
                    
                    # Verify it's a valid image
                    try:
                        img = Image.open(output_path)
                        print(f"📐 Image dimensions: {img.size}")
                        print(f"🎨 Image mode: {img.mode}")
                        image_saved = True
                        break
                    except Exception as e:
                        print(f"❌ Invalid image file: {e}")
                        
                except Exception as e:
                    print(f"❌ Failed to decode image: {e}")
        
        if image_saved:
            print(f"\n🎉 SUCCESS! Nano Banana image generated:")
            print(f"   File: {output_path}")
            print(f"   Size: {output_path.stat().st_size / 1024:.1f} KB")
            print(f"\n🎯 You can view the image:")
            print(f"   open {output_path}")
        else:
            print(f"\n❌ FAILED: No valid image data found in response")
            
            # Debug: show response structure
            print(f"\n🔍 Debug info:")
            for i, part in enumerate(candidate.content.parts):
                print(f"   Part {i}: {dir(part)}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_nano_banana_generation())
