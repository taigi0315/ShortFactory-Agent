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
            
            # Log the prompt
            logger.info(f"SSW PROMPT for scene {scene_number}:")
            logger.info(f"Length: {len(prompt)}")
            
            # Generate response using ADK
            response = await self._simulate_adk_response(prompt)
            
            if response:
                # Save prompt and response
                self._save_prompt_and_response(session_id, scene_number, prompt, response)
                
                # Parse and validate response
                scene_package = self._parse_response_safely(response, scene_number)
                
                # Add safety checks
                scene_package['safety_checks'] = self._run_safety_checks(scene_package)
                
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
        beats = scene_data.get('beats', [])
        learning_objectives = scene_data.get('learning_objectives', [])
        needs_animation = scene_data.get('needs_animation', False)
        transition = scene_data.get('transition_to_next', 'fade')
        importance = scene_data.get('scene_importance', 3)
        
        # Context from global
        title = global_context.get('title', '')
        overall_style = global_context.get('overall_style', 'engaging')
        main_character = global_context.get('main_character', 'Huh - a cute, blob-like cartoon character')
        cosplay = global_context.get('cosplay_instructions', '')
        story_summary = global_context.get('story_summary', '')
        
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

SCENE BEATS TO EXPAND:
{chr(10).join([f"- {beat}" for beat in beats])}

LEARNING OBJECTIVES:
{chr(10).join([f"- {obj}" for obj in learning_objectives])}

{enhancement_info}

{continuity_context}

ELABORATION & HOOKING MISSION:
Your job is to ELABORATE the story beats and ADD HOOKING elements to make this scene compelling.

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
✓ narration_script (array with line, at_ms)
✓ visuals (array with frame_id, shot_type, image_prompt, aspect_ratio)
✓ tts (object with engine, voice, elevenlabs_settings)
✓ timing (object with total_ms)
✓ continuity (object with in_from, out_to, callback_tags)

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
  - stability: 0.0-1.0
  - similarity_boost: 0.0-1.0  
  - style: 0.0-1.0
  - speed: 0.7-1.3
  - loudness: 0.0-1.0

OUTPUT FORMAT:
Generate ONLY valid JSON following ScenePackage.json schema.

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
    "language": "en-US",
    "elevenlabs_settings": {{
      "stability": 0.35,
      "similarity_boost": 0.8,
      "style": 0.85,
      "speed": 1.08,
      "loudness": 0.2
    }}
  }},
  "sfx_cues": [],
  "on_screen_text": [],
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

IMPORTANT: Create only 1-2 visual frames per scene. Focus on the most impactful visual moment.
"""
    
    async def _simulate_adk_response(self, prompt: str) -> str:
        """Use actual ADK API to generate response"""
        try:
            logger.info("Using actual ADK API for scene script generation")
            
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
                    
                    # Method 3: Direct model call
                    client = genai.Client()
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[prompt],
                        config={
                            "temperature": 0.8,
                            "top_p": 0.9,
                            "top_k": 40,
                            "max_output_tokens": 8192,
                            "response_mime_type": "application/json"
                        }
                    )
                    logger.info("Successfully used direct model call")
            
            if response and hasattr(response, 'text') and response.text:
                logger.info("Successfully received scene script response from ADK API")
                return response.text
            elif response and isinstance(response, str):
                logger.info("Successfully received string scene script response from ADK API")
                return response
            else:
                logger.error("No response text from ADK API")
                raise ValueError("No response received from ADK API")
                
        except Exception as e:
            logger.error(f"ADK API call failed for scene script: {str(e)}")
            raise ValueError(f"ADK API call failed for scene script: {str(e)}")
    
    def _parse_response_safely(self, response_text: str, scene_number: int) -> Dict[str, Any]:
        """Parse AI response safely and validate"""
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
            
            # Parse JSON
            scene_package = json.loads(clean_json)
            
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
                if key in ['stability', 'similarity_boost', 'style', 'loudness'] and not (0.0 <= value <= 1.0):
                    valid_tts = False
                elif key == 'speed' and not (0.7 <= value <= 1.3):
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
