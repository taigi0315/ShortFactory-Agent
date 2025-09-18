#!/usr/bin/env python3
"""
Test script for Video Maker Agent using mock_output data
"""

import sys
import os
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.video_maker_agent import VideoMakerAgent

def main():
    """Test Video Maker Agent with mock data"""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎬 Testing Video Maker Agent with mock_output data")
    print("=" * 60)
    
    # Initialize Video Maker Agent
    try:
        agent = VideoMakerAgent()
        print("✅ Video Maker Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Video Maker Agent: {e}")
        return
    
    # Test session path
    session_path = "tests/mock_output"
    
    if not Path(session_path).exists():
        print(f"❌ Session path not found: {session_path}")
        return
    
    print(f"📁 Using session: {session_path}")
    
    # Remove existing video to create fresh one
    existing_video = Path(session_path) / "final_video.mp4"
    if existing_video.exists():
        existing_video.unlink()
        print("🗑️ Removed existing video for fresh test")
    
    try:
        # Step 1: Analyze session content
        print("\n📊 Step 1: Analyzing session content...")
        segments = agent.analyze_session_content(session_path)
        
        print(f"Found {len(segments)} video segments:")
        total_duration = 0
        
        for segment in segments:
            print(f"  🎬 Scene {segment.scene_number}:")
            print(f"     🎤 Voice: {segment.voice_duration:.1f}s")
            print(f"     🖼️ Images: {len(segment.images)}")
            
            for timing in segment.image_timings:
                print(f"       {timing.frame_id}: {timing.start_time:.1f}s → {timing.start_time + timing.duration:.1f}s ({timing.duration:.1f}s)")
            
            total_duration += segment.voice_duration
        
        print(f"\n📏 Total expected duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
        
        # Step 2: Create video
        print("\n🎬 Step 2: Creating final video...")
        video_path = agent.create_final_video(session_path)
        
        if not Path(video_path).exists():
            print(f"❌ Video file was not created: {video_path}")
            return
        
        print(f"✅ Video created successfully: {video_path}")
        
        # Step 3: Create metadata
        print("\n📋 Step 3: Creating video metadata...")
        metadata = agent.create_video_metadata(session_path, video_path)
        
        # Display results
        print("\n🎉 VIDEO CREATION COMPLETE!")
        print("=" * 60)
        print(f"📁 Video file: {video_path}")
        print(f"⏱️ Duration: {metadata['total_duration']:.1f} seconds ({metadata['total_duration']/60:.1f} minutes)")
        print(f"💾 File size: {metadata['file_size_bytes'] / (1024*1024):.1f} MB")
        print(f"🎬 Scenes: {metadata['scenes_count']}")
        
        print(f"\n📊 Scene breakdown:")
        for scene_info in metadata['scenes']:
            scene_num = scene_info['scene_number']
            voice_dur = scene_info['voice_duration']
            img_count = scene_info['images_count']
            print(f"  Scene {scene_num}: {voice_dur:.1f}s, {img_count} images")
        
        # Verify video file
        file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
        print(f"\n✅ Video file verification:")
        print(f"   File exists: {Path(video_path).exists()}")
        print(f"   File size: {file_size_mb:.1f} MB")
        
        if file_size_mb > 0.1:  # At least 100KB
            print(f"   Status: ✅ Video appears to be valid")
        else:
            print(f"   Status: ⚠️ Video file seems too small")
        
        print(f"\n🎯 You can now play the video:")
        print(f"   open {video_path}")
        
    except Exception as e:
        print(f"❌ Video creation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎉 Test completed successfully!")

if __name__ == "__main__":
    main()
