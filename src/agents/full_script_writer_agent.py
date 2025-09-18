"""
Enhanced ADK Full Script Agent
Uses Pydantic-based schemas for type safety and automatic ADK schema generation
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import google.genai as genai
from google.genai import types

from schemas.input_models import FullScriptInput
from schemas.output_models import FullScriptOutput
from core.schema_converter import PydanticToADKSchema

logger = logging.getLogger(__name__)


class FullScriptWriterAgent:
    """
    ADK-based Full Script Writer Agent
    Uses Pydantic models for type-safe input/output and automatic ADK schema generation
    """
    
    def __init__(self):
        """Initialize ADK Full Script Agent"""
        
        # Generate ADK schemas from Pydantic models
        self.input_schema = PydanticToADKSchema.convert_model_to_schema(FullScriptInput)
        self.output_schema = PydanticToADKSchema.convert_model_to_schema(FullScriptOutput)
        self.output_key = PydanticToADKSchema.get_output_key(FullScriptOutput)
        
        # Initialize ADK client
        self.client = genai.Client()
        
        logger.info("🚀 ADK Full Script Agent initialized with Pydantic schemas")
        logger.info(f"📋 Input schema: {len(self.input_schema.get('properties', {}))} properties")
        logger.info(f"📋 Output schema: {len(self.output_schema.get('properties', {}))} properties")
        logger.info(f"🔑 Output key: {self.output_key}")
    
    async def generate_script(self, input_data: FullScriptInput) -> FullScriptOutput:
        """
        Generate full script with type-safe input/output
        
        Args:
            input_data: Type-safe input data
            
        Returns:
            FullScriptOutput: Type-safe output data
        """
        try:
            logger.info(f"🎬 Generating full script for topic: {input_data.topic}")
            logger.info(f"📏 Length: {input_data.length_preference}")
            logger.info(f"🎨 Style: {input_data.style_profile}")
            
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
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=8192
                )
            )
            
            # Extract and validate response
            response_text = response.text
            logger.info("✅ ADK Full Script generation successful")
            
            # Parse JSON response
            try:
                response_data = json.loads(response_text)
                logger.info("✅ JSON parsing successful")
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing failed: {e}")
                raise ValueError(f"Invalid JSON response: {e}")
            
            # Validate with Pydantic model
            try:
                validated_output = FullScriptOutput.model_validate(response_data)
                logger.info("✅ Pydantic validation successful")
                return validated_output
            except Exception as e:
                logger.error(f"❌ Pydantic validation failed: {e}")
                # Create fallback with minimal valid data
                return self._create_fallback_output(input_data, str(e))
            
        except Exception as e:
            logger.error(f"❌ Enhanced ADK Full Script generation failed: {e}")
            return self._create_fallback_output(input_data, str(e))
    
    def _create_instruction(self, input_data: FullScriptInput) -> str:
        """Create instruction prompt for the agent"""
        return f"""You are an expert story architect for educational video content.

Your mission is to transform the topic "{input_data.topic}" into a compelling story structure for a {input_data.length_preference} video.

Target audience: {input_data.target_audience}
Style: {input_data.style_profile}
Language: {input_data.language}

CORE RESPONSIBILITIES:
1. Analyze the topic and create an engaging narrative framework
2. Determine optimal scene count (3-8 scenes) based on topic complexity
3. Define scene types, order, and narrative flow
4. Set learning objectives for each scene
5. Assign importance levels (1-5) and animation requirements
6. Plan transitions between scenes

OUTPUT REQUIREMENTS:
- Respond with ONLY valid JSON matching the provided schema
- Create 3-8 scenes with clear learning progression
- Each scene should have specific learning objectives
- Importance levels: 5 (critical), 4 (important), 3 (useful), 2 (nice-to-have), 1 (optional)
- Scene types: hook, explanation, story, analysis, revelation, summary, example, comparison

STORY PRINCIPLES:
- Start with attention-grabbing hook
- Build knowledge progressively
- Include surprising facts or revelations
- End with clear summary and takeaways
- Maintain engagement throughout

The response MUST be valid JSON only, no additional text or explanation."""
    
    def _create_fallback_output(self, input_data: FullScriptInput, error_msg: str) -> FullScriptOutput:
        """Create fallback output when generation fails"""
        logger.warning(f"⚠️ Creating fallback full script for topic: {input_data.topic}")
        
        fallback_data = {
            "title": f"Understanding {input_data.topic}",
            "logline": f"An educational exploration of {input_data.topic}",
            "overall_style": input_data.style_profile,
            "main_character": "Glowbie",
            "cosplay_instructions": "Educational presenter outfit appropriate for the topic",
            "story_summary": f"This video explores {input_data.topic} in an engaging and educational manner. Content generation encountered an issue: {error_msg}",
            "scenes": [
                {
                    "scene_number": 1,
                    "scene_type": "hook",
                    "beats": [f"Introduce {input_data.topic} with surprising fact"],
                    "learning_objectives": ["Capture viewer attention"],
                    "needs_animation": True,
                    "transition_to_next": "fade",
                    "scene_importance": 5
                },
                {
                    "scene_number": 2,
                    "scene_type": "explanation", 
                    "beats": [f"Explain the basics of {input_data.topic}"],
                    "learning_objectives": ["Understand fundamentals"],
                    "needs_animation": True,
                    "transition_to_next": "fade",
                    "scene_importance": 4
                },
                {
                    "scene_number": 3,
                    "scene_type": "summary",
                    "beats": [f"Summarize key points about {input_data.topic}"],
                    "learning_objectives": ["Retain key information"],
                    "needs_animation": False,
                    "transition_to_next": "fade",
                    "scene_importance": 3
                }
            ]
        }
        
        return FullScriptOutput.model_validate(fallback_data)
    
    def get_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get the ADK schemas for this agent"""
        return {
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "output_key": self.output_key
        }
