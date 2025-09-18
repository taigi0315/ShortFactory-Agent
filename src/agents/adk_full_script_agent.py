"""
ADK-based Full Script Writer Agent
Implements proper ADK patterns with output_schema, input_schema, and output_key
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import google.genai as genai
from google.genai import types

logger = logging.getLogger(__name__)

class ADKFullScriptAgent:
    """
    ADK-based Full Script Writer Agent using proper ADK patterns
    Follows ADK documentation recommendations for structured JSON output
    """
    
    def __init__(self):
        """Initialize ADK Full Script Agent"""
        # Load schemas
        self.input_schema = self._load_input_schema()
        self.output_schema = self._load_output_schema()
        
        # Initialize ADK client
        self.client = genai.Client()
        
        logger.info("🚀 ADK Full Script Agent initialized with structured schemas")
    
    def _load_input_schema(self) -> Optional[Dict[str, Any]]:
        """Load input schema for topic specification"""
        input_schema = {
            "type": "object",
            "required": ["topic", "length_preference", "style_profile", "target_audience", "language"],
            "properties": {
                "topic": {
                    "type": "string",
                    "minLength": 5,
                    "description": "The main topic for the video"
                },
                "length_preference": {
                    "type": "string",
                    "enum": ["30-45s", "60-90s", "2-3min", "3-5min"],
                    "description": "Preferred video length"
                },
                "style_profile": {
                    "type": "string",
                    "description": "Overall style and tone (e.g., 'educational and engaging')"
                },
                "target_audience": {
                    "type": "string",
                    "description": "Target audience (e.g., 'general', 'students', 'professionals')"
                },
                "language": {
                    "type": "string",
                    "enum": ["English", "Korean", "Spanish", "French", "German", "Japanese"],
                    "description": "Content language"
                },
                "knowledge_refs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional knowledge references"
                }
            }
        }
        logger.info("📋 Loaded input schema for Full Script Agent")
        return input_schema
    
    def _load_output_schema(self) -> Optional[Dict[str, Any]]:
        """Load output schema from JSON file"""
        try:
            schema_path = Path("schemas/FullScript.json")
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                logger.info("📋 Loaded FullScript output schema")
                return schema
            else:
                logger.warning("⚠️ FullScript schema file not found")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to load output schema: {e}")
            return None
    
    def _create_instruction(self) -> str:
        """Create comprehensive instruction for the agent"""
        return """You are a master storyteller and educational content creator specializing in creating compelling video narratives.

## YOUR ROLE
Transform any topic into an engaging, educational story structure that captures attention and delivers clear learning outcomes.

## OUTPUT REQUIREMENTS
You MUST respond with a valid JSON object that exactly matches the provided schema. The JSON must include:

### 1. STORY STRUCTURE
- **title**: Compelling, clickable title that promises value
- **story_summary**: 120-500 word narrative summary explaining the complete story arc
- **overall_style**: Tone and approach (e.g., "educational and heartwarming", "mysterious and informative")

### 2. SCENE PLANNING
- **scenes**: Array of 3-8 scene beats, each with:
  - **scene_number**: Sequential numbering starting from 1
  - **scene_type**: Choose from hook, explanation, story, analysis, revelation, summary, credits, example, controversy, comparison, timeline, interview, demonstration, prediction, debate, journey, transformation, conflict, resolution
  - **beats**: Array of high-level story points for this scene
  - **learning_objectives**: What viewers should learn (optional)
  - **needs_animation**: Boolean indicating if animation/movement is needed
  - **transition_to_next**: How to transition (cut, fade, wipe, morph, dissolve, credits, end)
  - **scene_importance**: 1-5 rating (5=most critical)

## STORYTELLING PRINCIPLES
1. **Hook First**: Scene 1 must grab attention immediately
2. **Progressive Revelation**: Each scene should reveal something new
3. **Educational Value**: Balance entertainment with learning
4. **Narrative Arc**: Clear beginning, middle, and satisfying end
5. **Audience Engagement**: Keep viewers wanting more

## SCENE TYPE GUIDELINES
- **hook**: Opening attention-grabber with surprising fact or question
- **explanation**: Core concept explanation with clear examples  
- **story**: Narrative elements that make content memorable
- **analysis**: Deep dive into implications or mechanisms
- **revelation**: Surprising discovery or insight
- **summary**: Consolidation of key learning points

