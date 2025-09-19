"""
LlmAgent - Simple Pydantic-based Agent Wrapper
Clean abstraction over Google AI with direct Pydantic model support
"""

import json
import logging
from typing import Type, Dict, Any, Optional
import google.genai as genai
from google.genai import types
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LlmAgent:
    """
    Simple LlmAgent wrapper for Google AI with direct Pydantic support
    Follows the clean pattern: instruction + output_schema + output_key
    """
    
    def __init__(self,
                 name: str,
                 model: str = "gemini-2.5-flash",
                 description: str = "",
                 instruction: str = "",
                 output_schema: Type[BaseModel] = None,
                 output_key: str = "result"):
        """
        Initialize LlmAgent with Pydantic schema
        
        Args:
            name: Agent name
            model: LLM model to use
            description: Agent description
            instruction: System instruction prompt
            output_schema: Pydantic model for structured output
            output_key: Key for storing result in state
        """
        self.name = name
        self.model = model
        self.description = description
        self.instruction = instruction
        self.output_schema = output_schema
        self.output_key = output_key
        
        # Initialize Google AI client
        self.client = genai.Client()
        
        logger.info(f"🚀 LlmAgent '{name}' initialized with Pydantic schema")
    
    async def run(self, input_data: Any) -> BaseModel:
        """
        Run agent with input data and return structured Pydantic output
        
        Args:
            input_data: Input data (can be string, dict, or Pydantic model)
            
        Returns:
            BaseModel: Structured Pydantic output
        """
        try:
            # Convert input to prompt string
            if isinstance(input_data, BaseModel):
                prompt_text = input_data.model_dump_json(indent=2)
            elif isinstance(input_data, dict):
                prompt_text = json.dumps(input_data, indent=2)
            else:
                prompt_text = str(input_data)
            
            logger.info(f"🤖 Running {self.name} agent...")
            
            # Use Google AI structured generation
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(parts=[
                        types.Part(text=prompt_text)
                    ])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=self.instruction,
                    response_schema=self.output_schema.model_json_schema() if self.output_schema else None,
                    temperature=0.8,
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=8192
                )
            )
            
            # Parse structured response with Pydantic
            if self.output_schema:
                # Clean response text (remove markdown if present)
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    # Extract JSON from markdown
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    if start != -1 and end != 0:
                        response_text = response_text[start:end]
                
                result = self.output_schema.model_validate_json(response_text)
                logger.info(f"✅ {self.name} completed successfully")
                return result
            else:
                # No schema - return raw response
                return response.text
                
        except Exception as e:
            logger.error(f"❌ {self.name} failed: {e}")
            raise
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema information for this agent"""
        return {
            "name": self.name,
            "model": self.model,
            "description": self.description,
            "output_schema": self.output_schema.model_json_schema() if self.output_schema else None,
            "output_key": self.output_key
        }
