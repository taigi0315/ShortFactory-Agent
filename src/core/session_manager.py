"""
Session Manager for ShortFactory Agent
Manages UUID-based sessions and file storage structure
"""

import os
import uuid
import json
import shutil
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manages sessions and file storage for ShortFactory Agent
    
    Session Structure:
    sessions/
    └── {session_id}/
        ├── script.json              # Main script file
        ├── images/                  # Generated images
        │   ├── scene_1.png
        │   ├── scene_2.png
        │   └── ...
        ├── videos/                  # Generated videos
        │   ├── scene_1.mp4
        │   ├── scene_2.mp4
        │   └── ...
        ├── audios/                  # Generated audios
        │   ├── scene_1.wav
        │   ├── scene_2.wav
        │   └── ...
        ├── metadata.json           # Session metadata
        └── logs/                   # Session logs
            └── session.log
    """
    
    def __init__(self, base_dir: str = "sessions"):
        """
        Initialize Session Manager
        
        Args:
            base_dir: Base directory for all sessions
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        logger.info(f"Session Manager initialized with base directory: {self.base_dir}")
    
    def create_session(self, subject: str, language: str = "English") -> str:
        """
        Create a new session with unique UUID
        
        Args:
            subject: The subject/topic for the session
            language: Target language
            
        Returns:
            str: Session ID (UUID)
        """
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create session directory
        session_dir = self.base_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (session_dir / "images").mkdir(exist_ok=True)
        (session_dir / "videos").mkdir(exist_ok=True)
        (session_dir / "audios").mkdir(exist_ok=True)
        (session_dir / "logs").mkdir(exist_ok=True)
        
        # Create metadata
        metadata = {
            "session_id": session_id,
            "subject": subject,
            "language": language,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "files": {
                "script": None,
                "images": [],
                "videos": [],
                "audios": []
            },
            "progress": {
                "script_generated": False,
                "images_generated": 0,
                "videos_generated": 0,
                "audios_generated": 0,
                "total_scenes": 0
            }
        }
        
        # Save metadata
        metadata_path = session_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create session log
        log_path = session_dir / "logs" / "session.log"
        with open(log_path, 'w') as f:
            f.write(f"Session {session_id} created at {datetime.now().isoformat()}\n")
            f.write(f"Subject: {subject}\n")
            f.write(f"Language: {language}\n")
        
        logger.info(f"Created new session: {session_id}")
        logger.info(f"Session directory: {session_dir}")
        
        return session_id
    
    def get_session_dir(self, session_id: str) -> Path:
        """
        Get session directory path
        
        Args:
            session_id: Session ID
            
        Returns:
            Path: Session directory path
        """
        return self.base_dir / session_id
    
    def save_script(self, session_id: str, script_data: Dict[str, Any]) -> str:
        """
        Save script to session
        
        Args:
            session_id: Session ID
            script_data: Script data (VideoScript object or dict)
            
        Returns:
            str: Path to saved script file
        """
        session_dir = self.get_session_dir(session_id)
        script_path = session_dir / "script.json"
        
        # Convert to dict if it's a Pydantic model
        if hasattr(script_data, 'model_dump'):
            script_dict = script_data.model_dump()
        else:
            script_dict = script_data
        
        # Save script
        with open(script_path, 'w') as f:
            json.dump(script_dict, f, indent=2)
        
        # Update metadata
        self._update_metadata(session_id, {
            "files.script": str(script_path),
            "progress.script_generated": True,
            "progress.total_scenes": len(script_dict.get('scenes', []))
        })
        
        # Log
        self._log(session_id, f"Script saved: {script_path}")
        
        logger.info(f"Script saved for session {session_id}: {script_path}")
        return str(script_path)
    
    def save_image(self, session_id: str, scene_number: int, image_data: bytes, format: str = "png") -> str:
        """
        Save generated image to session
        
        Args:
            session_id: Session ID
            scene_number: Scene number
            image_data: Image data (bytes)
            format: Image format (png, jpg, etc.)
            
        Returns:
            str: Path to saved image file
        """
        session_dir = self.get_session_dir(session_id)
        image_path = session_dir / "images" / f"scene_{scene_number}.{format}"
        
        # Save image
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        # Update metadata
        self._update_metadata(session_id, {
            f"files.images": self._get_metadata_value(session_id, "files.images") + [str(image_path)],
            "progress.images_generated": self._get_metadata_value(session_id, "progress.images_generated") + 1
        })
        
        # Log
        self._log(session_id, f"Image saved: {image_path}")
        
        logger.info(f"Image saved for session {session_id}: {image_path}")
        return str(image_path)
    
    def save_video(self, session_id: str, scene_number: int, video_data: bytes, format: str = "mp4") -> str:
        """
        Save generated video to session
        
        Args:
            session_id: Session ID
            scene_number: Scene number
            video_data: Video data (bytes)
            format: Video format (mp4, avi, etc.)
            
        Returns:
            str: Path to saved video file
        """
        session_dir = self.get_session_dir(session_id)
        video_path = session_dir / "videos" / f"scene_{scene_number}.{format}"
        
        # Save video
        with open(video_path, 'wb') as f:
            f.write(video_data)
        
        # Update metadata
        self._update_metadata(session_id, {
            f"files.videos": self._get_metadata_value(session_id, "files.videos") + [str(video_path)],
            "progress.videos_generated": self._get_metadata_value(session_id, "progress.videos_generated") + 1
        })
        
        # Log
        self._log(session_id, f"Video saved: {video_path}")
        
        logger.info(f"Video saved for session {session_id}: {video_path}")
        return str(video_path)
    
    def save_audio(self, session_id: str, scene_number: int, audio_data: bytes, format: str = "wav") -> str:
        """
        Save generated audio to session
        
        Args:
            session_id: Session ID
            scene_number: Scene number
            audio_data: Audio data (bytes)
            format: Audio format (wav, mp3, etc.)
            
        Returns:
            str: Path to saved audio file
        """
        session_dir = self.get_session_dir(session_id)
        audio_path = session_dir / "audios" / f"scene_{scene_number}.{format}"
        
        # Save audio
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        # Update metadata
        self._update_metadata(session_id, {
            f"files.audios": self._get_metadata_value(session_id, "files.audios") + [str(audio_path)],
            "progress.audios_generated": self._get_metadata_value(session_id, "progress.audios_generated") + 1
        })
        
        # Log
        self._log(session_id, f"Audio saved: {audio_path}")
        
        logger.info(f"Audio saved for session {session_id}: {audio_path}")
        return str(audio_path)
    
    def get_session_metadata(self, session_id: str) -> Dict[str, Any]:
        """
        Get session metadata
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict: Session metadata
        """
        session_dir = self.get_session_dir(session_id)
        metadata_path = session_dir / "metadata.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Session {session_id} not found")
        
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def list_sessions(self) -> list:
        """
        List all sessions
        
        Returns:
            list: List of session IDs
        """
        sessions = []
        for session_dir in self.base_dir.iterdir():
            if session_dir.is_dir() and (session_dir / "metadata.json").exists():
                sessions.append(session_dir.name)
        return sorted(sessions, reverse=True)  # Most recent first
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get session status and progress
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict: Session status
        """
        metadata = self.get_session_metadata(session_id)
        return {
            "session_id": session_id,
            "subject": metadata["subject"],
            "created_at": metadata["created_at"],
            "status": metadata["status"],
            "progress": metadata["progress"],
            "files": metadata["files"]
        }
    
    def _update_metadata(self, session_id: str, updates: Dict[str, Any]):
        """Update session metadata"""
        session_dir = self.get_session_dir(session_id)
        metadata_path = session_dir / "metadata.json"
        
        # Load current metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Apply updates
        for key, value in updates.items():
            keys = key.split('.')
            current = metadata
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        
        # Save updated metadata
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _get_metadata_value(self, session_id: str, key: str) -> Any:
        """Get value from metadata using dot notation"""
        metadata = self.get_session_metadata(session_id)
        keys = key.split('.')
        current = metadata
        for k in keys:
            current = current[k]
        return current
    
    def _log(self, session_id: str, message: str):
        """Add log entry to session"""
        session_dir = self.get_session_dir(session_id)
        log_path = session_dir / "logs" / "session.log"
        
        with open(log_path, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    
    def cleanup_session(self, session_id: str):
        """Delete session and all its files"""
        session_dir = self.get_session_dir(session_id)
        if session_dir.exists():
            shutil.rmtree(session_dir)
            logger.info(f"Session {session_id} cleaned up")
    
    def export_session(self, session_id: str, export_path: str):
        """Export session to zip file"""
        session_dir = self.get_session_dir(session_id)
        shutil.make_archive(export_path, 'zip', session_dir)
        logger.info(f"Session {session_id} exported to {export_path}.zip")


# Example usage and testing
if __name__ == "__main__":
    # Create session manager
    session_manager = SessionManager()
    
    # Test session creation
    print("🧪 Testing Session Manager")
    print("=" * 40)
    
    # Create a test session
    session_id = session_manager.create_session(
        subject="How Elon Musk became CEO of Tesla",
        language="English"
    )
    
    print(f"✅ Created session: {session_id}")
    
    # Get session status
    status = session_manager.get_session_status(session_id)
    print(f"📊 Session status: {status}")
    
    # List all sessions
    sessions = session_manager.list_sessions()
    print(f"📁 All sessions: {sessions}")
    
    # Test file paths
    session_dir = session_manager.get_session_dir(session_id)
    print(f"📂 Session directory: {session_dir}")
    print(f"🖼️  Images directory: {session_dir / 'images'}")
    print(f"🎬 Videos directory: {session_dir / 'videos'}")
    print(f"🔊 Audios directory: {session_dir / 'audios'}")
    
    print("\n✅ Session Manager test completed!")