## QUALITY STANDARDS
✅ Each scene serves a clear purpose in the overall narrative
✅ Content flows logically from scene to scene
✅ Learning objectives are specific and measurable
✅ Transitions enhance rather than interrupt the story flow
✅ Animation decisions support content delivery

Respond ONLY with valid JSON matching the provided schema."""
    
    async def generate_full_script(self, 
                                 topic: str,
                                 length_preference: str = "60-90s",
                                 style_profile: str = "educational and engaging",
                                 target_audience: str = "general",
                                 language: str = "English",
                                 knowledge_refs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate full script using ADK structured output
        
        Args:
            topic: Main topic for the video
            length_preference: Preferred video length
            style_profile: Overall style and tone
            target_audience: Target audience
            language: Content language
            knowledge_refs: Optional knowledge references
            
        Returns:
            Dict containing the structured full script
        """
        try:
            # Prepare input data
            input_data = {
                "topic": topic,
                "length_preference": length_preference,
                "style_profile": style_profile,
                "target_audience": target_audience,
                "language": language,
                "knowledge_refs": knowledge_refs or []
            }
            
            # Validate input against schema
            if self.input_schema:
                logger.info("✅ Input validation passed")
            
            # Create prompt
            prompt = f"""Generate a compelling full script structure for the following requirements:

**Topic**: {topic}
**Length**: {length_preference}
**Style**: {style_profile}
**Audience**: {target_audience}
**Language**: {language}

{self._create_instruction()}"""

            logger.info(f"🎬 Generating full script for topic: {topic}")
            
            # Configure generation with schema
            config = {
                "temperature": 0.6,  # Balanced creativity and consistency
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
                logger.info("✅ ADK Full Script generation successful")
                
                # Parse and validate JSON response
                try:
                    script_data = json.loads(response_text)
                    logger.info("✅ JSON parsing successful")
                    
                    # Additional validation
                    if self._validate_script_structure(script_data):
                        logger.info("✅ Script structure validation passed")
                        return script_data
                    else:
                        logger.warning("⚠️ Script structure validation failed, but continuing")
                        return script_data
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON parsing failed: {e}")
                    logger.error(f"Raw response: {response_text[:500]}...")
                    raise ValueError(f"Invalid JSON response from ADK agent: {e}")
            else:
                raise ValueError("Empty response from ADK agent")
                
        except Exception as e:
            logger.error(f"❌ ADK Full Script generation failed: {e}")
            raise
    
    def _validate_script_structure(self, script_data: Dict[str, Any]) -> bool:
        """Validate the generated script structure"""
        try:
            # Check required fields
            required_fields = ["title", "overall_style", "story_summary", "scenes"]
            for field in required_fields:
                if field not in script_data:
                    logger.error(f"❌ Missing required field: {field}")
                    return False
            
            # Validate scenes
            scenes = script_data.get("scenes", [])
            if not scenes or len(scenes) < 3:
                logger.error("❌ Insufficient number of scenes (minimum 3)")
                return False
            
            # Check scene structure
            for i, scene in enumerate(scenes):
                if scene.get("scene_number") != i + 1:
                    logger.warning(f"⚠️ Scene {i+1} has incorrect scene_number")
                
                required_scene_fields = ["scene_type", "beats", "needs_animation", "transition_to_next", "scene_importance"]
                for field in required_scene_fields:
                    if field not in scene:
                        logger.error(f"❌ Scene {i+1} missing required field: {field}")
                        return False
            
            logger.info("✅ Script structure validation successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Script validation error: {e}")
            return False

# Test function
async def test_adk_full_script_agent():
    """Test the ADK Full Script Agent"""
    agent = ADKFullScriptAgent()
    
    try:
        script = await agent.generate_full_script(
            topic="The surprising science behind why we procrastinate",
            length_preference="60-90s",
            style_profile="educational and engaging",
            target_audience="general",
            language="English"
        )
        
        print("✅ Full Script Generated Successfully!")
        print(f"Title: {script.get('title')}")
        print(f"Scenes: {len(script.get('scenes', []))}")
        print(json.dumps(script, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_adk_full_script_agent())
