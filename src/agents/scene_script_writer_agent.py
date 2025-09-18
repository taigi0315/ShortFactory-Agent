"""
Scene Script Writer Agent - Simple LlmAgent Pattern  
Direct Pydantic input/output with clean instruction-based approach
"""

import logging
from typing import Dict, Any
import google.genai as genai
from google.genai import types

from model.input_models import SceneExpansionInput
from model.output_models import ScenePackageOutput

logger = logging.getLogger(__name__)


class SceneScriptWriterAgent:
    """
    Simple Scene Script Writer Agent using direct Pydantic models
    Clean instruction-based approach without complex schema conversion
    """
    
    def __init__(self):
        """Initialize Simple Scene Script Writer Agent"""
        self.client = genai.Client()
        
        # Simple instruction - no complex schema conversion needed
        self.instruction = """You are a Scene Script Writer Agent that transforms scene beats into production-ready packages.

Given scene information and context, create detailed narration, visuals, TTS settings, and timing.

REQUIREMENTS:
- Create engaging narration script with precise timing (at_ms, pause_ms)
- Design 1-6 visual frames with detailed image prompts (40+ characters each)
- Configure TTS settings (LemonFox engine, voice, speed)
- Calculate realistic timing based on narration length
- Maintain character consistency (use main character from context)

NARRATION GUIDELINES:
- Use conversational, engaging language
- Write numbers as words ("five" not "5")
- Plan realistic pacing (150-180 words per minute)
- Add appropriate pauses for emphasis

VISUAL GUIDELINES:
- Create 1-6 frames per scene for visual variety
- Each frame represents 3-5 seconds of content
- Include main character in appropriate context
- Specify shot types, poses, expressions, backgrounds
- Image prompts must be 40+ characters minimum

OUTPUT FORMAT:
Respond ONLY with valid JSON matching the ScenePackageOutput schema.
No additional text, explanations, or markdown formatting."""
        
        # Legacy compatibility properties for tests
        self.input_schema = SceneExpansionInput.model_json_schema()
        self.output_schema = ScenePackageOutput.model_json_schema()
        self.output_key = "scene_package_output_result"
        
        logger.info("🚀 Simple Scene Script Writer Agent initialized")
    
    async def expand_scene(self, input_data: SceneExpansionInput) -> ScenePackageOutput:
        """
        Expand scene with simple direct approach
        
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
            
            # Create context prompt from input data
            context_prompt = self._create_context_prompt(input_data)
            
            # Use ADK structured generation with direct Pydantic schema
            response = await self.client.agenerate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(parts=[
                        types.Part(text=context_prompt)
                    ])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=self.instruction,
                    response_schema=ScenePackageOutput.model_json_schema(),  # Direct Pydantic!
                    temperature=0.8,
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=8192
                )
            )
            
            # Parse and validate with Pydantic
            result = ScenePackageOutput.model_validate_json(response.text)
            
            logger.info(f"✅ Scene {scene_number} expansion completed")
            return result
                
        except Exception as e:
            logger.error(f"❌ Scene expansion failed: {e}")
            return self._create_fallback_output(input_data)
    
    def _create_context_prompt(self, input_data: SceneExpansionInput) -> str:
        """Create context prompt from input data"""
        scene_data = input_data.scene_data
        global_context = input_data.global_context
        
        scene_number = scene_data.get('scene_number', 1)
        scene_type = scene_data.get('scene_type', 'explanation')
        beats = scene_data.get('beats', [])
        learning_objectives = scene_data.get('learning_objectives', [])
        
        main_character = global_context.get('main_character', 'Glowbie')
        overall_style = global_context.get('overall_style', 'educational and engaging')
        target_audience = global_context.get('target_audience', 'general')
        
        context = f"""
SCENE TO EXPAND:
- Scene {scene_number}: {scene_type}
- Story beats: {', '.join(beats)}
- Learning objectives: {', '.join(learning_objectives)}

CONTEXT:
- Character: {main_character}
- Style: {overall_style}
- Audience: {target_audience}
"""
        
        # Add previous scenes context if available
        if input_data.previous_scenes:
            context += "\nPREVIOUS SCENES:\n"
            for prev_scene in input_data.previous_scenes:
                context += f"- Scene {prev_scene.get('scene_number', '?')}: {prev_scene.get('summary', 'No summary')}\n"
        
        context += "\nCreate a detailed, timed, production-ready scene package."
        
        return context
    
    def _create_fallback_output(self, input_data: SceneExpansionInput) -> ScenePackageOutput:
        """Create fallback output when generation fails"""
        scene_data = input_data.scene_data
        scene_number = scene_data.get('scene_number', 1)
        
        logger.warning(f"⚠️ Creating fallback scene package for scene {scene_number}")
        
        return ScenePackageOutput(
            scene_number=scene_number,
            narration_script=[
                {
                    "line": f"This is scene {scene_number}. Content generation encountered an issue, but we're providing a basic structure.",
                    "at_ms": 0,
                    "pause_ms": 500
                }
            ],
            visuals=[
                {
                    "frame_id": f"{scene_number}A",
                    "shot_type": "medium",
                    "image_prompt": "Educational scene with friendly character explaining a concept in a clear and engaging manner with colorful background",
                    "aspect_ratio": "16:9"
                }
            ],
            tts={
                "engine": "lemonfox",
                "voice": "sarah",
                "language": "en-US",
                "speed": 1.0
            },
            timing={
                "total_ms": 5000,
                "estimated": True
            }
        )
    
    def get_schemas(self) -> Dict[str, Any]:
        """Get the schemas for this agent (legacy compatibility)"""
        return {
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "output_key": self.output_key
        }
    
    def _create_instruction(self, input_data: SceneExpansionInput) -> str:
        """Create instruction (legacy compatibility)"""
        return self.instruction