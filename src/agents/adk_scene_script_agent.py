"""
ADK-based Scene Script Writer Agent
Implements proper ADK patterns with output_schema, input_schema, and output_key
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import google.genai as genai
from google.genai import types

logger = logging.getLogger(__name__)

class ADKSceneScriptAgent:
    """
    ADK-based Scene Script Writer Agent using proper ADK patterns
    Follows ADK documentation recommendations for structured JSON output
    """
    
    def __init__(self):
        """Initialize ADK Scene Script Agent"""
        # Load schemas
        self.input_schema = self._load_input_schema()
        self.output_schema = self._load_output_schema()
        
        # Initialize ADK client
        self.client = genai.Client()
        
        logger.info("🚀 ADK Scene Script Agent initialized with structured schemas")
    
    def _load_input_schema(self) -> Optional[Dict[str, Any]]:
        """Load input schema for scene expansion specification"""
        input_schema = {
            "type": "object",
            "required": ["scene_data", "global_context"],
            "properties": {
                "scene_data": {
                    "type": "object",
                    "required": ["scene_number", "scene_type", "beats"],
                    "properties": {
                        "scene_number": {"type": "integer", "minimum": 1},
                        "scene_type": {"type": "string"},
                        "beats": {"type": "array", "items": {"type": "string"}},
                        "learning_objectives": {"type": "array", "items": {"type": "string"}},
                        "needs_animation": {"type": "boolean"},
                        "transition_to_next": {"type": "string"},
                        "scene_importance": {"type": "integer", "minimum": 1, "maximum": 5}
                    }
                },
                "global_context": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "overall_style": {"type": "string"},
                        "story_summary": {"type": "string"},
                        "main_character": {"type": "string"},
                        "target_audience": {"type": "string"}
                    }
                },
                "previous_scenes": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Previously generated scenes for continuity"
                }
            }
        }
        logger.info("📋 Loaded input schema for Scene Script Agent")
        return input_schema
    
    def _load_output_schema(self) -> Optional[Dict[str, Any]]:
        """Load output schema from JSON file"""
        try:
            schema_path = Path("schemas/ScenePackage.json")
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                logger.info("📋 Loaded ScenePackage output schema")
                return schema
            else:
                logger.warning("⚠️ ScenePackage schema file not found")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to load output schema: {e}")
            return None
    
    def _create_instruction(self) -> str:
        """Create comprehensive instruction for the scene script agent"""
        return """You are a master scene writer who transforms high-level story beats into production-ready scene packages.

## YOUR ROLE
Take scene beats and expand them into detailed, timed, production-ready packages with narration, visuals, and technical specifications.

## OUTPUT REQUIREMENTS
You MUST respond with a valid JSON object that exactly matches the provided ScenePackage schema. The JSON must include:

### 1. NARRATION SCRIPT
- **narration_script**: Array of timed narration lines with:
  - **line**: Compelling, conversational text (not teacher-speak)
  - **at_ms**: Precise timing in milliseconds
  - **pause_ms**: Optional pause duration after line

### 2. VISUAL SPECIFICATIONS  
- **visuals**: Array of 1-8 visual frames, each with:
  - **frame_id**: Format like "1A", "2B", etc.
  - **shot_type**: wide, medium, close, macro, extreme_wide, extreme_close
  - **image_prompt**: Detailed 40+ character prompt for image generation
  - **aspect_ratio**: 16:9, 9:16, 1:1, 4:5, 3:2, or 2:3
  - Optional: camera_motion, character_pose, expression, background, lighting, color_mood

### 3. TTS CONFIGURATION
- **tts**: Text-to-speech settings with:
  - **engine**: "elevenlabs" (preferred), "openai", "google", or "azure"
  - **voice**: Voice identifier (e.g., "Adam", "Rachel")
  - **elevenlabs_settings**: Stability, similarity_boost, style, speed, loudness (0.0-1.0)

### 4. TIMING & CONTINUITY
- **timing**: Total scene duration in milliseconds (minimum 1000ms)
- **continuity**: Scene transition information
- Optional: **sfx_cues**, **on_screen_text**, **dialogue**

