#!/usr/bin/env python3
"""
Test Video Generation Only
Uses existing session data to test the fixed audio cutoff issue
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.video_maker_agent import VideoMakerAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_video_generation(session_path: str):
    """Test video generation with existing session data"""
    
    session_path = Path(session_path)
    
    if not session_path.exists():
        logger.error(f"❌ Session path does not exist: {session_path}")
        return False
    
    # Check required files
    voices_dir = session_path / "voices"
    images_dir = session_path / "images"
    
    if not voices_dir.exists():
        logger.error(f"❌ Voices directory not found: {voices_dir}")
        return False
        
    if not images_dir.exists():
        logger.error(f"❌ Images directory not found: {images_dir}")
        return False
    
    # List available files
    voice_files = list(voices_dir.glob("*.mp3"))
    image_files = list(images_dir.glob("*.png"))
    
    logger.info(f"📁 Session: {session_path.name}")
    logger.info(f"🎵 Voice files: {len(voice_files)}")
    for vf in sorted(voice_files):
        logger.info(f"   - {vf.name}")
    
    logger.info(f"🖼️ Image files: {len(image_files)}")
    for img in sorted(image_files):
        logger.info(f"   - {img.name}")
    
    try:
        # Initialize Video Maker Agent
        logger.info("🚀 Initializing Video Maker Agent...")
        video_agent = VideoMakerAgent()
        
        # Analyze session content
        logger.info("🔍 Analyzing session content...")
        segments = video_agent.analyze_session_content(str(session_path))
        
        if not segments:
            logger.error("❌ No valid segments found")
            return False
        
        logger.info(f"📊 Found {len(segments)} video segments:")
        for segment in segments:
            logger.info(f"   Scene {segment.scene_number}: {len(segment.images)} images, {segment.voice_duration:.2f}s audio")
        
        # Create test video with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_video_name = f"test_fixed_audio_{timestamp}.mp4"
        output_path = session_path / test_video_name
        
        logger.info(f"🎬 Creating test video: {test_video_name}")
        logger.info("🔧 TESTING FIXED AUDIO CUTOFF ISSUE")
        
        # Generate video
        final_video_path = video_agent.create_final_video(str(session_path), str(output_path))
        
        # Create metadata
        video_metadata = video_agent.create_video_metadata(str(session_path), final_video_path)
        
        # Report results
        logger.info("✅ Video generation completed!")
        logger.info(f"📁 Video file: {final_video_path}")
        logger.info(f"⏱️ Duration: {video_metadata.get('total_duration', 0):.2f}s")
        logger.info(f"💾 Size: {video_metadata.get('file_size_bytes', 0) / (1024*1024):.2f}MB")
        
        # Compare with audio durations
        total_audio_duration = sum(segment.voice_duration for segment in segments)
        video_duration = video_metadata.get('total_duration', 0)
        
        logger.info("🎵 Audio vs Video Duration Analysis:")
        logger.info(f"   Total Audio Duration: {total_audio_duration:.2f}s")
        logger.info(f"   Video Duration: {video_duration:.2f}s")
        
        if abs(video_duration - total_audio_duration) < 1.0:
            logger.info("✅ SUCCESS: Video duration matches audio duration!")
        elif video_duration < total_audio_duration - 1.0:
            logger.warning(f"⚠️ WARNING: Video is {total_audio_duration - video_duration:.2f}s shorter than audio")
        else:
            logger.info(f"ℹ️ INFO: Video is {video_duration - total_audio_duration:.2f}s longer than audio (acceptable)")
        
        # Individual scene analysis
        logger.info("📊 Scene-by-scene analysis:")
        for i, segment in enumerate(segments):
            scene_audio = segment.voice_duration
            # Estimate scene video duration (this is approximate)
            scene_video = sum(timing.duration for timing in segment.image_timings)
            logger.info(f"   Scene {segment.scene_number}: Audio={scene_audio:.2f}s, Video={scene_video:.2f}s")
        
        logger.info(f"🎉 Test completed! Check the video: {final_video_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Video generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_video_generation.py <session_path>")
        print("Example: python test_video_generation.py sessions/20250918-b5175936-ecd5-4116-a5d7-e154c371d002")
        sys.exit(1)
    
    session_path = sys.argv[1]
    success = test_video_generation(session_path)
    sys.exit(0 if success else 1)
