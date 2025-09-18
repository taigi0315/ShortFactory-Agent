"""
Robust JSON Parser with Pydantic Integration
Handles common JSON parsing issues from AI-generated responses
"""

import json
import re
import logging
from typing import Any, Dict, Optional, Type, TypeVar, Union
from pydantic import BaseModel, ValidationError
from pathlib import Path

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class JSONParsingError(Exception):
    """Custom exception for JSON parsing errors"""
    def __init__(self, message: str, original_error: Optional[Exception] = None, raw_content: Optional[str] = None):
        super().__init__(message)
        self.original_error = original_error
        self.raw_content = raw_content

class RobustJSONParser:
    """
    Robust JSON parser that handles common issues with AI-generated JSON responses
    """
    
    @staticmethod
    def extract_json_from_response(response_text: str) -> str:
        """
        Extract JSON content from AI response text
        
        Args:
            response_text: Raw response text from AI
            
        Returns:
            str: Extracted JSON string
            
        Raises:
            JSONParsingError: If no valid JSON boundaries are found
        """
        if not response_text or not response_text.strip():
            raise JSONParsingError("Empty response text")
        
        # Remove common prefixes/suffixes
        cleaned = response_text.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        # Find JSON boundaries
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise JSONParsingError(
                "No valid JSON boundaries found in response", 
                raw_content=response_text[:500]
            )
        
        # Extract clean JSON
        json_str = cleaned[start_idx:end_idx]
        
        return json_str
    
    @staticmethod
    def repair_json(json_str: str, context_name: str = "unknown") -> str:
        """
        Attempt to repair common JSON syntax errors
        
        Args:
            json_str: JSON string to repair
            context_name: Context for logging (e.g., "scene_5")
            
        Returns:
            str: Repaired JSON string
        """
        logger.info(f"🔧 Attempting JSON repair for {context_name}")
        
        repaired = json_str
        
        # Fix 1: Remove trailing commas (most common issue)
        repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
        
        # Fix 2: Fix missing commas after closing braces/brackets
        repaired = re.sub(r'}(\s*)(["\w])', r'},\1\2', repaired)
        repaired = re.sub(r'](\s*)(["\w])', r'],\1\2', repaired)
        
        # Fix 3: Fix missing commas between array elements
        repaired = re.sub(r'}\s*{', '},{', repaired)
        repaired = re.sub(r']\s*\[', '],[', repaired)
        
        # Fix 4: Handle unterminated strings
        lines = repaired.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check for unterminated string patterns
            if ':' in line and '"' in line:
                quote_count = line.count('"')
                # If odd number of quotes, likely unterminated string
                if quote_count % 2 == 1:
                    # Look for pattern: "key": "unterminated_value
                    match = re.search(r'"([^"]*)":\s*"([^"]*)$', line)
                    if match:
                        line = line + '"'
                        logger.debug(f"🔧 Fixed unterminated string on line {i+1}")
            
            fixed_lines.append(line)
        
        repaired = '\n'.join(fixed_lines)
        
        # Fix 5: Balance braces and brackets
        open_braces = repaired.count('{')
        close_braces = repaired.count('}')
        open_brackets = repaired.count('[')
        close_brackets = repaired.count(']')
        
        if open_braces > close_braces:
            repaired += '}' * (open_braces - close_braces)
            logger.debug(f"🔧 Added {open_braces - close_braces} closing braces")
        elif close_braces > open_braces:
            repaired = '{' * (close_braces - open_braces) + repaired
            logger.debug(f"🔧 Added {close_braces - open_braces} opening braces")
            
        if open_brackets > close_brackets:
            repaired += ']' * (open_brackets - close_brackets)
            logger.debug(f"🔧 Added {open_brackets - close_brackets} closing brackets")
        elif close_brackets > open_brackets:
            repaired = '[' * (close_brackets - open_brackets) + repaired
            logger.debug(f"🔧 Added {close_brackets - open_brackets} opening brackets")
        
        # Fix 6: Handle truncated JSON more aggressively
        repaired = repaired.strip()
        
        # Remove incomplete final line if it exists
        lines = repaired.split('\n')
        if lines and not lines[-1].strip().endswith((',', '}', ']', '"')):
            # Last line looks incomplete, remove it
            repaired = '\n'.join(lines[:-1])
            logger.debug("🔧 Removed incomplete final line")
        
        # Balance braces and brackets
        if not repaired.endswith('}') and not repaired.endswith(']'):
            open_braces = repaired.count('{')
            close_braces = repaired.count('}')
            open_brackets = repaired.count('[')
            close_brackets = repaired.count(']')
            
            # Add missing closing braces
            if open_braces > close_braces:
                repaired += '}' * (open_braces - close_braces)
                logger.debug(f"🔧 Added {open_braces - close_braces} closing braces for truncated JSON")
                
            # Add missing closing brackets  
            if open_brackets > close_brackets:
                repaired += ']' * (open_brackets - close_brackets)
                logger.debug(f"🔧 Added {open_brackets - close_brackets} closing brackets for truncated JSON")
        
        # Fix 7: Remove control characters except newlines and tabs
        repaired = ''.join(char for char in repaired if ord(char) >= 32 or char in '\n\t\r')
        
        logger.info(f"🔧 JSON repair completed for {context_name}")
        return repaired
    
    @staticmethod
    def normalize_data(data: Dict[str, Any], context_name: str = "unknown") -> Dict[str, Any]:
        """
        Normalize data to fix common AI generation issues
        
        Args:
            data: Parsed JSON data
            context_name: Context for logging
            
        Returns:
            Dict[str, Any]: Normalized data
        """
        logger.debug(f"🔧 Normalizing data for {context_name}")
        
        # Normalize transition values
        transition_mapping = {
            'cut_to_black': 'cut',
            'cut to black': 'cut',
            'cut to black, then reveal': 'cut',
            'morphing diagram': 'morph',
            'swirling genetic sequence': 'dissolve',
            'fade to a thoughtful Glowbie': 'fade',
            'fade to credits': 'credits',
            'fade_to_black': 'fade',
            'fade_to_credits': 'credits',
            'swipe_left': 'wipe',
            'end_screen': 'end',
            'slide_left': 'wipe',
            'slide_right': 'wipe'
        }
        
        # Process scenes if they exist (for FullScript)
        if 'scenes' in data and isinstance(data['scenes'], list):
            for scene in data['scenes']:
                if isinstance(scene, dict) and 'transition_to_next' in scene:
                    original_transition = scene['transition_to_next']
                    normalized_transition = transition_mapping.get(original_transition, original_transition)
                    
                    if normalized_transition != original_transition:
                        logger.debug(f"🔧 Normalized transition '{original_transition}' -> '{normalized_transition}'")
                        scene['transition_to_next'] = normalized_transition
                    
                    # Ensure it's one of the valid values
                    valid_transitions = ['cut', 'fade', 'wipe', 'morph', 'dissolve', 'credits', 'end']
                    if scene['transition_to_next'] not in valid_transitions:
                        logger.warning(f"⚠️ Invalid transition '{scene['transition_to_next']}', defaulting to 'fade'")
                        scene['transition_to_next'] = 'fade'
        
        # Process SFX cues if they exist (for ScenePackage)
        if 'sfx_cues' in data and isinstance(data['sfx_cues'], list):
            for i, sfx in enumerate(data['sfx_cues']):
                if isinstance(sfx, dict):
                    # Map various field names to cue
                    cue_field_names = ['sfx_name', 'effect', 'sound_effect', 'cue_name', 'name']
                    for field_name in cue_field_names:
                        if field_name in sfx and 'cue' not in sfx:
                            sfx['cue'] = sfx.pop(field_name)
                            logger.info(f"🔧 Mapped {field_name} to cue in SFX {i}")
                            break
                    
                    # Map start_ms to at_ms
                    if 'start_ms' in sfx and 'at_ms' not in sfx:
                        sfx['at_ms'] = sfx.pop('start_ms')
                        logger.debug(f"🔧 Mapped start_ms to at_ms in SFX {i}")
                    
                    # Calculate duration_ms from end_ms if available
                    if 'end_ms' in sfx and 'at_ms' in sfx:
                        duration = sfx.pop('end_ms') - sfx['at_ms']
                        sfx['duration_ms'] = max(duration, 100)  # Minimum 100ms
                        logger.debug(f"🔧 Calculated duration_ms from end_ms in SFX {i}")
                    elif 'duration_ms' not in sfx:
                        sfx['duration_ms'] = 1000  # Default 1 second duration
                        logger.debug(f"🔧 Added default duration_ms to SFX {i}")
                    
                    # Remove extra fields that aren't in our schema
                    extra_fields = ['volume', 'fade_in_ms', 'fade_out_ms', 'end_ms']
                    for field in extra_fields:
                        if field in sfx:
                            sfx.pop(field)
                            logger.debug(f"🔧 Removed extra field '{field}' from SFX {i}")
        
        # Process on-screen text if it exists (for ScenePackage)
        if 'on_screen_text' in data and isinstance(data['on_screen_text'], list):
            for i, text_item in enumerate(data['on_screen_text']):
                if isinstance(text_item, dict):
                    # Fix None values in required string fields
                    string_fields = ['text', 'style', 'position']
                    for field in string_fields:
                        if field in text_item and text_item[field] is None:
                            if field == 'text':
                                text_item[field] = f"Text {i+1}"
                            elif field == 'style':
                                text_item[field] = "normal"
                            elif field == 'position':
                                text_item[field] = "center"
                            logger.info(f"🔧 Fixed None value in on-screen text {i}.{field} -> '{text_item[field]}'")
                    
                    # Map start_ms to at_ms
                    if 'start_ms' in text_item and 'at_ms' not in text_item:
                        text_item['at_ms'] = text_item.pop('start_ms')
                        logger.debug(f"🔧 Mapped start_ms to at_ms in on-screen text {i}")
                    
                    # Calculate duration_ms from end_ms if available
                    if 'end_ms' in text_item and 'at_ms' in text_item:
                        duration = text_item.pop('end_ms') - text_item['at_ms']
                        text_item['duration_ms'] = max(duration, 500)  # Minimum 500ms
                        logger.debug(f"🔧 Calculated duration_ms from end_ms in on-screen text {i}")
                    elif 'duration_ms' not in text_item:
                        text_item['duration_ms'] = 3000  # Default 3 seconds duration
                        logger.debug(f"🔧 Added default duration_ms to on-screen text {i}")
                    
                    # Add missing at_ms if not present
                    if 'at_ms' not in text_item:
                        text_item['at_ms'] = 0  # Default to start of scene
                        logger.debug(f"🔧 Added default at_ms to on-screen text {i}")
                    
                    # Remove extra fields that aren't in our schema
                    extra_fields = ['font_size', 'color', 'background_color', 'position', 'animation_in', 'animation_out', 'end_ms']
                    for field in extra_fields:
                        if field in text_item:
                            text_item.pop(field)
                            logger.debug(f"🔧 Removed extra field '{field}' from on-screen text {i}")
        
        # Process ImageAsset fields if they exist
        if 'seed' in data and data['seed'] is None:
            data['seed'] = 123456  # Default seed value
            logger.info("🔧 Fixed None seed value for ImageAsset -> 123456")
        
        if 'cfg' in data and data['cfg'] is None:
            data['cfg'] = 7.5  # Default CFG value
            logger.info("🔧 Fixed None cfg value for ImageAsset -> 7.5")
        
        if 'steps' in data and data['steps'] is None:
            data['steps'] = 20  # Default steps value
            logger.info("🔧 Fixed None steps value for ImageAsset -> 20")
        
        # Fix None values in common string fields
        common_string_fields = {
            'title': 'Untitled',
            'description': 'No description provided',
            'character_name': 'Glowbie',
            'shot_type': 'medium',
            'camera_motion': 'static',
            'lighting': 'natural'
        }
        
        for field, default_value in common_string_fields.items():
            if field in data and data[field] is None:
                data[field] = default_value
                logger.info(f"🔧 Fixed None {field} -> '{default_value}'")
        
        # Fix None values in array fields (ScenePackage)
        array_fields = {
            'dialogue': [],
            'sfx_cues': [],
            'on_screen_text': [],
            'narration_script': [],
            'visuals': [],
            'beats': [],
            'learning_objectives': []
        }
        
        for field, default_value in array_fields.items():
            if field in data and data[field] is None:
                data[field] = default_value
                logger.info(f"🔧 Fixed None {field} -> {default_value} (empty array)")
        
        return data
    
    @staticmethod
    def parse_with_fallback(json_str: str, context_name: str = "unknown") -> Dict[str, Any]:
        """
        Parse JSON with multiple fallback strategies
        
        Args:
            json_str: JSON string to parse
            context_name: Context for logging
            
        Returns:
            Dict[str, Any]: Parsed JSON data
            
        Raises:
            JSONParsingError: If all parsing strategies fail
        """
        original_json = json_str
        
        # Strategy 1: Direct parsing
        try:
            data = json.loads(json_str)
            logger.info(f"✅ Direct JSON parsing successful for {context_name}")
            return data
        except json.JSONDecodeError as e:
            logger.warning(f"Direct parsing failed for {context_name}: {e}")
        
        # Strategy 2: JSON repair then parse
        try:
            repaired_json = RobustJSONParser.repair_json(json_str, context_name)
            data = json.loads(repaired_json)
            logger.info(f"✅ Repaired JSON parsing successful for {context_name}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Repaired parsing also failed for {context_name}: {e}")
        except Exception as e:
            logger.error(f"JSON repair failed for {context_name}: {e}")
        
        # Strategy 3: Try to extract partial valid JSON (with safety limits)
        try:
            # Find the longest valid JSON prefix with step size to prevent infinite loops
            step_size = max(1, len(json_str) // 100)  # Limit to 100 attempts max
            attempts = 0
            max_attempts = 50  # Hard limit to prevent infinite loops
            
            for i in range(len(json_str), 0, -step_size):
                attempts += 1
                if attempts > max_attempts:
                    logger.error(f"❌ Partial JSON extraction exceeded max attempts ({max_attempts}) for {context_name}")
                    break
                    
                try:
                    partial_json = json_str[:i]
                    # Try to balance it
                    balanced = RobustJSONParser.repair_json(partial_json, f"{context_name}_partial_{attempts}")
                    data = json.loads(balanced)
                    logger.warning(f"⚠️ Partial JSON parsing successful for {context_name} (used {i}/{len(json_str)} chars, attempt {attempts})")
                    return data
                except:
                    continue
        except Exception as e:
            logger.error(f"Partial JSON extraction failed for {context_name}: {e}")
        
        # All strategies failed
        raise JSONParsingError(
            f"Failed to parse JSON for {context_name} with all strategies",
            raw_content=original_json[:500]
        )
    
    @staticmethod
    def parse_and_validate(
        response_text: str, 
        model_class: Type[T], 
        context_name: str = "unknown",
        allow_partial: bool = False
    ) -> T:
        """
        Parse JSON response and validate against Pydantic model
        
        Args:
            response_text: Raw response text from AI
            model_class: Pydantic model class to validate against
            context_name: Context for logging
            allow_partial: Whether to allow partial data with defaults
            
        Returns:
            T: Validated Pydantic model instance
            
        Raises:
            JSONParsingError: If parsing or validation fails
        """
        try:
            # Step 1: Extract JSON from response
            json_str = RobustJSONParser.extract_json_from_response(response_text)
            logger.debug(f"Extracted JSON for {context_name}: {json_str[:200]}...")
            
            # Step 2: Parse JSON with fallback strategies
            json_data = RobustJSONParser.parse_with_fallback(json_str, context_name)
            
            # Step 2.5: Normalize data to fix common AI issues
            json_data = RobustJSONParser.normalize_data(json_data, context_name)
            
            # Step 3: Validate against Pydantic model
            try:
                validated_data = model_class.model_validate(json_data)
                logger.info(f"✅ Pydantic validation successful for {context_name}")
                return validated_data
            except ValidationError as e:
                if allow_partial:
                    # Try to create with partial data and defaults
                    try:
                        validated_data = model_class.model_validate(json_data, strict=False)
                        logger.warning(f"⚠️ Partial Pydantic validation successful for {context_name}")
                        return validated_data
                    except ValidationError as e2:
                        logger.error(f"Even partial validation failed for {context_name}: {e2}")
                        raise JSONParsingError(
                            f"Pydantic validation failed for {context_name}: {e2}",
                            original_error=e2,
                            raw_content=response_text[:500]
                        )
                else:
                    logger.error(f"Pydantic validation failed for {context_name}: {e}")
                    raise JSONParsingError(
                        f"Pydantic validation failed for {context_name}: {e}",
                        original_error=e,
                        raw_content=response_text[:500]
                    )
                    
        except JSONParsingError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in parse_and_validate for {context_name}: {e}")
            raise JSONParsingError(
                f"Unexpected error parsing {context_name}: {e}",
                original_error=e,
                raw_content=response_text[:500]
            )
    
    @staticmethod
    def create_fallback_data(model_class: Type[T], context_name: str = "unknown", **kwargs) -> T:
        """
        Create fallback data when parsing completely fails
        
        Args:
            model_class: Pydantic model class
            context_name: Context for logging
            **kwargs: Additional data to include
            
        Returns:
            T: Fallback model instance with minimal required data
        """
        logger.warning(f"Creating fallback data for {context_name}")
        
        # Create minimal required data based on model
        fallback_data = kwargs.copy()
        
        # Add common fallback values based on model type
        if hasattr(model_class, '__name__'):
            model_name = model_class.__name__
            
            if 'ScenePackage' in model_name:
                fallback_data.update({
                    'scene_number': fallback_data.get('scene_number', 1),
                    'narration_script': fallback_data.get('narration_script', [
                        {'line': 'Content generation failed', 'at_ms': 0}
                    ]),
                    'visuals': fallback_data.get('visuals', [
                        {
                            'frame_id': '1A',
                            'shot_type': 'medium',
                            'image_prompt': 'A simple educational scene with a friendly character',
                            'aspect_ratio': '16:9'
                        }
                    ]),
                    'tts': fallback_data.get('tts', {
                        'engine': 'elevenlabs',
                        'voice': 'Adam',
                        'elevenlabs_settings': {
                            'stability': 0.5,
                            'similarity_boost': 0.8,
                            'style': 0.5,
                            'speed': 1.0,
                            'loudness': 0.0
                        }
                    }),
                    'timing': fallback_data.get('timing', {'total_ms': 5000}),
                    'safety_checks': ['fallback_data_used']
                })
            
            elif 'FullScript' in model_name:
                fallback_data.update({
                    'title': fallback_data.get('title', 'Generated Content'),
                    'overall_style': fallback_data.get('overall_style', 'educational'),
                    'story_summary': fallback_data.get('story_summary', 'A brief educational video about the requested topic.'),
                    'scenes': fallback_data.get('scenes', [
                        {
                            'scene_number': 1,
                            'scene_type': 'hook',
                            'beats': ['Introduction to the topic'],
                            'needs_animation': False,
                            'transition_to_next': 'fade',
                            'scene_importance': 5
                        },
                        {
                            'scene_number': 2,
                            'scene_type': 'explanation',
                            'beats': ['Main explanation'],
                            'needs_animation': False,
                            'transition_to_next': 'fade',
                            'scene_importance': 4
                        },
                        {
                            'scene_number': 3,
                            'scene_type': 'summary',
                            'beats': ['Summary and conclusion'],
                            'needs_animation': False,
                            'transition_to_next': 'end',
                            'scene_importance': 3
                        }
                    ])
                })
        
        try:
            return model_class.model_validate(fallback_data)
        except ValidationError as e:
            logger.error(f"Even fallback data validation failed for {context_name}: {e}")
            raise JSONParsingError(
                f"Cannot create valid fallback data for {context_name}: {e}",
                original_error=e
            )

# Convenience functions for specific models
def parse_scene_package(response_text: str, scene_number: int) -> 'ScenePackage':
    """Parse and validate ScenePackage from AI response"""
    from model.models import ScenePackage
    
    return RobustJSONParser.parse_and_validate(
        response_text=response_text,
        model_class=ScenePackage,
        context_name=f"scene_{scene_number}",
        allow_partial=True
    )

def parse_full_script(response_text: str) -> 'FullScript':
    """Parse and validate FullScript from AI response"""
    from model.models import FullScript
    
    return RobustJSONParser.parse_and_validate(
        response_text=response_text,
        model_class=FullScript,
        context_name="full_script",
        allow_partial=True
    )

def parse_image_asset(response_text: str, frame_id: str) -> 'ImageAsset':
    """Parse and validate ImageAsset from AI response"""
    from model.models import ImageAsset
    
    return RobustJSONParser.parse_and_validate(
        response_text=response_text,
        model_class=ImageAsset,
        context_name=f"image_{frame_id}",
        allow_partial=True
    )
