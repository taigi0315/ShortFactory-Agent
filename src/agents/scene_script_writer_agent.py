"""
Enhanced ADK Scene Script Agent
Uses Pydantic-based schemas for type safety and automatic ADK schema generation
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import google.genai as genai
from google.genai import types

from schemas.input_models import SceneExpansionInput
from schemas.output_models import ScenePackageOutput, NarrationLine, VisualFrame, TTSSettings, TimingInfo
from core.schema_converter import PydanticToADKSchema

logger = logging.getLogger(__name__)


class SceneScriptWriterAgent:
    """
    ADK-based Scene Script Writer Agent
    Uses Pydantic models for type-safe input/output and automatic ADK schema generation
    """
    
    def __init__(self):
        """Initialize ADK Scene Script Agent"""
        
        # Generate ADK schemas from Pydantic models
        self.input_schema = PydanticToADKSchema.convert_model_to_schema(SceneExpansionInput)
        self.output_schema = PydanticToADKSchema.convert_model_to_schema(ScenePackageOutput)
        self.output_key = PydanticToADKSchema.get_output_key(ScenePackageOutput)
        
        # Initialize ADK client
        self.client = genai.Client()
        
        logger.info("🚀 ADK Scene Script Agent initialized with Pydantic schemas")
        logger.info(f"📋 Input schema: {len(self.input_schema.get('properties', {}))} properties")
        logger.info(f"📋 Output schema: {len(self.output_schema.get('properties', {}))} properties")
        logger.info(f"🔑 Output key: {self.output_key}")
    
    async def expand_scene(self, input_data: SceneExpansionInput) -> ScenePackageOutput:
        """
        Expand scene with type-safe input/output
        
        Args:
            input_data: Type-safe scene expansion input
            
        Returns:
            ScenePackageOutput: Type-safe scene package output
        """
        try:
            scene_data = input_data.scene_data
            scene_number = scene_data.get('scene_number', 1)
            scene_type = scene_data.get('scene_type', 'explanation')
            
            logger.info(f"🎬 Expanding scene {scene_number} ({scene_type})")
            
            # Create instruction prompt
            instruction = self._create_instruction(input_data)
            
            # Prepare input for ADK
            input_dict = input_data.model_dump()
            
            # Use ADK structured generation
            response = await self.client.agenerate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(parts=[
                        types.Part(text=json.dumps(input_dict))
                    ])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=instruction,
                    response_schema=self.output_schema,
                    temperature=0.8,
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=8192
                )
            )
            
            # Extract and validate response
            response_text = response.text
            logger.info(f"✅ Scene {scene_number} generation successful")
            
            # Parse JSON response
            try:
                response_data = json.loads(response_text)
                logger.info(f"✅ JSON parsing successful for scene {scene_number}")
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing failed for scene {scene_number}: {e}")
                raise ValueError(f"Invalid JSON response for scene {scene_number}: {e}")
            
            # Validate with Pydantic model
            try:
                validated_output = ScenePackageOutput.model_validate(response_data)
                logger.info(f"✅ Pydantic validation successful for scene {scene_number}")
                return validated_output
            except Exception as e:
                logger.error(f"❌ Pydantic validation failed for scene {scene_number}: {e}")
                # Create fallback with minimal valid data
                return self._create_fallback_output(input_data, str(e))
            
        except Exception as e:
            logger.error(f"❌ Scene generation failed: {e}")
            return self._create_fallback_output(input_data, str(e))
    
    def _create_instruction(self, input_data: SceneExpansionInput) -> str:
        """Create instruction prompt for scene expansion"""
        scene_data = input_data.scene_data
        scene_number = scene_data.get('scene_number', 1)
        scene_type = scene_data.get('scene_type', 'explanation')
        beats = scene_data.get('beats', [])
        learning_objectives = scene_data.get('learning_objectives', [])
        
        global_context = input_data.global_context
        overall_style = global_context.get('overall_style', 'educational and engaging')
        main_character = global_context.get('main_character', 'Glowbie')
        target_audience = global_context.get('target_audience', 'general')
        
        return f"""You are a master scene writer who transforms high-level story beats into production-ready scene packages.

SCENE TO EXPAND:
- Scene {scene_number}: {scene_type}
- Story beats: {', '.join(beats)}
- Learning objectives: {', '.join(learning_objectives)}

CONTEXT:
- Character: {main_character}
- Style: {overall_style}
- Audience: {target_audience}

YOUR MISSION:
Transform the above scene beat into a detailed, timed, production-ready package with narration, visuals, and technical specifications.

OUTPUT REQUIREMENTS:
You MUST respond with ONLY valid JSON matching the provided schema.

CORE RESPONSIBILITIES:
1. Create detailed narration script with precise timing (at_ms, pause_ms)
2. Design 1-6 visual frames with specific image prompts (40+ characters each)
3. Configure TTS settings (LemonFox engine, voice, speed)
4. Calculate realistic timing based on narration length
5. Maintain visual consistency with character

NARRATION GUIDELINES:
- Use conversational, engaging language
- Include specific facts, examples, and details
- Write numbers as words ("five" not "5")
- Plan realistic pacing (150-180 words per minute)
- Add appropriate pauses for emphasis

VISUAL GUIDELINES:
- Create 1-6 frames per scene for visual variety
- Each frame should represent 3-5 seconds of content
- Include {main_character} character in appropriate cosplay
- Specify shot types, poses, expressions, backgrounds
- Image prompts must be 40+ characters minimum

TTS CONFIGURATION:
- Engine: "lemonfox" (preferred)
- Voice: "sarah" (default)
- Speed: 1.0-1.2 (slightly faster for engagement)
- Language: "en-US"

TIMING CALCULATION:
- Estimate narration duration based on text length
- Add pause times between lines
- Set total_ms for entire scene
- Mark as estimated=true (will be updated with actual TTS duration)

The response MUST be valid JSON only, no additional text or explanation."""
    
    def _create_fallback_output(self, input_data: SceneExpansionInput, error_msg: str) -> ScenePackageOutput:
        """Create fallback output when generation fails"""
        scene_data = input_data.scene_data
        scene_number = scene_data.get('scene_number', 1)
        
        logger.warning(f"⚠️ Creating fallback scene package for scene {scene_number}")
        
        fallback_data = {
            "scene_number": scene_number,
            "narration_script": [
                {
                    "line": f"This is scene {scene_number}. Content generation encountered an issue: {error_msg}",
                    "at_ms": 0,
                    "pause_ms": 500
                }
            ],
            "visuals": [
                {
                    "frame_id": f"{scene_number}A",
                    "shot_type": "medium",
                    "image_prompt": "Educational scene with friendly character explaining a concept in a clear and engaging manner",
                    "aspect_ratio": "16:9"
                }
            ],
            "tts": {
                "engine": "lemonfox",
                "voice": "sarah",
                "language": "en-US",
                "speed": 1.0
            },
            "timing": {
                "total_ms": 5000,
                "estimated": True
            }
        }
        
        return ScenePackageOutput.model_validate(fallback_data)
    
    def get_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get the ADK schemas for this agent"""
        return {
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "output_key": self.output_key
        }
