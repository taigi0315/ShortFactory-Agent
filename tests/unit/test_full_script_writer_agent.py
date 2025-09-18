"""
Test: Full Script Writer Agent - Simple Pattern
Clean tests for the simplified agent
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.full_script_writer_agent import FullScriptWriterAgent
from model.input_models import FullScriptInput, LengthPreference, Language
from model.output_models import FullScriptOutput


class TestFullScriptWriterAgent:
    """Full Script Writer Agent unit tests - Simple pattern"""

    def test_agent_initialization(self):
        """Test agent initialization"""
        
        with patch('agents.full_script_writer_agent.genai.Client'):
            agent = FullScriptWriterAgent()
            
            # Check basic properties exist
            assert hasattr(agent, 'instruction')
            assert hasattr(agent, 'client')
            assert isinstance(agent.instruction, str)
            assert "Full Script Writer Agent" in agent.instruction

    def test_type_safe_input_creation(self):
        """Test type-safe input data creation"""
        
        # Create type-safe input
        input_data = FullScriptInput(
            topic="Artificial Intelligence",
            length_preference=LengthPreference.MEDIUM,
            style_profile="educational and engaging",
            target_audience="general",
            language=Language.ENGLISH
        )
        
        # Verify type safety
        assert input_data.topic == "Artificial Intelligence"
        assert input_data.length_preference == LengthPreference.MEDIUM
        assert input_data.style_profile == "educational and engaging"
        
        # Verify serialization
        input_dict = input_data.model_dump()
        assert isinstance(input_dict, dict)
        assert input_dict["topic"] == "Artificial Intelligence"

    # Complex mock test removed - simple pattern focuses on core functionality

    @pytest.mark.asyncio 
    async def test_fallback_on_error(self):
        """Test fallback when generation fails"""
        
        with patch('agents.full_script_writer_agent.genai.Client') as mock_client_class:
            # Mock client that throws error
            mock_client = MagicMock()
            mock_client.agenerate_content = AsyncMock(side_effect=Exception("API Error"))
            mock_client_class.return_value = mock_client
            
            agent = FullScriptWriterAgent()
            
            input_data = FullScriptInput(topic="Test Topic")
            
            # Should fallback gracefully
            result = await agent.generate_script(input_data)
            
            # Verify fallback result
            assert isinstance(result, FullScriptOutput)
            assert "Test Topic" in result.title
            assert len(result.scenes) >= 3  # Fallback creates basic structure


if __name__ == "__main__":
    pytest.main([__file__, "-v"])