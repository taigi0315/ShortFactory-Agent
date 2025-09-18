"""
Test: Scene Script Writer Agent - Simple Pattern
Clean tests for the simplified agent
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.scene_script_writer_agent import SceneScriptWriterAgent
from model.input_models import SceneExpansionInput
from model.output_models import ScenePackageOutput


class TestSceneScriptWriterAgent:
    """Scene Script Writer Agent unit tests - Simple pattern"""

    def test_agent_initialization(self):
        """Test agent initialization"""
        
        with patch('agents.scene_script_writer_agent.genai.Client'):
            agent = SceneScriptWriterAgent()
            
            # Check basic properties exist
            assert hasattr(agent, 'instruction')
            assert hasattr(agent, 'client')
            assert isinstance(agent.instruction, str)
            assert "Scene Script Writer Agent" in agent.instruction

    def test_type_safe_input_creation(self):
        """Test type-safe input data creation"""
        
        # Create type-safe input
        input_data = SceneExpansionInput(
            scene_data={
                "scene_number": 1,
                "scene_type": "hook",
                "beats": ["Introduce surprising fact"],
                "learning_objectives": ["Capture attention"],
                "needs_animation": True,
                "scene_importance": 5
            },
            global_context={
                "main_character": "Glowbie",
                "overall_style": "educational and engaging",
                "target_audience": "general"
            }
        )
        
        # Verify type safety
        assert input_data.scene_data["scene_number"] == 1
        assert input_data.scene_data["scene_type"] == "hook"
        assert input_data.global_context["main_character"] == "Glowbie"

    @pytest.mark.asyncio
    async def test_expand_scene_with_mock_response(self):
        """Test scene expansion with mocked LLM response"""
        
        # Mock successful LLM response
        mock_response = MagicMock()
        mock_response.text = """{
            "scene_number": 1,
            "narration_script": [
                {
                    "line": "Did you know that cats purr at healing frequencies?",
                    "at_ms": 0,
                    "pause_ms": 800
                }
            ],
            "visuals": [
                {
                    "frame_id": "1A",
                    "shot_type": "medium",
                    "image_prompt": "Glowbie character explaining cat purring with scientific diagrams in background",
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
                "total_ms": 8000,
                "estimated": true
            }
        }"""
        
        with patch('agents.scene_script_writer_agent.genai.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client.agenerate_content = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client
            
            agent = SceneScriptWriterAgent()
            
            # Create input
            input_data = SceneExpansionInput(
                scene_data={
                    "scene_number": 1,
                    "scene_type": "hook",
                    "beats": ["Cats purr for healing"],
                    "learning_objectives": ["Understand cat purring"]
                },
                global_context={"main_character": "Glowbie"}
            )
            
            # Expand scene
            result = await agent.expand_scene(input_data)
            
            # Verify type-safe output
            assert isinstance(result, ScenePackageOutput)
            assert result.scene_number == 1
            assert len(result.narration_script) == 1
            assert len(result.visuals) == 1
            assert result.visuals[0].frame_id == "1A"

    @pytest.mark.asyncio
    async def test_fallback_on_error(self):
        """Test fallback when generation fails"""
        
        with patch('agents.scene_script_writer_agent.genai.Client') as mock_client_class:
            # Mock client that throws error
            mock_client = MagicMock()
            mock_client.agenerate_content = AsyncMock(side_effect=Exception("API Error"))
            mock_client_class.return_value = mock_client
            
            agent = SceneScriptWriterAgent()
            
            input_data = SceneExpansionInput(
                scene_data={
                    "scene_number": 2,
                    "scene_type": "explanation",
                    "beats": ["Test beat"],
                    "learning_objectives": ["Test objective"]
                },
                global_context={"main_character": "Glowbie"}
            )
            
            # Should fallback gracefully
            result = await agent.expand_scene(input_data)
            
            # Verify fallback result
            assert isinstance(result, ScenePackageOutput)
            assert result.scene_number == 2
            assert len(result.narration_script) >= 1
            assert len(result.visuals) >= 1

    @pytest.mark.asyncio
    async def test_scene_with_previous_context(self):
        """Test scene expansion with previous scenes context"""
        
        mock_response = MagicMock()
        mock_response.text = """{
            "scene_number": 2,
            "narration_script": [
                {
                    "line": "Building on what we learned, let's dive deeper.",
                    "at_ms": 0,
                    "pause_ms": 600
                }
            ],
            "visuals": [
                {
                    "frame_id": "2A",
                    "shot_type": "medium", 
                    "image_prompt": "Glowbie character continuing explanation with continuity from previous scene",
                    "aspect_ratio": "16:9"
                }
            ],
            "tts": {
                "engine": "lemonfox",
                "voice": "sarah",
                "speed": 1.0
            },
            "timing": {
                "total_ms": 5000,
                "estimated": true
            }
        }"""
        
        with patch('agents.scene_script_writer_agent.genai.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client.agenerate_content = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client
            
            agent = SceneScriptWriterAgent()
            
            # Create input with previous scenes
            input_data = SceneExpansionInput(
                scene_data={
                    "scene_number": 2,
                    "scene_type": "explanation",
                    "beats": ["Continue explanation"],
                    "learning_objectives": ["Build on previous knowledge"]
                },
                global_context={"main_character": "Glowbie"},
                previous_scenes=[
                    {
                        "scene_number": 1,
                        "scene_type": "hook",
                        "summary": "Introduced the topic"
                    }
                ]
            )
            
            result = await agent.expand_scene(input_data)
            
            # Verify continuity
            assert result.scene_number == 2
            assert len(result.narration_script) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])