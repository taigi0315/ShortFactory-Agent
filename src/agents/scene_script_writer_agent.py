"""
Scene Script Writer Agent - New Architecture
Takes FSW scene beats and expands them into production-ready scene packages.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from google.adk import Agent
import google.genai as genai
from core.shared_context import SharedContextManager
from core.educational_enhancer import EducationalEnhancer
from core.image_style_selector import ImageStyleSelector
from core.json_parser import RobustJSONParser, JSONParsingError, parse_scene_package
from core.cost_optimizer import CostOptimizer, validate_and_optimize_prompt, validate_response_quality
from model.models import ScenePackage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SceneScriptWriterAgent(Agent):
    """
    Scene Script Writer Agent - New Architecture
    
    Mission: Take each FSW scene beat and expand it into a production-ready scene package:
    - Detailed narration script with timing
    - Visual storyboard with specific prompts
    - TTS settings and voice configuration
    - Sound effects and on-screen text cues
    - Continuity and safety checks
    """
    
    def __init__(self, shared_context_manager: SharedContextManager = None):
        """Initialize Scene Script Writer Agent"""
        # Check if API key is available
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        # Initialize ADK Agent
        super().__init__(
            name="scene_script_writer",
            description="Expands scene beats into production-ready scene packages",
            model="gemini-2.5-flash",
            instruction=self._get_instruction(),
            generate_content_config={
                "temperature": 0.8,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json"
            }
        )
        
        # Store dependencies
        self._shared_context_manager = shared_context_manager or SharedContextManager()
        self._educational_enhancer = EducationalEnhancer()
        self._style_selector = ImageStyleSelector()
        
        logger.info("Scene Script Writer Agent initialized with new architecture")
    
    def _save_prompt_and_response(self, session_id: str, scene_number: int, prompt: str, response: str):
        """Save prompt and response to session directory"""
        try:
            session_dir = Path(f"sessions/{session_id}")
            prompts_dir = session_dir / "prompts"
            prompts_dir.mkdir(parents=True, exist_ok=True)
            
            # Save prompt
            prompt_file = prompts_dir / f"scene_script_writer_scene_{scene_number}_prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            # Save response
            response_file = prompts_dir / f"scene_script_writer_scene_{scene_number}_response.txt"
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(response)
            
            logger.info(f"Saved SSW scene {scene_number} prompt and response to {prompts_dir}")
            
        except Exception as e:
            logger.error(f"Failed to save SSW scene {scene_number} prompt and response: {str(e)}")
    
    def _get_instruction(self) -> str:
        """Get the instruction prompt for the agent"""
        return """
You are the Scene Script Writer (SSW) in a multi-agent video production system.

Your mission is to take high-level scene beats from the Full Script Writer and expand them into production-ready scene packages.

You are responsible for:
- Detailed narration scripts with precise timing
- Visual storyboard with specific image prompts
- TTS/voice settings and configuration
- Sound effects and audio cues
- On-screen text elements
- Continuity and callback elements
- Safety and quality checks

Your output must follow the ScenePackage.json schema exactly.

