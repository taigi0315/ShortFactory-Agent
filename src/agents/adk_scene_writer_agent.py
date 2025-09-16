"""
ADK Scene Writer Agent
Generates detailed scene scripts with comprehensive information for image/video generation
"""

import json
import logging
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import BaseTool

from model.models import VideoScript, Scene, SceneType, VoiceTone, ImageStyle, TransitionType
from core.session_manager import SessionManager
from core.shared_context import SharedContextManager, SharedContext

logger = logging.getLogger(__name__)

class SceneWritingTool(BaseTool):
    """Tool for writing detailed scene scripts"""
    
    def __init__(self, session_manager: SessionManager):
        super().__init__(
            name="write_scene_script",
            description="Write detailed scene script with comprehensive information for image/video generation"
        )
        self.session_manager = session_manager
    
    async def run(self, scene_number: int, scene_type: str, overall_story: str, 
                  full_script_context: str, subject: str, **kwargs) -> Dict[str, Any]:
        """
        Write detailed scene script
        
        Args:
            scene_number: Scene number (1-based)
            scene_type: Type of scene (hook, explanation, etc.)
            overall_story: The overall story being told
            full_script_context: Complete script context for understanding
            subject: Main subject/topic
            **kwargs: Additional parameters
            
        Returns:
            Dict with detailed scene information
        """
        try:
            logger.info(f"Writing detailed scene {scene_number} of type {scene_type}")
            
            # This will be called by the ADK agent
            return {
                "scene_number": scene_number,
                "scene_type": scene_type,
                "detailed_script": f"Detailed scene {scene_number} script for {subject}",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error writing scene script: {str(e)}")
            return {
                "scene_number": scene_number,
                "error": str(e),
                "success": False
            }

class ADKSceneWriterAgent(Agent):
    """ADK Scene Writer Agent for detailed scene generation"""
    
    def __init__(self, session_manager: SessionManager, shared_context_manager: SharedContextManager = None):
        """
        Initialize ADK Scene Writer Agent
        
        Args:
            session_manager: SessionManager instance for file operations
        """
        # Check if API key is available
        import os
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        # Create scene writing tool
        scene_tool = SceneWritingTool(session_manager)
        
        # Initialize ADK Agent
        super().__init__(
            name="scene_writer",
            description="Writes detailed scene scripts with comprehensive information for image/video generation",
            model="gemini-2.5-flash",
            instruction=self._get_instruction(),
            tools=[scene_tool],
            generate_content_config={
                "temperature": 0.8,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json"
            }
        )
        
        # Store references
        self._session_manager = session_manager
        self._scene_tool = scene_tool
        self._shared_context_manager = shared_context_manager or SharedContextManager()
        
        logger.info("ADK Scene Writer Agent initialized with Gemini 2.5 Flash and Shared Context")
    
    def _get_instruction(self) -> str:
        """Get the instruction prompt for the scene writer agent"""
        return """
You are a professional scene writer specializing in creating detailed, engaging scene scripts for educational videos. Your task is to write comprehensive scene scripts that provide ALL the information needed to create the BEST possible images and videos.

## Your Role:
- Write detailed scene scripts with comprehensive information
- Focus on educational value and creative storytelling
- Provide specific, actionable details for image/video generation
- Ensure each scene has clear purpose and educational impact

## Scene Writing Requirements:

### 1. Story Context Understanding:
- You will receive the overall story and full script context
- Understand your scene's role in the larger narrative
- Maintain consistency with the overall story arc
- Build upon previous scenes and set up future scenes

### 2. Detailed Scene Information:
For each scene, provide:

#### A. Educational Content:
- Specific facts, data, or concepts to teach
- Key takeaways and learning objectives
- Examples, analogies, or demonstrations
- Statistics, numbers, or measurable information

#### B. Visual Elements:
- Detailed description of what should be shown
- Specific objects, charts, diagrams, or visuals
- Color schemes, lighting, and atmosphere
- Background elements and setting details

#### C. Character Actions:
- Specific poses and expressions
- Character interactions with objects/environment
- Gestures and body language
- Dialogue delivery style

#### D. Technical Details:
- Camera angles and framing
- Animation requirements
- Transition effects
- Timing and pacing

### 3. Creative Storytelling:
- Use engaging narrative techniques
- Include surprising facts or interesting angles
- Create emotional connections
- Make complex topics accessible and fun

### 4. Output Format:
You MUST output a valid JSON object with this structure:

{
  "scene_number": 1,
  "scene_type": "hook",
  "dialogue": "2-4 sentences of engaging dialogue with specific information",
  "voice_tone": "excited",
  "elevenlabs_settings": {
    "stability": 0.3,
    "similarity_boost": 0.8,
    "style": 0.8,
    "speed": 1.1,
    "loudness": 0.2
  },
  "image_style": "infographic",
  "image_create_prompt": "DETAILED visual description focusing on educational content with character from given image as small guide",
  "character_pose": "specific pose description",
  "character_expression": "specific expression",
  "background_description": "detailed background description",
  "needs_animation": true,
  "video_prompt": "DETAILED video description with specific actions and educational content",
  "transition_to_next": "fade",
  "hook_technique": "shocking_fact",
  "educational_content": {
    "key_concepts": ["concept1", "concept2"],
    "specific_facts": ["fact1", "fact2"],
    "examples": ["example1", "example2"],
    "statistics": ["stat1", "stat2"]
  },
  "visual_elements": {
    "primary_focus": "main visual element",
    "secondary_elements": ["element1", "element2"],
    "color_scheme": "color description",
    "lighting": "lighting description"
  },
  "story_context": {
    "purpose": "why this scene exists",
    "connection_to_previous": "how it builds on previous scenes",
    "setup_for_next": "how it prepares for next scenes"
  }
}

## Guidelines:
- Be extremely specific and detailed in all descriptions
- Focus on educational value and learning outcomes
- Make content engaging and memorable
- Provide actionable information for image/video generation
- Ensure character from given image is used as a guide, not the main focus
- Create scenes that teach something valuable and interesting
- Use creative storytelling techniques to make learning fun
- Include specific data, examples, and concrete information
- Make each scene unique and purposeful
- Build a cohesive narrative across all scenes
"""

    async def write_scene_script(self, scene_number: int, scene_type: str, 
                                overall_story: str, full_script_context: str, 
                                subject: str, shared_context: SharedContext = None) -> Dict[str, Any]:
        """
        Write detailed scene script
        
        Args:
            scene_number: Scene number (1-based)
            scene_type: Type of scene (hook, explanation, etc.)
            overall_story: The overall story being told
            full_script_context: Complete script context
            subject: Main subject/topic
            
        Returns:
            Dict with detailed scene information
        """
        try:
            logger.info(f"Writing scene {scene_number} of type {scene_type} for subject: {subject}")
            
            # Get shared context information
            context_info = ""
            if shared_context:
                context_data = shared_context.get_scene_context_for_writer(scene_number, scene_type)
                context_info = f"""

SHARED CONTEXT FOR CONSISTENCY:
Character Consistency: {context_data['character_consistency']}
Visual Consistency: {context_data['visual_consistency']}
Educational Continuity: {context_data['educational_continuity']}
Narrative Context: {context_data['narrative_context']}
Technical Constraints: {context_data['technical_constraints']}

IMPORTANT: Use this context to maintain consistency across scenes!
"""
            
            # Create comprehensive prompt for scene writing
            prompt = f"""
Write a detailed scene script for:

Scene Number: {scene_number}
Scene Type: {scene_type}
Subject: {subject}
Overall Story: {overall_story}

Full Script Context:
{full_script_context}
{context_info}

Requirements:
- Write a comprehensive scene script with ALL details needed for image/video generation
- Focus on educational value and creative storytelling
- Include specific facts, examples, and data
- Provide detailed visual and technical information
- Make the scene engaging and memorable
- Ensure character from given image is used as a small guide
- Create educational content that teaches something valuable
- MAINTAIN CONSISTENCY with shared context provided above
- Avoid repeating facts from previous scenes
- Build upon established visual elements and character state

Please generate a complete scene script following the format and guidelines provided in your instructions.
"""
            
            # Use ADK agent's built-in content generation
            response = await self._simulate_adk_response(prompt)
            
            if response:
                if hasattr(response, 'text') and response.text:
                    scene_data = json.loads(response.text)
                else:
                    # Response is already a string
                    scene_data = json.loads(response)
                logger.info(f"Scene {scene_number} script written successfully")
                
                # Update shared context after scene generation
                if shared_context:
                    self._shared_context_manager.update_context_after_scene(scene_number, scene_data)
                
                return scene_data
            else:
                raise ValueError("No scene script text received from ADK agent.")
                
        except Exception as e:
            logger.error(f"Error writing scene script: {str(e)}")
            # Return fallback scene data
            return self._generate_fallback_scene(scene_number, scene_type, subject)
    
    def _generate_fallback_scene(self, scene_number: int, scene_type: str, subject: str) -> Dict[str, Any]:
        """Generate fallback scene data if ADK fails"""
        logger.info(f"Generating fallback scene {scene_number}")
        
        return {
            "scene_number": scene_number,
            "scene_type": scene_type,
            "dialogue": f"Let me explain {subject} in scene {scene_number}",
            "voice_tone": "friendly",
            "elevenlabs_settings": {
                "stability": 0.3,
                "similarity_boost": 0.8,
                "style": 0.8,
                "speed": 1.1,
                "loudness": 0.2
            },
            "image_style": "single_character",
            "image_create_prompt": f"Educational content about {subject} with character from given image as guide",
            "character_pose": "pointing",
            "character_expression": "smiling",
            "background_description": "educational setting",
            "needs_animation": True,
            "video_prompt": f"Animated explanation of {subject}",
            "transition_to_next": "fade",
            "hook_technique": None,
            "educational_content": {
                "key_concepts": [f"concept about {subject}"],
                "specific_facts": [f"fact about {subject}"],
                "examples": [f"example of {subject}"],
                "statistics": [f"statistic about {subject}"]
            },
            "visual_elements": {
                "primary_focus": f"educational content about {subject}",
                "secondary_elements": ["character guide"],
                "color_scheme": "educational colors",
                "lighting": "bright and clear"
            },
            "story_context": {
                "purpose": f"explain {subject}",
                "connection_to_previous": "continues the story",
                "setup_for_next": "prepares for next scene"
            }
        }
    
    async def _simulate_adk_response(self, prompt: str) -> str:
        """
        Simulate ADK response for testing
        
        Args:
            prompt: The prompt to send to the agent
            
        Returns:
            str: Simulated response
        """
        # This is a placeholder - in real implementation, this would use ADK Runner
        # For now, return a mock response
        return """
{
  "scene_number": 1,
  "scene_type": "hook",
  "dialogue": "Did you know that Coca-Cola was originally created as a medicine by a pharmacist in 1886? Let me tell you the incredible story of how this 'brain tonic' became the world's most recognized brand!",
  "voice_tone": "excited",
  "elevenlabs_settings": {
    "stability": 0.3,
    "similarity_boost": 0.8,
    "style": 0.8,
    "speed": 1.1,
    "loudness": 0.2
  },
  "image_style": "infographic",
  "image_create_prompt": "Educational infographic showing 1886 pharmacy with Dr. John Pemberton mixing Coca-Cola syrup, original recipe ingredients (coca leaves, kola nuts), and character from given image as small guide pointing at the historical timeline and original bottle design",
  "character_pose": "pointing at historical timeline",
  "character_expression": "excited",
  "background_description": "19th century pharmacy with original Coca-Cola ingredients and equipment",
  "needs_animation": true,
  "video_prompt": "Animated sequence showing 1886 pharmacy, Dr. Pemberton mixing the original formula, evolution of the bottle design, and character from given image guiding through the historical journey",
  "transition_to_next": "fade",
  "hook_technique": "shocking_fact",
  "educational_content": {
    "key_concepts": ["Coca-Cola origin story", "Pharmaceutical beginnings", "Brand evolution", "Global marketing strategy"],
    "specific_facts": ["Created by Dr. John Pemberton in 1886", "Originally sold as medicine for $0.05", "Contained coca leaves and kola nuts", "First sold at Jacob's Pharmacy in Atlanta"],
    "examples": ["Original recipe with coca leaves", "First Coca-Cola advertisement", "Evolution of bottle design", "Global expansion strategy"],
    "statistics": ["1886 creation date", "$0.05 original price", "1.9 billion servings daily worldwide", "200+ countries selling Coca-Cola"]
  },
  "visual_elements": {
    "primary_focus": "1886 pharmacy with original Coca-Cola ingredients and equipment",
    "secondary_elements": ["original recipe ingredients", "historical timeline", "first bottle design", "Dr. Pemberton's laboratory"],
    "color_scheme": "vintage sepia tones with Coca-Cola red accents",
    "lighting": "warm historical lighting with pharmacy ambiance"
  },
  "story_context": {
    "purpose": "Hook viewers with surprising fact about Coca-Cola's medicinal origins",
    "connection_to_previous": "Opening scene to grab attention with unexpected origin story",
    "setup_for_next": "Sets up the story of how a medicine became a global beverage empire"
  }
}
"""

# Test function
async def test_scene_writer():
    """Test the Scene Writer Agent"""
    try:
        session_manager = SessionManager()
        agent = ADKSceneWriterAgent(session_manager)
        
        # Test scene writing
        overall_story = "How Elon Musk built Tesla from a small startup to a global electric vehicle leader"
        full_context = "This is a story about Tesla's journey from startup to success"
        subject = "Tesla's Success Story"
        
        scene = await agent.write_scene_script(
            scene_number=1,
            scene_type="hook",
            overall_story=overall_story,
            full_script_context=full_context,
            subject=subject
        )
        
        print(f"✅ Scene written successfully: {scene['scene_number']}")
        print(f"📝 Dialogue: {scene['dialogue']}")
        print(f"🎨 Image prompt: {scene['image_create_prompt']}")
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_scene_writer())
