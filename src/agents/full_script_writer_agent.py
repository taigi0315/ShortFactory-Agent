"""
Full Script Writer Agent - Simple LlmAgent Pattern
Direct Pydantic input/output with clean instruction-based approach
"""

import logging
from typing import Dict, Any
import google.genai as genai
from google.genai import types

from model.input_models import FullScriptInput
from model.output_models import FullScriptOutput

logger = logging.getLogger(__name__)


class FullScriptWriterAgent:
    """
    Simple Full Script Writer Agent using direct Pydantic models
    Clean instruction-based approach without complex schema conversion
    """
    
    def __init__(self):
        """Initialize Simple Full Script Writer Agent"""
        self.client = genai.Client()
        
        # Simple instruction - no complex schema conversion needed
        self.instruction = """You are a Full Script Writer Agent that creates comprehensive video scripts.

Given a topic and preferences, create a complete script structure with multiple scenes.

REQUIREMENTS:
- Create 3-7 scenes that tell a complete story
- Each scene should have clear learning objectives and story beats
- Include scene types: hook, explanation, example, conclusion
- Consider the target audience and style preferences
- Ensure logical flow between scenes

OUTPUT FORMAT:
Respond ONLY with valid JSON matching the FullScriptOutput schema.
No additional text, explanations, or markdown formatting."""
        
        # Legacy compatibility properties for tests
        self.input_schema = FullScriptInput.model_json_schema()
        self.output_schema = FullScriptOutput.model_json_schema()
        self.output_key = "full_script_output_result"
        
        logger.info("🚀 Simple Full Script Writer Agent initialized")
    
    async def generate_script(self, input_data: FullScriptInput) -> FullScriptOutput:
        """
        Generate full script with simple direct approach
        
        Args:
            input_data: Type-safe input data
            
        Returns:
            FullScriptOutput: Type-safe output
        """
        try:
            logger.info(f"📝 Generating full script for topic: {input_data.topic}")
            
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
                    response_schema=FullScriptOutput.model_json_schema(),  # Direct Pydantic!
                    temperature=0.8,
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=8192
                )
            )
            
            # Parse and validate with Pydantic
            result = FullScriptOutput.model_validate_json(response.text)
            
            logger.info(f"✅ Full script generated: {len(result.scenes)} scenes")
            return result
            
        except Exception as e:
            logger.error(f"❌ Script generation failed: {e}")
            return self._create_fallback_output(input_data)
    
    def _create_context_prompt(self, input_data: FullScriptInput) -> str:
        """Create context prompt from input data"""
        return f"""
TOPIC: {input_data.topic}

PREFERENCES:
- Length: {input_data.length_preference}
- Style: {input_data.style_profile}
- Target Audience: {input_data.target_audience}
- Language: {input_data.language}

KNOWLEDGE REFERENCES:
{chr(10).join(f"- {ref}" for ref in input_data.knowledge_refs) if input_data.knowledge_refs else "- None provided"}

Create a comprehensive script structure for this topic.
"""
    
    def _create_fallback_output(self, input_data: FullScriptInput) -> FullScriptOutput:
        """Create fallback output when generation fails"""
        logger.warning("⚠️ Creating fallback full script output")
        
        return FullScriptOutput(
            title=f"Script for {input_data.topic}",
            description="Fallback script generated due to processing error",
            overall_style=input_data.style_profile,
            story_summary=f"Educational content about {input_data.topic}",
            total_estimated_duration_ms=300000,  # 5 minutes
            scenes=[
                {
                    "scene_number": 1,
                    "scene_type": "hook",
                    "title": f"Introduction to {input_data.topic}",
                    "description": f"Opening scene introducing {input_data.topic}",
                    "beats": [f"Introduce {input_data.topic}", "Capture viewer attention"],
                    "learning_objectives": [f"Understand what {input_data.topic} is about"],
                    "estimated_duration_ms": 60000,
                    "needs_animation": False,
                    "scene_importance": 5
                },
                {
                    "scene_number": 2,
                    "scene_type": "explanation",
                    "title": f"Understanding {input_data.topic}",
                    "description": f"Main explanation of {input_data.topic}",
                    "beats": [f"Explain key concepts of {input_data.topic}"],
                    "learning_objectives": [f"Learn core principles of {input_data.topic}"],
                    "estimated_duration_ms": 180000,
                    "needs_animation": True,
                    "scene_importance": 5,
                    "transition_to_next": "smooth"
                },
                {
                    "scene_number": 3,
                    "scene_type": "summary",
                    "title": "Summary and Next Steps",
                    "description": f"Wrap up the {input_data.topic} discussion",
                    "beats": ["Summarize key points", "Suggest next steps"],
                    "learning_objectives": ["Consolidate learning"],
                    "estimated_duration_ms": 60000,
                    "needs_animation": False,
                    "scene_importance": 4,
                    "transition_to_next": "fade"
                }
            ]
        )
    
    def get_schemas(self) -> Dict[str, Any]:
        """Get the schemas for this agent (legacy compatibility)"""
        return {
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "output_key": self.output_key
        }
    
    def _create_instruction(self, input_data: FullScriptInput) -> str:
        """Create instruction (legacy compatibility)"""
        return self.instruction