"""
Test: Full Script Writer Agent
Type-safe Pydantic-based agent testing
"""

import pytest
import sys
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.full_script_writer_agent import FullScriptWriterAgent
from schemas.input_models import FullScriptInput, LengthPreference, Language
from schemas.output_models import FullScriptOutput


class TestFullScriptWriterAgent:
    """Full Script Writer Agent unit tests"""

    def test_agent_initialization(self):
        """Test agent initialization with Pydantic schemas"""
        
        with patch('agents.full_script_writer_agent.genai.Client'):
            agent = FullScriptWriterAgent()
            
            # Check schemas are generated
            assert hasattr(agent, 'input_schema')
            assert hasattr(agent, 'output_schema')
            assert hasattr(agent, 'output_key')
            
            # Check schema structure
            assert agent.input_schema["type"] == "object"
            assert "properties" in agent.input_schema
            assert agent.output_key == "full_script_output_result"

    def test_get_schemas_method(self):
        """Test schema retrieval method"""
        
        with patch('agents.full_script_writer_agent.genai.Client'):
            agent = FullScriptWriterAgent()
            
            schemas = agent.get_schemas()
            
            assert "input_schema" in schemas
            assert "output_schema" in schemas
            assert "output_key" in schemas
            
            # Verify they're valid dictionaries
            assert isinstance(schemas["input_schema"], dict)
            assert isinstance(schemas["output_schema"], dict)
            assert isinstance(schemas["output_key"], str)

    def test_type_safe_input_creation(self):
        """Test type-safe input data creation"""
        
        # Create type-safe input
        input_data = FullScriptInput(
            topic="Why cats purr",
            length_preference=LengthPreference.SHORT,
            style_profile="friendly and informative",
            target_audience="pet owners",
            language=Language.ENGLISH
        )
        
        # Verify type safety
        assert input_data.topic == "Why cats purr"
        assert input_data.length_preference == "30-45s"
        assert input_data.language == "English"
        
        # Verify serialization
        input_dict = input_data.model_dump()
        assert isinstance(input_dict, dict)
        assert input_dict["topic"] == "Why cats purr"

    @pytest.mark.asyncio
    async def test_generate_script_with_mock_response(self):
        """Test script generation with mocked LLM response"""
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "title": "The Mystery of Cat Purring",
            "logline": "Discover the science behind why cats purr",
            "overall_style": "friendly and informative",
            "main_character": "Glowbie",
            "cosplay_instructions": "Cat-loving scientist with lab coat",
            "story_summary": "This video explores the fascinating science behind cat purring.",
            "scenes": [
                {
                    "scene_number": 1,
                    "scene_type": "hook",
                    "beats": ["Cats purr in mysterious ways"],
                    "learning_objectives": ["Capture attention"],
                    "needs_animation": True,
                    "transition_to_next": "fade",
                    "scene_importance": 5
                },
                {
                    "scene_number": 2,
                    "scene_type": "explanation",
                    "beats": ["The science of purring"],
                    "learning_objectives": ["Understand mechanism"],
                    "needs_animation": True,
                    "transition_to_next": "fade", 
                    "scene_importance": 4
                },
                {
                    "scene_number": 3,
                    "scene_type": "summary",
                    "beats": ["Why purring matters"],
                    "learning_objectives": ["Remember key points"],
                    "needs_animation": False,
                    "transition_to_next": "fade",
                    "scene_importance": 3
                }
            ]
        })
        
        with patch('agents.full_script_writer_agent.genai.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client.agenerate_content = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client
            
            agent = FullScriptWriterAgent()
            
            # Create type-safe input
            input_data = FullScriptInput(
                topic="Why cats purr",
                length_preference=LengthPreference.SHORT
            )
            
            # Generate script
            result = await agent.generate_script(input_data)
            
            # Verify type-safe output
            assert isinstance(result, FullScriptOutput)
            assert result.title == "The Mystery of Cat Purring"
            assert len(result.scenes) == 3
            assert result.scenes[0].scene_number == 1
            assert result.scenes[0].scene_type == "hook"

    def test_fallback_output_creation(self):
        """Test fallback output when generation fails"""
        
        with patch('agents.full_script_writer_agent.genai.Client'):
            agent = FullScriptWriterAgent()
            
            input_data = FullScriptInput(
                topic="Test topic",
                length_preference=LengthPreference.MEDIUM
            )
            
            # Create fallback
            fallback = agent._create_fallback_output(input_data, "Test error")
            
            # Verify fallback is valid
            assert isinstance(fallback, FullScriptOutput)
            assert "Test topic" in fallback.title
            assert len(fallback.scenes) >= 3
            assert fallback.scenes[0].scene_importance == 5  # Hook should be highest priority

    def test_instruction_creation(self):
        """Test instruction prompt creation"""
        
        with patch('agents.full_script_writer_agent.genai.Client'):
            agent = FullScriptWriterAgent()
            
            input_data = FullScriptInput(
                topic="Quantum physics",
                target_audience="students",
                style_profile="educational and clear"
            )
            
            instruction = agent._create_instruction(input_data)
            
            # Verify instruction contains key elements
            assert "Quantum physics" in instruction
            assert "students" in instruction
            assert "educational and clear" in instruction
            assert "JSON" in instruction
            assert "schema" in instruction

    @pytest.mark.asyncio
    async def test_malformed_json_handling(self):
        """Test handling of malformed JSON response"""
        
        # Mock malformed response
        mock_response = MagicMock()
        mock_response.text = '{"title": "Test", "scenes": [invalid json'
        
        with patch('agents.full_script_writer_agent.genai.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client.agenerate_content = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client
            
            agent = FullScriptWriterAgent()
            
            input_data = FullScriptInput(topic="Test topic")
            
            # Should fallback gracefully
            result = await agent.generate_script(input_data)
            
            # Verify fallback was used
            assert isinstance(result, FullScriptOutput)
            assert "Test topic" in result.title
            assert len(result.scenes) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
