"""
Test: Scene Script Writer Agent
Type-safe Pydantic-based scene script agent testing
"""

import pytest
import sys
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.scene_script_writer_agent import SceneScriptWriterAgent
from model.input_models import SceneExpansionInput
from model.output_models import ScenePackageOutput, NarrationLine, VisualFrame, TTSSettings


class TestSceneScriptWriterAgent:
    """Scene Script Writer Agent unit tests"""

    def test_agent_initialization(self):
        """Test agent initialization with Pydantic schemas"""
        
        with patch('agents.scene_script_writer_agent.genai.Client'):
            agent = SceneScriptWriterAgent()
            
            # Check schemas are generated
            assert hasattr(agent, 'input_schema')
            assert hasattr(agent, 'output_schema')
            assert hasattr(agent, 'output_key')
            
            # Check schema structure
            assert agent.input_schema["type"] == "object"
            assert "properties" in agent.input_schema
            assert agent.output_key == "scene_package_output_result"

    def test_type_safe_input_creation(self):
        """Test type-safe input data creation"""
        
        # Create type-safe input
        input_data = SceneExpansionInput(
            scene_data={
                "scene_number": 1,
                "scene_type": "hook",
                "beats": ["Introduce surprising fact about cats"],
                "learning_objectives": ["Capture viewer attention"],
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
        
        # Verify serialization
        input_dict = input_data.model_dump()
        assert isinstance(input_dict, dict)
        assert input_dict["scene_data"]["scene_number"] == 1

    @pytest.mark.asyncio
    async def test_expand_scene_with_mock_response(self):
        """Test scene expansion with mocked LLM response"""
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "scene_number": 1,
            "narration_script": [
                {
                    "line": "Did you know that cats purr at a frequency that can heal bones?",
                    "at_ms": 0,
                    "pause_ms": 800
                },
                {
                    "line": "This amazing ability has fascinated scientists for decades.",
                    "at_ms": 4000,
                    "pause_ms": 500
                }
            ],
            "visuals": [
                {
                    "frame_id": "1A",
                    "shot_type": "medium",
                    "image_prompt": "Glowbie character dressed as a veterinarian, standing next to a purring cat with visible sound waves, educational and friendly atmosphere",
                    "aspect_ratio": "16:9",
                    "character_pose": "pointing to cat",
                    "expression": "amazed",
                    "background": "veterinary clinic"
                },
                {
                    "frame_id": "1B", 
                    "shot_type": "close",
                    "image_prompt": "Close-up of Glowbie examining scientific data about cat purring frequencies, with charts and graphs visible",
                    "aspect_ratio": "16:9",
                    "character_pose": "studying data",
                    "expression": "curious"
                }
            ],
            "tts": {
                "engine": "lemonfox",
                "voice": "sarah",
                "language": "en-US",
                "speed": 1.1
            },
            "timing": {
                "total_ms": 8000,
                "estimated": True
            }
        })
        
        with patch('agents.scene_script_writer_agent.genai.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client.agenerate_content = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client
            
            agent = SceneScriptWriterAgent()
            
            # Create type-safe input
            input_data = SceneExpansionInput(
                scene_data={
                    "scene_number": 1,
                    "scene_type": "hook",
                    "beats": ["Cats purr for healing"],
                    "learning_objectives": ["Understand cat purring"],
                    "needs_animation": True,
                    "scene_importance": 5
                },
                global_context={
                    "main_character": "Glowbie",
                    "overall_style": "educational and engaging"
                }
            )
            
            # Expand scene
            result = await agent.expand_scene(input_data)
            
            # Verify type-safe output
            assert isinstance(result, ScenePackageOutput)
            assert result.scene_number == 1
            assert len(result.narration_script) == 2
            assert len(result.visuals) == 2
            
            # Check narration details
            first_line = result.narration_script[0]
            assert isinstance(first_line, NarrationLine)
            assert "cats purr" in first_line.line.lower()
            assert first_line.at_ms == 0
            
            # Check visual details
            first_visual = result.visuals[0]
            assert isinstance(first_visual, VisualFrame)
            assert first_visual.frame_id == "1A"
            assert len(first_visual.image_prompt) >= 40
            
            # Check TTS settings
            assert isinstance(result.tts, TTSSettings)
            assert result.tts.engine == "lemonfox"
            assert result.tts.voice == "sarah"

    def test_fallback_output_creation(self):
        """Test fallback output when generation fails"""
        
        with patch('agents.scene_script_writer_agent.genai.Client'):
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
            
            # Create fallback
            fallback = agent._create_fallback_output(input_data, "Test error")
            
            # Verify fallback is valid
            assert isinstance(fallback, ScenePackageOutput)
            assert fallback.scene_number == 2
            assert len(fallback.narration_script) >= 1
            assert len(fallback.visuals) >= 1
            assert fallback.visuals[0].frame_id == "2A"

    def test_instruction_creation(self):
        """Test instruction prompt creation"""
        
        with patch('agents.scene_script_writer_agent.genai.Client'):
            agent = SceneScriptWriterAgent()
            
            input_data = SceneExpansionInput(
                scene_data={
                    "scene_number": 3,
                    "scene_type": "revelation",
                    "beats": ["Surprising discovery about quantum physics"],
                    "learning_objectives": ["Understand quantum concepts"]
                },
                global_context={
                    "main_character": "Glowbie",
                    "overall_style": "scientific and mysterious",
                    "target_audience": "students"
                }
            )
            
            instruction = agent._create_instruction(input_data)
            
            # Verify instruction contains key elements
            assert "Scene 3" in instruction
            assert "revelation" in instruction
            assert "quantum physics" in instruction
            assert "Glowbie" in instruction
            assert "students" in instruction
            assert "JSON" in instruction
            assert "schema" in instruction

    @pytest.mark.asyncio
    async def test_scene_with_previous_scenes_context(self):
        """Test scene expansion with previous scenes context"""
        
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "scene_number": 2,
            "narration_script": [
                {
                    "line": "Building on what we learned in the previous scene, let's dive deeper.",
                    "at_ms": 0,
                    "pause_ms": 600
                }
            ],
            "visuals": [
                {
                    "frame_id": "2A",
                    "shot_type": "medium",
                    "image_prompt": "Glowbie character continuing the explanation from the previous scene, showing continuity",
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
                "estimated": True
            }
        })
        
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
                    "beats": ["Continue the explanation"],
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
            assert "previous scene" in result.narration_script[0].line.lower()

    def test_get_schemas_method(self):
        """Test schema retrieval method"""
        
        with patch('agents.scene_script_writer_agent.genai.Client'):
            agent = SceneScriptWriterAgent()
            
            schemas = agent.get_schemas()
            
            assert "input_schema" in schemas
            assert "output_schema" in schemas
            assert "output_key" in schemas
            
            # Verify they're valid
            assert isinstance(schemas["input_schema"], dict)
            assert isinstance(schemas["output_schema"], dict)
            assert schemas["output_key"] == "scene_package_output_result"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
