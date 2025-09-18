"""
Video Maker Agent - Creates final video by synchronizing images and audio

This agent takes the generated images and voice files and creates a synchronized video
where images are displayed for durations calculated based on the audio length.
"""

import os
import json
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import subprocess
from dataclasses import dataclass

# Try to import audio analysis libraries
try:
    from mutagen.mp3 import MP3
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    logging.warning("Mutagen not available. Using ffprobe for audio duration.")

logger = logging.getLogger(__name__)

@dataclass
class ImageTiming:
    """Represents timing information for an image in the video"""
    image_path: str
    start_time: float
    duration: float
    scene_number: int
    frame_id: str

@dataclass
class SceneVideoSegment:
    """Represents a complete scene with images and audio"""
    scene_number: int
    voice_file: str
    voice_duration: float
    images: List[str]
    image_timings: List[ImageTiming]

class VideoMakerAgent:
    """
    Video Maker Agent that creates synchronized videos from images and audio
    """
    
    def __init__(self):
        """Initialize the Video Maker Agent"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Video Maker Agent initialized")
        
        # Check for required tools
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required tools are available"""
        try:
            # Check for ffmpeg
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError("FFmpeg not found")
            self.logger.info("FFmpeg available")
        except FileNotFoundError:
            raise RuntimeError("FFmpeg is required but not found in PATH")
        
        try:
            # Check for ffprobe
            result = subprocess.run(['ffprobe', '-version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError("FFprobe not found")
            self.logger.info("FFprobe available")
        except FileNotFoundError:
            raise RuntimeError("FFprobe is required but not found in PATH")
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get the duration of an audio file in seconds
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Duration in seconds
        """
        if MUTAGEN_AVAILABLE:
            try:
                audio = MP3(audio_path)
                return float(audio.info.length)
            except Exception as e:
                self.logger.warning(f"Failed to get duration with mutagen: {e}")
        
        # Fallback to ffprobe
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"FFprobe failed: {result.stderr}")
            
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            return duration
            
        except Exception as e:
            self.logger.error(f"Failed to get audio duration for {audio_path}: {e}")
            raise
    
    def distribute_image_timings(self, images: List[str], total_duration: float) -> List[float]:
        """
        Distribute the total duration among images
        
        Strategy:
        - Target 5-7 seconds per image for better engagement
        - If total duration allows, use optimal timing
        - If too short, distribute evenly but keep minimum 3s per image
        - If too long, extend proportionally
        
        Args:
            images: List of image paths
            total_duration: Total duration to distribute
            
        Returns:
            List of durations for each image
        """
        if not images:
            return []
        
        # Target duration per image (3-5 seconds for fast-paced content)
        target_min_duration = 3.0  
        target_max_duration = 5.0
        absolute_min_duration = 2.0  # Never go below 2 seconds
        
        if len(images) == 1:
            # Single image: use full duration but cap at reasonable maximum
            duration = min(total_duration, 15.0)  # Max 15 seconds for single image
            return [duration]
        
        # Calculate optimal duration per image
        optimal_duration = (target_min_duration + target_max_duration) / 2  # 4 seconds
        total_optimal = optimal_duration * len(images)
        
        durations = []
        
        if total_duration >= total_optimal:
            # We have enough time, distribute more evenly around optimal timing
            remaining_time = total_duration
            
            for i, _ in enumerate(images):
                if i == len(images) - 1:
                    # Last image: cap at maximum reasonable duration
                    max_last_duration = min(remaining_time, target_max_duration + 3.0)  # Max 10 seconds
                    durations.append(max_last_duration)
                else:
                    # Vary around optimal duration (5-7 seconds)
                    if i % 2 == 0:
                        duration = target_min_duration + (i * 0.3) % 2.0  # 5-7 seconds
                    else:
                        duration = target_max_duration - (i * 0.2) % 2.0  # 5-7 seconds
                    
                    # Ensure we don't exceed remaining time
                    min_remaining_for_others = (len(images) - i - 1) * target_min_duration
                    max_allowed = remaining_time - min_remaining_for_others
                    duration = min(duration, max_allowed)
                    
                    durations.append(duration)
                    remaining_time -= duration
        else:
            # Limited time, distribute evenly but respect minimum
            base_duration = total_duration / len(images)
            
            if base_duration >= absolute_min_duration:
                # Can give each image at least 3 seconds
                remaining_time = total_duration
                
                for i, _ in enumerate(images):
                    if i == len(images) - 1:
                        durations.append(remaining_time)
                    else:
                        # Slight variation around base duration
                        variation = base_duration * 0.15 * (0.5 - (i % 2))
                        duration = max(absolute_min_duration, base_duration + variation)
                        duration = min(duration, remaining_time - (len(images) - i - 1) * absolute_min_duration)
                        durations.append(duration)
                        remaining_time -= duration
            else:
                # Very limited time, just distribute evenly
                base_duration = max(2.0, total_duration / len(images))  # Minimum 2 seconds
                durations = [base_duration] * (len(images) - 1)
                durations.append(total_duration - sum(durations))
        
        return durations
    
    def _create_silent_video_segments(self, session_path: str) -> List[SceneVideoSegment]:
        """Create video segments with default timing when no voice files exist"""
        session_path = Path(session_path)
        images_dir = session_path / "images"
        
        if not images_dir.exists():
            return []
        
        # Group images by scene number
        scene_images = {}
        for img_path in images_dir.glob("*.png"):
            # Extract scene number from filename (1a.png -> 1)
            scene_num = int(img_path.stem[0])
            if scene_num not in scene_images:
                scene_images[scene_num] = []
            scene_images[scene_num].append(str(img_path))
        
        segments = []
        
        for scene_num in sorted(scene_images.keys()):
            images = sorted(scene_images[scene_num])
            
            # Default timing: 6 seconds per image
            default_duration_per_image = 6.0
            total_scene_duration = len(images) * default_duration_per_image
            
            # Calculate image timings
            durations = [default_duration_per_image] * len(images)
            
            image_timings = []
            current_time = 0.0
            
            for i, (img_path, duration) in enumerate(zip(images, durations)):
                timing = ImageTiming(
                    image_path=img_path,
                    start_time=current_time,
                    duration=duration,
                    scene_number=scene_num,
                    frame_id=f"{scene_num}{chr(ord('a') + i)}"
                )
                image_timings.append(timing)
                current_time += duration
            
            segment = SceneVideoSegment(
                scene_number=scene_num,
                voice_file="",  # No voice file
                voice_duration=total_scene_duration,
                images=images,
                image_timings=image_timings
            )
            
            segments.append(segment)
            
            logger.info(f"Silent scene {scene_num}: {len(images)} images, "
                       f"{total_scene_duration:.2f}s default timing")
        
        return segments
    
    def analyze_session_content(self, session_path: str) -> List[SceneVideoSegment]:
        """
        Analyze session content and create video segments
        
        Args:
            session_path: Path to the session directory
            
        Returns:
            List of SceneVideoSegment objects
        """
        session_path = Path(session_path)
        voices_dir = session_path / "voices"
        images_dir = session_path / "images"
        
        if not voices_dir.exists():
            raise FileNotFoundError(f"Voices directory not found: {voices_dir}")
        if not images_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {images_dir}")
        
        # Get all voice files and sort by scene number
        voice_files = list(voices_dir.glob("scene_*_voice.mp3"))
        voice_files.sort(key=lambda x: int(x.stem.split('_')[1]))
        
        # If no voice files, create silent video with default timing
        if not voice_files:
            logger.warning("No voice files found, creating silent video with default timing")
            return self._create_silent_video_segments(session_path)
        
        segments = []
        
        for voice_file in voice_files:
            # Extract scene number from filename (scene_01_voice.mp3 -> 1)
            scene_num = int(voice_file.stem.split('_')[1])
            
            # Get audio duration
            voice_duration = self.get_audio_duration(str(voice_file))
            
            # Find images for this scene
            scene_images = []
            for suffix in ['a', 'b', 'c', 'd', 'e']:  # Support up to 5 images per scene
                img_path = images_dir / f"{scene_num}{suffix}.png"
                if img_path.exists():
                    scene_images.append(str(img_path))
            
            if not scene_images:
                self.logger.warning(f"No images found for scene {scene_num}, skipping this scene")
                continue
            
            # Calculate image timings - ENSURE video is at least as long as audio
            durations = self.distribute_image_timings(scene_images, voice_duration)
            
            # CRITICAL: Verify total video duration matches or exceeds audio duration
            total_video_duration = sum(durations)
            if total_video_duration < voice_duration:
                # Extend the last image to match audio duration exactly
                durations[-1] += (voice_duration - total_video_duration)
                self.logger.info(f"🔧 Extended last image by {voice_duration - total_video_duration:.2f}s to match audio duration")
            
            image_timings = []
            current_time = 0.0
            
            for i, (img_path, duration) in enumerate(zip(scene_images, durations)):
                timing = ImageTiming(
                    image_path=img_path,
                    start_time=current_time,
                    duration=duration,
                    scene_number=scene_num,
                    frame_id=f"{scene_num}{chr(ord('a') + i)}"
                )
                image_timings.append(timing)
                current_time += duration
            
            segment = SceneVideoSegment(
                scene_number=scene_num,
                voice_file=str(voice_file),
                voice_duration=voice_duration,
                images=scene_images,
                image_timings=image_timings
            )
            
            segments.append(segment)
            
            self.logger.info(f"Scene {scene_num}: {len(scene_images)} images, "
                           f"{voice_duration:.2f}s audio")
        
        return segments
    
    def create_scene_video(self, segment: SceneVideoSegment, output_path: str) -> str:
        """
        Create a video for a single scene
        
        Args:
            segment: SceneVideoSegment with timing information
            output_path: Path for the output video file
            
        Returns:
            Path to the created video file
        """
        # Create a temporary file list for ffmpeg concat
        output_path = Path(output_path)
        temp_dir = output_path.parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        scene_segments = []
        
        for timing in segment.image_timings:
            # Create a video segment for each image
            segment_path = temp_dir / f"scene_{segment.scene_number}_{timing.frame_id}.mp4"
            
            cmd = [
                'ffmpeg', '-y',  # Overwrite output files
                '-loop', '1',    # Loop the image
                '-i', timing.image_path,  # Input image
                '-t', str(timing.duration),  # Duration
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',  # Vertical video format
                '-r', '30',      # Frame rate
                '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
                str(segment_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed for image {timing.image_path}: {result.stderr}")
            
            scene_segments.append(str(segment_path))
        
        # Concatenate image segments
        if len(scene_segments) == 1:
            video_only_path = scene_segments[0]
        else:
            # Create concat file
            concat_file = temp_dir / f"scene_{segment.scene_number}_concat.txt"
            with open(concat_file, 'w') as f:
                for seg_path in scene_segments:
                    # Use absolute paths for concat file
                    abs_path = Path(seg_path).resolve()
                    f.write(f"file '{abs_path}'\n")
            
            video_only_path = temp_dir / f"scene_{segment.scene_number}_video_only.mp4"
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',
                str(video_only_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg concat failed: {result.stderr}")
        
        # Add audio to the video (if voice file exists)
        if segment.voice_file and os.path.exists(segment.voice_file):
            # CRITICAL FIX: Always preserve full audio - never cut off dialogue
            # Remove -shortest flag and use audio as the master duration
            cmd = [
                'ffmpeg', '-y',
                '-i', str(video_only_path),  # Video input
                '-i', segment.voice_file,    # Audio input
                '-c:v', 'copy',              # Copy video codec
                '-c:a', 'aac',               # Audio codec
                '-map', '0:v',               # Use video stream
                '-map', '1:a',               # Use audio stream  
                output_path
            ]
            
            # Get audio duration for logging
            audio_duration = self.get_audio_duration(segment.voice_file)
            self.logger.info(f"🎵 Preserving full audio duration: {audio_duration:.2f}s for scene {segment.scene_number}")
            self.logger.info(f"🔧 FIXED: Removed -shortest flag to prevent audio cutoff")
        else:
            # No audio - just copy video
            cmd = [
                'ffmpeg', '-y',
                '-i', str(video_only_path),  # Video input
                '-c:v', 'copy',              # Copy video codec
                output_path
            ]
            logger.info(f"Creating silent video for scene {segment.scene_number}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg audio merge failed: {result.stderr}")
        
        # Clean up temporary files
        for seg_path in scene_segments:
            try:
                os.remove(seg_path)
            except:
                pass
        
        self.logger.info(f"Created scene video: {output_path}")
        return output_path
    
    def create_final_video(self, session_path: str, output_path: Optional[str] = None) -> str:
        """
        Create the final video by combining all scenes
        
        Args:
            session_path: Path to the session directory
            output_path: Optional output path. If None, uses session directory
            
        Returns:
            Path to the final video file
        """
        session_path = Path(session_path)
        
        if output_path is None:
            # Create title-based filename
            video_title = self._get_video_title(session_path)
            sanitized_title = self._sanitize_filename(video_title)
            title_filename = f"{sanitized_title}.mp4"
            
            output_path = session_path / title_filename
            
            # Also create legacy path for backward compatibility
            legacy_path = session_path / "final_video.mp4"
        else:
            output_path = Path(output_path)
            legacy_path = None
        
        # Analyze session content
        segments = self.analyze_session_content(str(session_path))
        
        if not segments:
            logger.warning("No scenes with both images and audio found, trying to create video with available content")
            # Try to create video with just images (silent video)
            segments = self._create_silent_video_segments(str(session_path))
            if not segments:
                raise ValueError("No valid scenes found in session - no images or audio available")
        
        self.logger.info(f"Creating video from {len(segments)} scenes")
        
        # Create temporary directory
        temp_dir = session_path / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        # Create video for each scene
        scene_videos = []
        for segment in segments:
            scene_output = temp_dir / f"scene_{segment.scene_number}.mp4"
            self.create_scene_video(segment, str(scene_output))
            scene_videos.append(str(scene_output))
        
        # Combine all scene videos
        if len(scene_videos) == 1:
            # Only one scene, just copy it
            cmd = ['cp', scene_videos[0], str(output_path)]
            subprocess.run(cmd)
        else:
            # Create concat file for final video
            concat_file = temp_dir / "final_concat.txt"
            with open(concat_file, 'w') as f:
                for video_path in scene_videos:
                    # Use absolute paths for concat file
                    abs_path = Path(video_path).resolve()
                    f.write(f"file '{abs_path}'\n")
            
            # Concatenate all scene videos
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Final video creation failed: {result.stderr}")
        
        # Clean up temporary files
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass
        
        # Get final video info
        duration = self.get_video_duration(str(output_path))
        file_size = output_path.stat().st_size
        
        # Create legacy symlink for backward compatibility
        if legacy_path and not legacy_path.exists():
            try:
                import os
                os.symlink(output_path.name, legacy_path)
                self.logger.debug(f"Created legacy symlink: {legacy_path}")
            except Exception as e:
                self.logger.warning(f"Failed to create legacy symlink: {e}")
        
        # Enhanced logging with clear file link
        self.logger.info(f"🎉 ✅ VIDEO CREATION COMPLETED! 🎉")
        self.logger.info(f"📁 Full Path: {output_path.absolute()}")
        self.logger.info(f"🎬 File: {output_path.name}")
        self.logger.info(f"📊 Duration: {duration:.2f} seconds")
        self.logger.info(f"💾 File size: {file_size / (1024*1024):.2f} MB")
        self.logger.info(f"🔗 Open with: open '{output_path.absolute()}'")
        self.logger.info(f"📂 Session folder: {output_path.parent}")
        
        return str(output_path)
    
    def _get_video_title(self, session_path: Path) -> str:
        """Extract video title from session metadata"""
        try:
            # Try to get title from full_script.json
            full_script_path = session_path / "full_script.json"
            if full_script_path.exists():
                with open(full_script_path, 'r', encoding='utf-8') as f:
                    script_data = json.load(f)
                    title = script_data.get('title', 'Untitled_Video')
                    if title and title != 'Untitled_Video':
                        return title
            
            # Try to get title from metadata.json
            metadata_path = session_path / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    title = metadata.get('title', 'Untitled_Video')
                    if title and title != 'Untitled_Video':
                        return title
            
            # Fallback to session folder name
            return session_path.name
            
        except Exception as e:
            self.logger.warning(f"Failed to extract video title: {e}")
            return "Untitled_Video"
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize title for use as filename"""
        import re
        
        # Remove or replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', title)
        sanitized = re.sub(r'[^\w\s-]', '', sanitized)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        
        # Limit length to 50 characters
        if len(sanitized) > 50:
            sanitized = sanitized[:50].rstrip('_')
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "Untitled_Video"
            
        return sanitized
    
    def get_video_duration(self, video_path: str) -> float:
        """Get the duration of a video file"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return 0.0
            
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except:
            return 0.0
    
    def create_video_metadata(self, session_path: str, video_path: str) -> Dict:
        """
        Create metadata for the generated video
        
        Args:
            session_path: Path to the session directory
            video_path: Path to the generated video
            
        Returns:
            Dictionary with video metadata
        """
        segments = self.analyze_session_content(session_path)
        video_duration = self.get_video_duration(video_path)
        file_size = Path(video_path).stat().st_size
        
        metadata = {
            "video_file": video_path,
            "total_duration": video_duration,
            "file_size_bytes": file_size,
            "scenes_count": len(segments),
            "creation_timestamp": os.path.getmtime(video_path),
            "scenes": []
        }
        
        for segment in segments:
            scene_info = {
                "scene_number": segment.scene_number,
                "voice_duration": segment.voice_duration,
                "images_count": len(segment.images),
                "image_timings": [
                    {
                        "frame_id": timing.frame_id,
                        "start_time": timing.start_time,
                        "duration": timing.duration,
                        "image_path": timing.image_path
                    }
                    for timing in segment.image_timings
                ]
            }
            metadata["scenes"].append(scene_info)
        
        # Save metadata
        metadata_path = Path(session_path) / "video_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata

if __name__ == "__main__":
    # Test the Video Maker Agent
    logging.basicConfig(level=logging.INFO)
    
    agent = VideoMakerAgent()
    
    # Test with mock output
    test_session = "./tests/mock_output"
    if os.path.exists(test_session):
        try:
            video_path = agent.create_final_video(test_session)
            metadata = agent.create_video_metadata(test_session, video_path)
            print(f"✅ Test video created: {video_path}")
            print(f"📊 Metadata: {metadata}")
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print(f"❌ Test session not found: {test_session}")
