"""
Voice Generate Agent - New Architecture
Generates voice audio files using ElevenLabs API from Scene Script Writer dialogue.
"""

import os
import json
import logging
import time
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceGenerateAgent:
    """
    Voice Generate Agent - New Architecture
    
    Mission: Generate voice audio files from Scene Script Writer dialogue
    using ElevenLabs API with the specified elevenlabs_settings.
    """
    
    def __init__(self):
        """Initialize Voice Generate Agent"""
        # Get ElevenLabs API credentials from environment
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID')
        
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is required in .env file")
        if not self.voice_id:
            raise ValueError("ELEVENLABS_VOICE_ID is required in .env file")
        
        # ElevenLabs API endpoint
        self.base_url = "https://api.elevenlabs.io/v1"
        
        logger.info("Voice Generate Agent initialized with ElevenLabs API")
        logger.info(f"Voice ID: {self.voice_id}")
    
    def _save_voice_metadata(self, session_id: str, scene_number: int, voice_data: Dict[str, Any]):
        """Save voice generation metadata to session directory"""
        try:
            session_dir = Path(f"sessions/{session_id}")
            prompts_dir = session_dir / "prompts"
            prompts_dir.mkdir(parents=True, exist_ok=True)
            
            # Save voice metadata
            metadata_file = prompts_dir / f"voice_generate_scene_{scene_number}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(voice_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved voice metadata for scene {scene_number} to {prompts_dir}")
            
        except Exception as e:
            logger.error(f"Failed to save voice metadata for scene {scene_number}: {str(e)}")
    
    async def generate_voices_for_session(self, 
                                        session_id: str, 
                                        scene_packages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate voice files for all scenes in a session
        
        Args:
            session_id: Session ID for file organization
            scene_packages: List of scene packages from Scene Script Writer
            
        Returns:
            List[Dict]: List of voice asset metadata
        """
        try:
            logger.info(f"Generating voice files for {len(scene_packages)} scenes")
            
            # Create voices directory in session
            session_dir = Path(f"sessions/{session_id}")
            voices_dir = session_dir / "voices"
            voices_dir.mkdir(parents=True, exist_ok=True)
            
            voice_assets = []
            
            for scene_package in scene_packages:
                try:
                    scene_number = scene_package.get('scene_number', 1)
                    logger.info(f"Generating voice for scene {scene_number}")
                    
                    # Generate voice for this scene
                    voice_asset = await self._generate_voice_for_scene(
                        scene_package=scene_package,
                        session_id=session_id,
                        voices_dir=voices_dir
                    )
                    
                    if voice_asset:
                        voice_assets.append(voice_asset)
                        logger.info(f"✅ Generated voice for scene {scene_number}")
                    else:
                        logger.warning(f"⚠️ Failed to generate voice for scene {scene_number}")
                        
                except Exception as e:
                    logger.error(f"❌ Error generating voice for scene {scene_package.get('scene_number', 'unknown')}: {str(e)}")
            
            # Save voice assets metadata
            assets_file = session_dir / "voice_assets.json"
            with open(assets_file, 'w', encoding='utf-8') as f:
                json.dump(voice_assets, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Voice generation completed: {len(voice_assets)} voice files")
            return voice_assets
            
        except Exception as e:
            logger.error(f"Error generating voices for session: {str(e)}")
            raise
    
    async def _generate_voice_for_scene(self, 
                                      scene_package: Dict[str, Any], 
                                      session_id: str,
                                      voices_dir: Path) -> Optional[Dict[str, Any]]:
        """Generate voice file for a single scene"""
        try:
            scene_number = scene_package.get('scene_number', 1)
            narration_script = scene_package.get('narration_script', [])
            tts_settings = scene_package.get('tts', {})
            
            # Extract dialogue text
            dialogue_text = self._extract_dialogue_text(narration_script)
            
            if not dialogue_text.strip():
                logger.warning(f"No dialogue text found for scene {scene_number}")
                return None
            
            # Get ElevenLabs settings
            elevenlabs_settings = tts_settings.get('elevenlabs_settings', {})
            
            # Validate ElevenLabs settings
            validated_settings = self._validate_elevenlabs_settings(elevenlabs_settings)
            
            logger.info(f"Generating voice for scene {scene_number} with text: {dialogue_text[:100]}...")
            logger.info(f"Using ElevenLabs settings: {validated_settings}")
            
            # Generate voice using ElevenLabs API
            voice_file_path = voices_dir / f"scene_{scene_number:02d}_voice.mp3"
            
            success = await self._call_elevenlabs_api(
                text=dialogue_text,
                voice_id=self.voice_id,
                settings=validated_settings,
                output_path=voice_file_path
            )
            
            if success:
                # Create voice asset metadata
                voice_asset = {
                    'scene_number': scene_number,
                    'voice_file': str(voice_file_path),
                    'text_used': dialogue_text,
                    'voice_id': self.voice_id,
                    'elevenlabs_settings': validated_settings,
                    'tts_engine': tts_settings.get('engine', 'elevenlabs'),
                    'language': tts_settings.get('language', 'en-US'),
                    'generation_time': time.time(),
                    'file_size_bytes': voice_file_path.stat().st_size if voice_file_path.exists() else 0
                }
                
                # Save metadata
                self._save_voice_metadata(session_id, scene_number, voice_asset)
                
                return voice_asset
            else:
                logger.error(f"Failed to generate voice for scene {scene_number}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating voice for scene {scene_package.get('scene_number', 'unknown')}: {str(e)}")
            return None
    
    def _extract_dialogue_text(self, narration_script: List[Dict[str, Any]]) -> str:
        """Extract dialogue text from narration script"""
        try:
            dialogue_lines = []
            
            for item in narration_script:
                if isinstance(item, dict) and 'line' in item:
                    line = item['line'].strip()
                    if line:
                        dialogue_lines.append(line)
                elif isinstance(item, str):
                    line = item.strip()
                    if line:
                        dialogue_lines.append(line)
            
            # Join with appropriate pauses
            dialogue_text = ". ".join(dialogue_lines)
            
            logger.info(f"Extracted dialogue text: {len(dialogue_text)} characters")
            return dialogue_text
            
        except Exception as e:
            logger.error(f"Error extracting dialogue text: {str(e)}")
            return ""
    
    def _validate_elevenlabs_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize ElevenLabs settings"""
        try:
            # Default settings
            default_settings = {
                'stability': 0.35,
                'similarity_boost': 0.8,
                'style': 0.85,
                'speed': 1.08,
                'loudness': 0.2
            }
            
            # Merge with provided settings
            validated = default_settings.copy()
            validated.update(settings)
            
            # Validate ranges
            for key, value in validated.items():
                if key in ['stability', 'similarity_boost', 'style', 'loudness']:
                    validated[key] = max(0.0, min(1.0, float(value)))
                elif key == 'speed':
                    validated[key] = max(0.7, min(1.3, float(value)))
            
            logger.info(f"Validated ElevenLabs settings: {validated}")
            return validated
            
        except Exception as e:
            logger.error(f"Error validating ElevenLabs settings: {str(e)}")
            # Return safe defaults
            return {
                'stability': 0.35,
                'similarity_boost': 0.8,
                'style': 0.85,
                'speed': 1.08,
                'loudness': 0.2
            }
    
    async def _call_elevenlabs_api(self, 
                                 text: str, 
                                 voice_id: str, 
                                 settings: Dict[str, Any],
                                 output_path: Path) -> bool:
        """Call ElevenLabs API to generate voice"""
        try:
            # Prepare API request
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            # Prepare request body
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": settings.get('stability', 0.35),
                    "similarity_boost": settings.get('similarity_boost', 0.8),
                    "style": settings.get('style', 0.85),
                    "use_speaker_boost": True
                }
            }
            
            logger.info(f"Calling ElevenLabs API for voice generation...")
            logger.info(f"Text length: {len(text)} characters")
            logger.info(f"Voice settings: {data['voice_settings']}")
            
            # Make API request
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                # Save audio file
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = output_path.stat().st_size
                logger.info(f"✅ Voice file saved: {output_path} ({file_size} bytes)")
                return True
            else:
                logger.error(f"❌ ElevenLabs API error: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error calling ElevenLabs API: {str(e)}")
            return False
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get information about the configured voice"""
        try:
            url = f"{self.base_url}/voices/{self.voice_id}"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                voice_info = response.json()
                logger.info(f"Voice info retrieved: {voice_info.get('name', 'Unknown')}")
                return voice_info
            else:
                logger.error(f"Failed to get voice info: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting voice info: {str(e)}")
            return {}