Key principles:
- ELABORATE on the basic scene content with rich details
- ADD HOOKING elements to maintain viewer engagement
- Use educational metaphors and concrete examples
- Ensure visual consistency with character and style
- Create compelling, detailed image prompts
- Maintain narrative flow and continuity
"""
    
    async def expand_scene(self, 
                          scene_data: Dict[str, Any],
                          global_context: Dict[str, Any],
                          session_id: str,
                          previous_scenes: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Expand a scene beat into a production-ready scene package
        
        Args:
            scene_data: Scene data from FSW (scene_number, scene_type, beats, etc.)
            global_context: Global context (characters, style, constraints, etc.)
            session_id: Session ID for saving prompts/responses
            previous_scenes: Previously generated scenes for continuity
            
        Returns:
            Dict: Scene package following ScenePackage.json schema
        """
        try:
            scene_number = scene_data.get('scene_number', 1)
            scene_type = scene_data.get('scene_type', 'explanation')
            
            logger.info(f"Expanding scene {scene_number} of type {scene_type}")
            
            # Enhance educational content
            try:
                enhanced_content = self._educational_enhancer.enhance_educational_content(
                    scene_data={'beats': scene_data.get('beats', [])},
                    target_audience=global_context.get('target_audience', 'general')
                )
                logger.info(f"Educational content enhanced successfully")
            except Exception as e:
                logger.warning(f"Educational enhancement failed: {str(e)}, proceeding without enhancement")
                # Create a simple fallback
                enhanced_content = type('obj', (object,), {
                    'educational_density': 0.5,
                    'complexity_score': 0.5,
                    'key_concepts': ['general concepts']
                })()
            
            # Create the prompt
            prompt = self._create_ssw_prompt(
                scene_data=scene_data,
                global_context=global_context,
                enhanced_content=enhanced_content,
                previous_scenes=previous_scenes
            )
            
            # Validate and optimize prompt before sending
            is_valid, optimized_prompt, validation_message = validate_and_optimize_prompt(
                prompt, f"scene_{scene_number}"
            )
            
            if not is_valid:
                logger.error(f"❌ Prompt validation failed for scene {scene_number}: {validation_message}")
                raise ValueError(f"Invalid prompt for scene {scene_number}: {validation_message}")
            
            # Log the prompt
            logger.info(f"SSW PROMPT for scene {scene_number}:")
            logger.info(f"Length: {len(optimized_prompt)} (optimized from {len(prompt)})")
            logger.info(f"Validation: {validation_message}")
            
            # Generate response using ADK
            response = await self._simulate_adk_response(optimized_prompt)
            
            if response:
                # Save prompt and response
                self._save_prompt_and_response(session_id, scene_number, prompt, response)
                
                # Parse and validate response using robust JSON parser
                scene_package = self._parse_response_with_pydantic(response, scene_number)
                
                # Add safety checks
                safety_checks = self._run_safety_checks(scene_package)
                scene_package['safety_checks'] = safety_checks
                
                logger.info(f"Scene {scene_number} package generated successfully")
                return scene_package
            else:
                raise ValueError(f"No response received for scene {scene_number}")
                
        except Exception as e:
            logger.error(f"Error expanding scene {scene_number}: {str(e)}")
            raise
    
    def _create_ssw_prompt(self, scene_data: Dict[str, Any], global_context: Dict[str, Any],
                          enhanced_content: Any, previous_scenes: Optional[List[Dict[str, Any]]] = None) -> str:
        """Create the SSW prompt"""
        
        scene_number = scene_data.get('scene_number', 1)
        scene_type = scene_data.get('scene_type', 'explanation')
        beats = scene_data.get('beats') or []
        learning_objectives = scene_data.get('learning_objectives') or []
        needs_animation = scene_data.get('needs_animation', False)
        transition = scene_data.get('transition_to_next', 'fade')
        importance = scene_data.get('scene_importance', 3)
        
        # Context from global
        title = global_context.get('title', '')
        overall_style = global_context.get('overall_style', 'engaging')
        main_character = global_context.get('main_character', 'Glowbie - a cute, blob-like cartoon character')
        cosplay = global_context.get('cosplay_instructions', '')
        story_summary = global_context.get('story_summary', '')
        language = global_context.get('language', 'English')
        
        # Previous scenes context
        continuity_context = ""
        if previous_scenes:
            continuity_context = f"""
CONTINUITY CONTEXT:
Previous scenes have established:
{chr(10).join([f"- Scene {s.get('scene_number', 'N/A')}: {s.get('scene_type', 'N/A')} - Key elements: {', '.join(s.get('callback_tags', []))}" for s in previous_scenes[-2:]])}

Maintain visual and narrative consistency.
"""
        
        # Educational enhancement info
        enhancement_info = f"""
EDUCATIONAL ENHANCEMENT:
Density score: {enhanced_content.educational_density:.2f}
Complexity score: {enhanced_content.complexity_score:.2f}
Key concepts: {', '.join(enhanced_content.key_concepts[:3]) if enhanced_content.key_concepts else 'N/A'}
"""
        
        return f"""
You are the Scene Script Writer (SSW). Expand this scene beat into a production-ready package.

SCENE DETAILS:
- Scene Number: {scene_number}
- Scene Type: {scene_type}
- Importance Level: {importance}/5
- Needs Animation: {needs_animation}
- Transition Out: {transition}

STORY CONTEXT:
- Title: {title}
- Overall Style: {overall_style}
- Main Character: {main_character}
- Character Cosplay: {cosplay}
- Story Summary: {story_summary}
- Language: {language}

SCENE BEATS TO EXPAND:
{chr(10).join([f"- {beat}" for beat in beats])}

LEARNING OBJECTIVES:
{chr(10).join([f"- {obj}" for obj in learning_objectives])}

{enhancement_info}

{continuity_context}

ELABORATION & HOOKING MISSION:
Your job is to ELABORATE the story beats and ADD HOOKING elements to make this scene compelling.
Generate all content in {language} language.

DIALOGUE FLOW & CONTINUITY MISSION:
Create smooth, natural dialogue that flows seamlessly within the scene and connects logically to other scenes.
Ensure each line of dialogue builds naturally from the previous line and leads smoothly to the next.

ELABORATION REQUIREMENTS:
- EXPAND on the basic beats with rich details, interesting facts, and compelling narratives
- ADD depth with specific examples, case studies, and real-world applications
- INCLUDE fascinating details, surprising facts, and intriguing information
- CREATE vivid descriptions and compelling storytelling elements
- DEVELOP the content into something truly engaging and memorable

HOOKING REQUIREMENTS:
- START with attention-grabbing elements (questions, surprising facts, intriguing statements)
- USE compelling storytelling techniques to maintain viewer interest
- INCLUDE emotional hooks, curiosity gaps, and engaging narrative elements
- CREATE moments that make viewers want to keep watching
- ADD suspense, intrigue, or compelling questions throughout the scene

DIALOGUE CONTINUITY REQUIREMENTS:
- REFERENCE previous scene content when appropriate (use continuity context)
- CREATE smooth transitions between dialogue lines within the scene
- USE connecting phrases like "Now that we've seen...", "Building on that...", "This leads us to..."
- MAINTAIN consistent narrative voice and perspective throughout
- ENSURE each dialogue line logically follows from the previous one
- AVOID sudden topic jumps or disconnected statements
- CREATE bridges between concepts using transitional language
- ESTABLISH clear cause-and-effect relationships in dialogue flow

TTS-FRIENDLY WRITING REQUIREMENTS:
- WRITE OUT all numbers as words (e.g., "5" → "five", "1920s" → "nineteen twenties")
- AVOID numerical symbols that TTS might mispronounce
- USE "zeros and ones" instead of "0s and 1s"
- WRITE "fifty percent" instead of "50%"
- CONVERT years properly: "2024" → "twenty twenty four"
- SPELL OUT technical abbreviations when first mentioned

TECHNICAL REQUIREMENTS:
- Follow ScenePackage.json schema exactly
- MUST include ALL required fields: scene_number, narration_script, visuals, tts, timing, continuity
- Create detailed narration_script with timing (at_ms, pause_ms)
- Design comprehensive visuals array with detailed image_prompts
- Include proper TTS settings with elevenlabs_settings
- Add appropriate sfx_cues and on_screen_text
- Calculate realistic timing.total_ms
- Maintain continuity with callback_tags
- Use frame_ids like "1A", "1B", etc.

REQUIRED FIELDS CHECKLIST:
✓ scene_number (integer)
✓ narration_script (array with line, at_ms, pause_ms)
✓ visuals (array with frame_id, shot_type, image_prompt, aspect_ratio)
✓ tts (object with engine, voice, elevenlabs_settings)
✓ timing (object with total_ms)
✓ continuity (object with in_from, out_to, callback_tags)

OPTIONAL FIELDS (use empty arrays if not needed):
✓ dialogue (array, can be empty: [])
✓ sfx_cues (array with cue, at_ms, duration_ms)
✓ on_screen_text (array with text, at_ms, duration_ms, style, position)

VISUAL REQUIREMENTS:
- Create 1-2 key visual frames per scene (not more than 2)
- Create compelling image_prompts (minimum 40 characters)
- Include negative_prompts to avoid unwanted elements
- Specify shot_types: wide, medium, close, macro, extreme_wide, extreme_close
- Add camera_motion, character_pose, expression, background, lighting
- Use aspect_ratio: 16:9, 9:16, 1:1, 4:5, 3:2, 2:3
- Include model_hints for style consistency
- Set appropriate guidance_scale (1.0-20.0)
- Focus on the MOST IMPORTANT visual moment(s) of the scene

TTS REQUIREMENTS:
- Use engine: "elevenlabs"
- Set voice appropriately
- Configure elevenlabs_settings:
  - stability: 0.2-0.6 (lower for more expressive, varied voice)
  - similarity_boost: 0.8-1.0 (higher for better voice consistency)  
  - style: 0.7-1.0 (higher for more emotional expression and mood)
  - speed: 1.2-1.5 (20-30% faster for better engagement)
  - loudness: 0.1-0.4 (moderate levels for clear audio)

OUTPUT FORMAT:
Generate ONLY valid JSON following ScenePackage.json schema.

CRITICAL JSON REQUIREMENTS:
- OUTPUT MUST BE COMPLETE, VALID JSON
- ALL STRINGS MUST BE PROPERLY CLOSED WITH QUOTES  
- ALL OBJECTS MUST END WITH CLOSING BRACES
- NO TRAILING COMMAS
- NO INCOMPLETE LINES OR TRUNCATED OUTPUT

SFX CUES FORMAT (IMPORTANT):
- Use "cue" field (NOT "name", "sfx_name", or "effect")
- Required fields: cue, at_ms, duration_ms
- Example: {{"cue": "whoosh_sound", "at_ms": 1000, "duration_ms": 500}}

ON-SCREEN TEXT FORMAT:
- Required fields: text, at_ms, duration_ms, style, position
- Use simple values: style="normal", position="center"

EXAMPLE OUTPUT STRUCTURE:
{{
  "scene_number": {scene_number},
  "narration_script": [
    {{"line": "Opening line...", "at_ms": 0, "pause_ms": 200}},
    {{"line": "Second line...", "at_ms": 2000}}
  ],
  "dialogue": [],
  "visuals": [
    {{
      "frame_id": "{scene_number}A",
      "shot_type": "wide",
      "camera_motion": "slow push-in",
      "character_pose": "pointing",
      "expression": "curious",
      "background": "educational setting",
      "foreground_props": "relevant props",
      "lighting": "soft key lighting",
      "color_mood": "warm and engaging",
      "image_prompt": "Detailed 40+ character prompt for image generation...",
      "negative_prompt": "low quality, blurry, distorted",
      "model_hints": ["illustration", "educational"],
      "aspect_ratio": "16:9",
      "seed": 123456,
      "guidance_scale": 7.5
    }}
  ],
  "tts": {{
    "engine": "elevenlabs",
    "voice": "friendly-narrator",
    "language": "{language}",
    "elevenlabs_settings": {{
      "stability": 0.4,
      "similarity_boost": 0.9,
      "style": 0.85,
      "speed": 1.3,
      "loudness": 0.25
    }}
  }},
  "sfx_cues": [
    {{"cue": "transition_whoosh", "at_ms": 500, "duration_ms": 800}},
    {{"cue": "emphasis_chime", "at_ms": 3000, "duration_ms": 300}}
  ],
  "on_screen_text": [
    {{"text": "Key Point", "at_ms": 2000, "duration_ms": 3000, "style": "normal", "position": "center"}}
  ],
  "timing": {{
    "total_ms": 5000
  }},
  "continuity": {{
    "in_from": "fade",
    "out_to": "{transition}",
    "callback_tags": ["relevant_tags"]
  }},
  "safety_checks": []
}}

Remember: You are creating production-ready content. Every field should be meaningful and detailed.
Make this scene {scene_number} truly compelling and engaging while maintaining educational value.
INCLUDE ALL REQUIRED FIELDS: scene_number, narration_script, visuals, tts, timing, continuity.

IMPORTANT: Create 3-6 visual frames per scene for better engagement (target 5-7 seconds per image). 
Each frame should represent a different moment or angle in the dialogue/narration.
Multiple images per dialogue segment are encouraged for dynamic storytelling.
"""
    
    async def _simulate_adk_response(self, prompt: str, max_retries: int = 3) -> str:
        """Use actual ADK API to generate response with retry mechanism"""
        import asyncio
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Using actual ADK API for scene script generation (attempt {attempt + 1}/{max_retries})")
                
                # Try different methods to call the ADK agent
                response = None
                
                # Method 1: Try run() method
                try:
                    response = await self.run(prompt)
                    logger.info("Successfully used run() method")
                except AttributeError:
                    logger.info("run() method not available, trying generate_content()")
                    
                    # Method 2: Try generate_content() method
                    try:
                        response = await self.generate_content(prompt)
                        logger.info("Successfully used generate_content() method")
                    except AttributeError:
                        logger.info("generate_content() method not available, trying direct model call")
                        
                        # Method 3: Direct model call with structured output
                        client = genai.Client()
                        # Load ScenePackage schema for structured output
                        schema_path = Path("schemas/ScenePackage.json")
                        scene_schema = None
                        if schema_path.exists():
                            with open(schema_path, 'r') as f:
                                scene_schema = json.load(f)
                                logger.info("📋 Loaded ScenePackage JSON schema")
                        
                        config = {
                            "temperature": 0.7,  # Lower temperature for more consistent JSON
                            "top_p": 0.8,
                            "top_k": 30,
                            "max_output_tokens": 8192,
                            "response_mime_type": "application/json"
                        }
                        
                        # Enable schema for structured output
                        if scene_schema:
                            config["response_schema"] = scene_schema
                            logger.info("🎯 Using JSON schema for structured output")
                        else:
                            logger.warning("⚠️ Schema not found, using standard JSON output")
                        
                        logger.info("🎯 Using ADK API with output schema for scene generation")
                        
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[prompt],
                            config=config
                        )
                        logger.info("Successfully used direct model call")
                
                # Extract and validate response
                response_text = None
                if response and hasattr(response, 'text') and response.text:
                    response_text = response.text.strip()
                elif response and isinstance(response, str):
                    response_text = response.strip()
                else:
                    raise ValueError("No response received from ADK API")
                
                # Validate response quality before expensive parsing
                is_valid_response, validation_reason = validate_response_quality(
                    response_text, f"scene_{attempt + 1}"
                )
                
                if not is_valid_response:
                    raise ValueError(f"Response validation failed: {validation_reason}")
                
                logger.info("Successfully received and validated scene script response from ADK API")
                return response_text
                    
            except Exception as e:
                logger.error(f"ADK API call failed for scene script (attempt {attempt + 1}): {str(e)}")
                
                if attempt < max_retries - 1:
                    # Use intelligent retry logic
                    should_retry = CostOptimizer.should_retry_request(str(e), attempt + 1, max_retries)
                    if should_retry:
                        wait_time = CostOptimizer.get_optimal_retry_delay(attempt + 1)
                        logger.info(f"Retrying in {wait_time:.1f} seconds...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error("Error is non-retryable, stopping attempts")
                        raise ValueError(f"Non-retryable error for scene script: {str(e)}")
                else:
                    logger.error("All API retry attempts failed")
                    raise ValueError(f"ADK API call failed for scene script after {max_retries} attempts: {str(e)}")
        
        raise ValueError(f"Unexpected error: reached end of retry loop")
    
    def _parse_response_with_pydantic(self, response_text: str, scene_number: int) -> Dict[str, Any]:
        """Parse AI response using robust JSON parser with Pydantic validation"""
        try:
            # Use the robust JSON parser with Pydantic validation
            scene_package_model = parse_scene_package(response_text, scene_number)
            
            # Convert Pydantic model back to dict for compatibility
            scene_package_dict = scene_package_model.model_dump()
            
            logger.info(f"✅ Scene {scene_number} parsed and validated successfully with Pydantic")
            return scene_package_dict
            
        except JSONParsingError as e:
            logger.error(f"❌ JSON parsing failed for scene {scene_number}: {e}")
            logger.error(f"Raw response preview: {response_text[:500]}...")
            
            # Try to create fallback data
            try:
                logger.warning(f"⚠️ Creating fallback data for scene {scene_number}")
                fallback_model = RobustJSONParser.create_fallback_data(
                    ScenePackage,
                    context_name=f"scene_{scene_number}",
                    scene_number=scene_number
                )
                fallback_dict = fallback_model.model_dump()
                fallback_dict['safety_checks'] = ['parsing_failed_fallback_used']
                return fallback_dict
            except Exception as fallback_error:
                logger.error(f"❌ Even fallback creation failed for scene {scene_number}: {fallback_error}")
                raise ValueError(f"Complete parsing failure for scene {scene_number}: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error parsing scene {scene_number}: {e}")
            raise ValueError(f"Unexpected parsing error for scene {scene_number}: {e}")
    
    def _parse_response_safely_legacy(self, response_text: str, scene_number: int) -> Dict[str, Any]:
        """Parse AI response safely with JSON repair and validation"""
        try:
            # Find JSON in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.error(f"No valid JSON found in scene {scene_number} response")
                raise ValueError(f"No valid JSON found in scene {scene_number} response")
            
            # Extract clean JSON
            clean_json = response_text[start_idx:end_idx]
            logger.info(f"Extracted scene {scene_number} JSON: {clean_json[:200]}...")
            
            # Try multiple JSON parsing strategies
            scene_package = None
            
            # Strategy 1: Direct parsing
            try:
                scene_package = json.loads(clean_json)
                logger.info(f"✅ Direct JSON parsing successful for scene {scene_number}")
            except json.JSONDecodeError as e:
                logger.warning(f"Direct parsing failed: {e}")
                
                # Strategy 2: JSON repair
                try:
                    repaired_json = self._repair_json(clean_json, scene_number)
                    scene_package = json.loads(repaired_json)
                    logger.info(f"✅ Repaired JSON parsing successful for scene {scene_number}")
                except Exception as repair_error:
                    logger.error(f"JSON repair also failed: {repair_error}")
                    raise e  # Raise original error
            
            if scene_package is None:
                raise ValueError("Failed to parse JSON with all strategies")
            
            # Basic validation
            required_fields = ['scene_number', 'narration_script', 'visuals', 'tts', 'timing', 'continuity']
            missing_fields = [field for field in required_fields if field not in scene_package]
            
            if missing_fields:
                logger.error(f"Missing required fields in scene {scene_number}: {missing_fields}")
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            logger.info(f"Scene {scene_number} JSON parsing successful")
            return scene_package
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed for scene {scene_number}: {e}")
            logger.error(f"Raw response: {response_text[:500]}...")
            raise ValueError(f"Failed to parse scene {scene_number} JSON response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in scene {scene_number} JSON parsing: {e}")
            raise ValueError(f"Unexpected error in scene {scene_number} JSON parsing: {e}")
    
    def _repair_json(self, json_str: str, scene_number: int) -> str:
        """Attempt to repair common JSON syntax errors"""
        logger.info(f"🔧 Attempting JSON repair for scene {scene_number}")
        
        # Common fixes
        repaired = json_str
        
        # Fix 1: Remove trailing commas (most common issue)
        import re
        repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
        
        # Fix 2: Fix missing commas after closing braces/brackets
        repaired = re.sub(r'}(\s*)(["\w])', r'},\1\2', repaired)
        repaired = re.sub(r'](\s*)(["\w])', r'],\1\2', repaired)
        
        # Fix 3: Fix missing commas between array elements
        repaired = re.sub(r'}\s*{', '},{', repaired)
        repaired = re.sub(r']\s*\[', '],[', repaired)
        
        # Fix 4: Fix unescaped quotes in strings
        # This is tricky - try to fix obvious cases
        lines = repaired.split('\n')
        fixed_lines = []
        for line in lines:
            # Fix quotes in the middle of strings
            if ':' in line and '"' in line:
                # Try to fix unescaped quotes
                line = re.sub(r'([^\\])(".*?[^\\])(".*?")', r'\1\2\\"\3', line)
            fixed_lines.append(line)
        repaired = '\n'.join(fixed_lines)
        
        # Fix 5: Ensure proper string escaping for newlines and tabs
        repaired = repaired.replace('\n', '\\n').replace('\t', '\\t')
        
        # Fix 6: Remove any control characters except newlines and tabs
        repaired = ''.join(char for char in repaired if ord(char) >= 32 or char in '\n\t')
        
        # Fix 7: Handle unterminated strings (common issue)
        lines = repaired.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check for unterminated string patterns like: "key": "value that never closes
            if ':' in line and '"' in line:
                # Count quotes in the line
                quote_count = line.count('"')
                # If odd number of quotes, likely unterminated string
                if quote_count % 2 == 1:
                    # Look for the pattern: "key": "unterminated_value
                    match = re.search(r'"([^"]*)":\s*"([^"]*)$', line)
                    if match:
                        # Close the unterminated string
                        line = line + '"'
                        logger.info(f"🔧 Fixed unterminated string on line {i+1}")
            
            fixed_lines.append(line)
        
        repaired = '\n'.join(fixed_lines)
        
        # Fix 8: Try to balance braces and brackets
        open_braces = repaired.count('{')
        close_braces = repaired.count('}')
        open_brackets = repaired.count('[')
        close_brackets = repaired.count(']')
        
        if open_braces > close_braces:
            repaired += '}' * (open_braces - close_braces)
        elif close_braces > open_braces:
            repaired = '{' * (close_braces - open_braces) + repaired
            
        if open_brackets > close_brackets:
            repaired += ']' * (open_brackets - close_brackets)
        elif close_brackets > open_brackets:
            repaired = '[' * (close_brackets - open_brackets) + repaired
        
        # Fix 9: Handle truncated JSON (if ends abruptly)
        repaired = repaired.strip()
        if not repaired.endswith('}') and not repaired.endswith(']'):
            # Try to find the last complete object/array and close it
            if repaired.rfind('{') > repaired.rfind('}'):
                repaired += '}'
            if repaired.rfind('[') > repaired.rfind(']'):
                repaired += ']'
        
        logger.info(f"🔧 JSON repair completed for scene {scene_number}")
        logger.debug(f"🔧 Repaired JSON preview: {repaired[:200]}...")
        return repaired
    
    def _run_safety_checks(self, scene_package: Dict[str, Any]) -> List[str]:
        """Run safety checks on the scene package"""
        checks = []
        
        try:
            # Schema validation check
            if all(field in scene_package for field in ['scene_number', 'narration_script', 'visuals', 'tts']):
                checks.append("schema_ok")
            else:
                checks.append("schema_incomplete")
            
            # TTS settings validation
            tts = scene_package.get('tts', {})
            elevenlabs = tts.get('elevenlabs_settings', {})
            
            valid_tts = True
            for key, value in elevenlabs.items():
                if key == 'stability' and not (0.2 <= value <= 0.6):
                    valid_tts = False
                elif key == 'similarity_boost' and not (0.8 <= value <= 1.0):
                    valid_tts = False
                elif key == 'style' and not (0.7 <= value <= 1.0):
                    valid_tts = False
                elif key == 'loudness' and not (0.1 <= value <= 0.4):
                    valid_tts = False
                elif key == 'speed' and not (1.2 <= value <= 1.5):
                    valid_tts = False
            
            if valid_tts:
                checks.append("tts_settings_valid")
            else:
                checks.append("tts_settings_invalid")
            
            # Visual prompts check
            visuals = scene_package.get('visuals', [])
            if all(len(v.get('image_prompt', '')) >= 40 for v in visuals):
                checks.append("image_prompts_adequate")
            else:
                checks.append("image_prompts_too_short")
            
            # Timing check
            timing = scene_package.get('timing', {})
            if timing.get('total_ms', 0) >= 1000:
                checks.append("timing_realistic")
            else:
                checks.append("timing_too_short")
                
        except Exception as e:
            logger.error(f"Error running safety checks: {str(e)}")
            checks.append("safety_check_error")
        
        return checks