## CONTENT PRINCIPLES
1. **ELABORATION**: Add rich details, facts, compelling narratives
2. **HOOKING**: Include attention-grabbing elements and curiosity gaps  
3. **EDUCATIONAL**: Balance entertainment with clear learning outcomes
4. **VISUAL DETAIL**: Specify shot types, camera motion, lighting, color mood
5. **CONTINUITY**: Maintain consistency with previous scenes

## NARRATION GUIDELINES
- Use conversational, engaging language
- Include specific numbers, names, dates, facts
- React to information like a real person would
- Start with most surprising/important information
- Avoid teacher-speak or formal presentations

## VISUAL PROMPT GUIDELINES
- Be extremely specific about visual elements
- Include technical specifications for image generation
- Specify lighting, composition, and style details
- Ensure prompts are 40+ characters minimum
- Consider informative visualization needs

## TIMING CONSIDERATIONS
- Plan realistic narration pacing (150-180 words per minute)
- Allow pauses for emphasis and comprehension
- Coordinate visual changes with narration beats
- Ensure total timing matches content density

Respond ONLY with valid JSON matching the ScenePackage schema."""
    
    async def expand_scene(self,
                          scene_data: Dict[str, Any],
                          global_context: Dict[str, Any],
                          previous_scenes: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Expand scene beat into production-ready scene package using ADK structured output
        
        Args:
            scene_data: Scene beat information from Full Script Writer
            global_context: Global story context
            previous_scenes: Previously generated scenes for continuity
            
        Returns:
            Dict containing the structured scene package
        """
        try:
            scene_number = scene_data.get("scene_number", 1)
            scene_type = scene_data.get("scene_type", "explanation")
            
            logger.info(f"🎬 Expanding scene {scene_number} ({scene_type})")
            
            # Prepare input data
            input_data = {
                "scene_data": scene_data,
                "global_context": global_context,
                "previous_scenes": previous_scenes or []
            }
            
            # Create comprehensive prompt
            prompt = self._create_scene_prompt(scene_data, global_context, previous_scenes)
            
            # Configure generation with schema
            config = {
                "temperature": 0.7,  # Higher creativity for scene details
                "top_p": 0.8,
                "top_k": 30,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json"
            }
            
            # Add output schema for structured response
            if self.output_schema:
                config["response_schema"] = self.output_schema
                logger.info("🎯 Using output schema for structured JSON response")
            
            # Generate content
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=config
            )
            
            if response and hasattr(response, 'text') and response.text:
                response_text = response.text.strip()
                logger.info(f"✅ ADK Scene {scene_number} generation successful")
                
                # Parse and validate JSON response
                try:
                    scene_package = json.loads(response_text)
                    logger.info(f"✅ JSON parsing successful for scene {scene_number}")
                    
                    # Additional validation
                    if self._validate_scene_package(scene_package, scene_number):
                        logger.info(f"✅ Scene {scene_number} structure validation passed")
                        return scene_package
                    else:
                        logger.warning(f"⚠️ Scene {scene_number} structure validation failed, but continuing")
                        return scene_package
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON parsing failed for scene {scene_number}: {e}")
                    logger.error(f"Raw response: {response_text[:500]}...")
                    raise ValueError(f"Invalid JSON response from ADK agent: {e}")
            else:
                raise ValueError(f"Empty response from ADK agent for scene {scene_number}")
                
        except Exception as e:
            logger.error(f"❌ ADK Scene {scene_number} generation failed: {e}")
            raise
    
    def _create_scene_prompt(self, 
                           scene_data: Dict[str, Any], 
                           global_context: Dict[str, Any],
                           previous_scenes: Optional[List[Dict[str, Any]]] = None) -> str:
        """Create detailed prompt for scene expansion"""
        
        scene_number = scene_data.get("scene_number", 1)
        scene_type = scene_data.get("scene_type", "explanation")
        beats = scene_data.get("beats", [])
        learning_objectives = scene_data.get("learning_objectives", [])
        
        # Build context from previous scenes
        previous_context = ""
        if previous_scenes:
            previous_context = f"""
## PREVIOUS SCENES CONTEXT
{self._summarize_previous_scenes(previous_scenes)}
"""
        
        prompt = f"""Expand the following scene beat into a complete, production-ready scene package:

## SCENE TO EXPAND
**Scene Number**: {scene_number}
**Scene Type**: {scene_type}
**Story Beats**: {', '.join(beats)}
**Learning Objectives**: {', '.join(learning_objectives) if learning_objectives else 'None specified'}

## GLOBAL STORY CONTEXT
**Title**: {global_context.get('title', 'Untitled')}
**Overall Style**: {global_context.get('overall_style', 'Informative')}
**Story Summary**: {global_context.get('story_summary', 'No summary provided')}
**Target Audience**: {global_context.get('target_audience', 'General')}

{previous_context}

## SPECIFIC REQUIREMENTS FOR THIS SCENE
- Transform the story beats into engaging, conversational narration
- Create 3-6 visual frames that support the informative content
- Specify precise timing for all narration elements
- Include appropriate TTS settings for the scene type
- Ensure visual continuity with previous scenes
- Add informative depth while maintaining engagement

{self._create_instruction()}"""

        return prompt
    
    def _summarize_previous_scenes(self, previous_scenes: List[Dict[str, Any]]) -> str:
        """Summarize previous scenes for continuity"""
        summaries = []
        for scene in previous_scenes:
            scene_num = scene.get("scene_number", "?")
            narration = scene.get("narration_script", [])
            first_line = narration[0].get("line", "No narration") if narration else "No narration"
            summaries.append(f"Scene {scene_num}: {first_line[:100]}...")
        
        return "\n".join(summaries)
    
    def _validate_scene_package(self, scene_package: Dict[str, Any], scene_number: int) -> bool:
        """Validate the generated scene package structure"""
        try:
            # Check required fields
            required_fields = ["scene_number", "narration_script", "visuals", "tts", "timing"]
            for field in required_fields:
                if field not in scene_package:
                    logger.error(f"❌ Scene {scene_number} missing required field: {field}")
                    return False
            
            # Validate narration script
            narration = scene_package.get("narration_script", [])
            if not narration:
                logger.error(f"❌ Scene {scene_number} has empty narration_script")
                return False
            
            # Validate visuals
            visuals = scene_package.get("visuals", [])
            if not visuals:
                logger.error(f"❌ Scene {scene_number} has empty visuals array")
                return False
            
            # Check visual frame IDs
            for i, visual in enumerate(visuals):
                if "frame_id" not in visual:
                    logger.error(f"❌ Scene {scene_number}, visual {i} missing frame_id")
                    return False
                if "image_prompt" not in visual or len(visual.get("image_prompt", "")) < 40:
                    logger.error(f"❌ Scene {scene_number}, visual {i} has insufficient image_prompt")
                    return False
            
            # Validate timing
            timing = scene_package.get("timing", {})
            total_ms = timing.get("total_ms", 0)
            if total_ms < 1000:
                logger.error(f"❌ Scene {scene_number} has insufficient duration: {total_ms}ms")
                return False
            
            logger.info(f"✅ Scene {scene_number} structure validation successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Scene {scene_number} validation error: {e}")
            return False

# Test function
async def test_adk_scene_script_agent():
    """Test the ADK Scene Script Agent"""
    agent = ADKSceneScriptAgent()
    
    # Mock scene data
    scene_data = {
        "scene_number": 1,
        "scene_type": "hook",
        "beats": ["Introduce surprising fact about procrastination", "Hook viewers with relatable scenario"],
        "learning_objectives": ["Understand the neuroscience behind procrastination"],
        "needs_animation": True,
        "transition_to_next": "fade",
        "scene_importance": 5
    }
    
    global_context = {
        "title": "The Surprising Science Behind Why We Procrastinate",
        "overall_style": "informative and engaging",
        "story_summary": "An exploration of the psychological and neurological factors that drive procrastination behavior.",
        "target_audience": "general"
    }
    
    try:
        scene_package = await agent.expand_scene(scene_data, global_context)
        
        print("✅ Scene Package Generated Successfully!")
        print(f"Scene Number: {scene_package.get('scene_number')}")
        print(f"Narration Lines: {len(scene_package.get('narration_script', []))}")
        print(f"Visual Frames: {len(scene_package.get('visuals', []))}")
        print(json.dumps(scene_package, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_adk_scene_script_agent())
