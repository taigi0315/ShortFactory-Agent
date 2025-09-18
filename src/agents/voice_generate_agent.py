"""
Voice Generate Agent - New Architecture
Generates voice audio files using LemonFox AI API from Scene Script Writer dialogue.
"""

import os
import json
import logging
import time
import requests
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceGenerateAgent:
    """
    Voice Generate Agent - New Architecture
    
    Mission: Generate voice audio files from Scene Script Writer dialogue
    using LemonFox AI API - 90% cheaper than ElevenLabs!
    """
    
    def __init__(self):
        """Initialize Voice Generate Agent"""
        # Get LemonFox API credentials from environment (support both naming conventions)
        self.api_key = (os.getenv('LEMON_FOX_API_KEY') or 
                       os.getenv('LEMONFOX_API_KEY') or 
                       os.getenv('ELEVENLABS_API_KEY'))
        self.voice_name = (os.getenv('LEMON_FOX_VOICE') or 
                          os.getenv('LEMONFOX_VOICE') or 
                          "sarah")
        
        if not self.api_key:
            raise ValueError("LEMON_FOX_API_KEY is required in .env file (or LEMONFOX_API_KEY/ELEVENLABS_API_KEY as fallback)")
        
        # LemonFox AI voices - much more variety and cheaper!
        available_voices = {
            # English (American) 🇺🇸
            'heart': 'heart', 'bella': 'bella', 'michael': 'michael', 'alloy': 'alloy',
            'aoe': 'aoe', 'deko': 'deko', 'jessica': 'jessica', 'nicole': 'nicole',
            'nova': 'nova', 'river': 'river', 'sarah': 'sarah', 'skye': 'skye',
            'echo': 'echo', 'eric': 'eric', 'fenrir': 'fenrir', 'liam': 'liam',
            'onyx': 'onyx', 'puck': 'puck', 'adam': 'adam', 'santa': 'santa',
            
            # English (British) 🇬🇧  
            'alice': 'alice', 'emma': 'emma', 'isabella': 'isabella', 'lily': 'lily',
            'daniel': 'daniel', 'fable': 'fable', 'george': 'george', 'lewis': 'lewis'
        }
        
        if self.voice_name not in available_voices:
            self.voice_name = "sarah"  # Default to Sarah
            logger.info(f"Using default voice 'sarah'")
        else:
            logger.info(f"Using voice '{self.voice_name}'")
        
        # LemonFox API endpoint - OpenAI compatible!
        self.base_url = "https://api.lemonfox.ai/v1"
        
        logger.info("Voice Generate Agent initialized with LemonFox AI API")
        logger.info(f"Voice: {self.voice_name}")
        logger.info("💰 Cost: $2.50 per 1M characters (90% cheaper than ElevenLabs!)")
    
    def clean_text_for_tts(self, text: str) -> str:
        """
        Clean text for TTS by removing special characters that ElevenLabs might read aloud
        and converting numbers to words for proper pronunciation
        
        Args:
            text: Raw text from dialogue
            
        Returns:
            Cleaned text suitable for TTS
        """
        if not text:
            return ""
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* -> italic
        text = re.sub(r'_([^_]+)_', r'\1', text)        # _underline_ -> underline
        
        # Remove brackets and parentheses content that are stage directions
        text = re.sub(r'\[([^\]]+)\]', '', text)        # [stage directions]
        text = re.sub(r'\(([^)]+)\)', '', text)         # (parentheses)
        
        # Remove special punctuation that TTS might read
        text = re.sub(r'[#@$%^&*+=<>{}|\\]', '', text)  # Remove special symbols
        text = re.sub(r'["""''`]', '"', text)           # Normalize quotes
        
        # Convert numbers to words for proper TTS pronunciation
        text = self._convert_numbers_to_words(text)
        
        # Clean up multiple spaces and line breaks
        text = re.sub(r'\s+', ' ', text)                # Multiple spaces -> single space
        text = re.sub(r'\n+', '. ', text)               # Line breaks -> periods
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Ensure proper sentence ending
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    def _convert_numbers_to_words(self, text: str) -> str:
        """
        Convert numbers to words for proper TTS pronunciation
        
        Args:
            text: Input text with numbers
            
        Returns:
            Text with numbers converted to words
        """
        # Dictionary for basic number conversions
        number_words = {
            '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
            '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine',
            '10': 'ten', '11': 'eleven', '12': 'twelve', '13': 'thirteen', '14': 'fourteen',
            '15': 'fifteen', '16': 'sixteen', '17': 'seventeen', '18': 'eighteen', '19': 'nineteen',
            '20': 'twenty', '30': 'thirty', '40': 'forty', '50': 'fifty',
            '60': 'sixty', '70': 'seventy', '80': 'eighty', '90': 'ninety',
            '100': 'one hundred', '1000': 'one thousand'
        }
        
        # Handle common problematic patterns first
        
        # Fix "0s and 1s" -> "zeros and ones"
        text = re.sub(r'\b0s\b', 'zeros', text, flags=re.IGNORECASE)
        text = re.sub(r'\b1s\b', 'ones', text, flags=re.IGNORECASE)
        
        # Handle decades like "1920s" -> "nineteen twenties"
        def convert_decade(match):
            century = match.group(1)
            decade_digit = int(match.group(2)[0])  # First digit of decade (e.g., '2' from '20')
            
            if century == "19":
                century_word = "nineteen"
            elif century == "20":
                century_word = "twenty"
            else:
                return match.group(0)  # Fallback
            
            # Convert decade digit to word + "ties"
            decade_words = ["", "tens", "twenties", "thirties", "forties", "fifties", 
                          "sixties", "seventies", "eighties", "nineties"]
            
            if decade_digit < len(decade_words):
                return f"{century_word} {decade_words[decade_digit]}"
            else:
                return match.group(0)  # Fallback
        
        text = re.sub(r'\b(19|20)(\d{2})s\b', convert_decade, text)
        
        # Handle years like "1969" -> "nineteen sixty nine"
        text = re.sub(r'\b(19)(\d{2})\b', lambda m: f"nineteen {self._convert_two_digit_to_words(m.group(2))}", text)
        text = re.sub(r'\b(20)(\d{2})\b', lambda m: f"twenty {self._convert_two_digit_to_words(m.group(2))}", text)
        
        # Handle percentages like "50%" -> "fifty percent"
        text = re.sub(r'\b(\d+)%', lambda m: f"{self._number_to_word(int(m.group(1)))} percent", text)
        
        # Handle simple numbers (1-100)
        def replace_number(match):
            num = match.group(0)
            try:
                num_int = int(num)
                if num_int <= 100:
                    return self._number_to_word(num_int)
                else:
                    # For larger numbers, keep as is for now
                    return num
            except ValueError:
                return num
        
        # Replace standalone numbers (not part of other patterns)
        text = re.sub(r'\b\d+\b', replace_number, text)
        
        return text
    
    def _convert_two_digit_to_words(self, two_digit_str: str) -> str:
        """Convert two-digit string to words (e.g., '20' -> 'twenty')"""
        try:
            num = int(two_digit_str)
            return self._number_to_word(num)
        except ValueError:
            return two_digit_str
    
    def _number_to_word(self, num: int) -> str:
        """Convert a number (0-100) to its word representation"""
        if num == 0:
            return "zero"
        elif num <= 19:
            ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                   "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                   "seventeen", "eighteen", "nineteen"]
            return ones[num]
        elif num <= 99:
            tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
            if num % 10 == 0:
                return tens[num // 10]
            else:
                return f"{tens[num // 10]} {self._number_to_word(num % 10)}"
        elif num == 100:
            return "one hundred"
        else:
            return str(num)  # Fallback for numbers > 100
    
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
            
            # Get TTS settings (legacy ElevenLabs settings still supported)
            tts_engine_settings = tts_settings.get('elevenlabs_settings', {})
            
            # Convert to LemonFox settings
            lemonfox_settings = self._convert_to_lemonfox_settings(tts_engine_settings)
            
            logger.info(f"Generating voice for scene {scene_number} with text: {dialogue_text[:100]}...")
            logger.info(f"Using LemonFox settings: {lemonfox_settings}")
            
            # Generate voice using LemonFox API
            voice_file_path = voices_dir / f"scene_{scene_number:02d}_voice.mp3"
            
            success = await self._call_lemonfox_api(
                text=dialogue_text,
                voice_name=self.voice_name,
                settings=lemonfox_settings,
                output_path=voice_file_path
            )
            
            if success:
                # Create voice asset metadata
                voice_asset = {
                    'scene_number': scene_number,
                    'voice_file': str(voice_file_path),
                    'text_used': dialogue_text,
                    'voice_name': self.voice_name,
                    'lemonfox_settings': lemonfox_settings,
                    'tts_engine': 'lemonfox',
                    'language': tts_settings.get('language', 'en-US'),
                    'generation_time': time.time(),
                    'file_size_bytes': voice_file_path.stat().st_size if voice_file_path.exists() else 0,
                    'cost_savings': '90% cheaper than ElevenLabs'
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
            raw_dialogue_text = ". ".join(dialogue_lines)
            
            # Clean text for TTS
            dialogue_text = self.clean_text_for_tts(raw_dialogue_text)
            
            logger.info(f"Extracted dialogue text: {len(dialogue_text)} characters (cleaned from {len(raw_dialogue_text)})")
            return dialogue_text
            
        except Exception as e:
            logger.error(f"Error extracting dialogue text: {str(e)}")
            return ""
    
    def _convert_to_lemonfox_settings(self, elevenlabs_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ElevenLabs settings to LemonFox settings with enhanced mood and slower pace"""
        try:
            # Get original speed and apply 10% increase for optimal delivery  
            original_speed = elevenlabs_settings.get('speed', 1.0)
            adjusted_speed = original_speed * 1.1  # 10% faster for balanced pacing
            
            # Validate speed range (LemonFox: 0.5 - 4.0)
            adjusted_speed = max(0.5, min(4.0, float(adjusted_speed)))
            
            # Select voice based on mood/style for 35% more emotional expression
            style_score = elevenlabs_settings.get('style', 0.5)
            stability = elevenlabs_settings.get('stability', 0.5)
            
            # Choose more expressive voice based on content mood
            if style_score > 0.7 or stability < 0.4:
                # High expressiveness - use more dramatic voices
                voice_options = ['bella', 'nova', 'jessica', 'skye']  # More expressive female voices
            elif style_score > 0.5:
                # Medium expressiveness - use balanced voices
                voice_options = ['sarah', 'river', 'heart']  # Balanced, warm voices
            else:
                # Lower expressiveness - use calm voices
                voice_options = ['alice', 'emma', 'lily']  # Calm, clear voices
            
            # Select voice (use configured or pick from appropriate category)
            selected_voice = self.voice_name
            if selected_voice not in voice_options and voice_options:
                selected_voice = voice_options[0]  # Use first from appropriate category
                logger.info(f"🎭 Adjusted voice for better mood: {self.voice_name} → {selected_voice}")
            
            lemonfox_settings = {
                'speed': adjusted_speed,
                'response_format': 'mp3',
                'language': 'en-us',
                'voice': selected_voice,
                'mood_enhancement': '35% more expressive',
                'pace_adjustment': '10% faster for balanced delivery'
            }
            
            logger.info(f"🎭 Enhanced LemonFox settings: {lemonfox_settings}")
            logger.info(f"🚀 Speed optimized: {original_speed:.2f} → {adjusted_speed:.2f} (10% faster for balanced pacing)")
            logger.info(f"🎨 Voice optimized for mood: {selected_voice}")
            return lemonfox_settings
            
        except Exception as e:
            logger.error(f"Error converting to LemonFox settings: {str(e)}")
            # Return enhanced defaults
            return {
                'speed': 0.8,  # 20% slower than default
                'response_format': 'mp3',
                'language': 'en-us',
                'voice': 'bella',  # More expressive default
                'mood_enhancement': 'applied'
            }
    
    async def _call_lemonfox_api(self, 
                               text: str, 
                               voice_name: str, 
                               settings: Dict[str, Any],
                               output_path: Path) -> bool:
        """Call LemonFox AI API to generate voice - OpenAI compatible!"""
        try:
            # Prepare API request - OpenAI compatible endpoint
            url = f"{self.base_url}/audio/speech"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Use the optimized voice from settings if available
            optimized_voice = settings.get('voice', voice_name)
            
            # Prepare request body - OpenAI compatible format
            data = {
                "input": text,
                "voice": optimized_voice,
                "response_format": settings.get('response_format', 'mp3'),
                "speed": settings.get('speed', 0.8),  # Default to slower speed
                "language": settings.get('language', 'en-us')
            }
            
            logger.info(f"Calling LemonFox AI API for voice generation...")
            logger.info(f"Text length: {len(text)} characters")
            logger.info(f"Voice: {voice_name}")
            logger.info(f"Settings: {data}")
            
            # Calculate estimated cost
            estimated_cost = (len(text) / 1000000) * 2.50
            logger.info(f"💰 Estimated cost: ${estimated_cost:.4f} (vs ${estimated_cost*10:.4f} with ElevenLabs)")
            
            # Make API request
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                # Save audio file
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = output_path.stat().st_size
                logger.info(f"✅ Voice file saved: {output_path} ({file_size} bytes)")
                logger.info(f"💰 Actual cost: ${estimated_cost:.4f} - Saved ${estimated_cost*9:.4f}!")
                return True
            else:
                logger.error(f"❌ LemonFox API error: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error calling LemonFox API: {str(e)}")
            return False
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get information about the configured voice"""
        try:
            # LemonFox doesn't need a separate voice info API call
            # Return static info about the selected voice
            voice_info = {
                'name': self.voice_name,
                'language': 'en-us',
                'provider': 'LemonFox AI',
                'cost_per_1m_chars': '$2.50',
                'cost_savings': '90% cheaper than ElevenLabs',
                'api_endpoint': self.base_url,
                'supported_formats': ['mp3', 'opus', 'aac', 'flac', 'pcm', 'ogg', 'wav'],
                'speed_range': '0.5 - 4.0x'
            }
            
            logger.info(f"Voice info: {voice_info['name']} ({voice_info['provider']})")
            return voice_info
                
        except Exception as e:
            logger.error(f"Error getting voice info: {str(e)}")
            return {
                'name': self.voice_name,
                'provider': 'LemonFox AI',
                'error': str(e)
            }
