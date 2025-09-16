"""
ADK-based Script Writer Agent
Uses Google Agent Development Kit for script generation
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.models import BaseLlm
from model.models import SceneType, ImageStyle, VoiceTone, TransitionType, HookTechnique, VideoScript, Scene, ElevenLabsSettings

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ADKScriptWriterAgent(Agent):
    """
    ADK-based Script Writer Agent
    
    This agent generates video scripts using Google ADK with Gemini 2.5
    """
    
    def __init__(self):
        """
        Initialize ADK Script Writer Agent
        
        Note: ADK handles API key management automatically
        """
        # Check if API key is available
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        # Initialize ADK Agent
        super().__init__(
            name="script_writer",
            description="Generates video scripts using Gemini 2.5 with Huh character",
            model="gemini-2.5-flash",
            instruction=self._get_instruction(),
            generate_content_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json"
            }
        )
        
        logger.info("ADK Script Writer Agent initialized with Gemini 2.5 Flash")
    
    def _get_instruction(self) -> str:
        """
        Get the instruction prompt for the agent
        
        Returns:
            str: The instruction prompt
        """
        return """
You are a professional video script writer specializing in creating engaging, educational short videos. Your task is to generate a complete video script with detailed scene breakdowns.

## Character Requirements:
- Use ONLY the character "Huh" - a cute, blob-like cartoon character
- Huh is the main character who appears in all scenes
- Include character_cosplay_instructions: Describe how Huh should be cosplayed/dressed for this topic (e.g., "dress Huh as a scientist with lab coat", "dress Huh as a programmer with glasses", etc.)
- Include character_expression for each scene: Describe Huh's emotional expression (e.g., "smiling", "winking", "excited", "surprised", "confident")
- Huh should be relatable and engaging
- Add speech bubbles or text boxes with dialogue for Huh in each scene

## Available Options:

### Scene Types:
- "hook": Opening scene to grab attention
- "explanation": Educational content scene
- "visual_demo": Visual demonstration scene
- "comparison": Comparison explanation scene
- "story_telling": Story-telling scene
- "conclusion": Closing/summary scene

### Image Styles:
- "single_character": Huh alone in the scene
- "character_with_background": Huh with educational background
- "infographic": Information display with Huh
- "diagram_explanation": Diagram with Huh explaining
- "before_after_comparison": Comparison with Huh
- "step_by_step_visual": Step-by-step with Huh
- "four_cut_cartoon": Comic-style with Huh
- "comic_panel": Comic panel with Huh
- "speech_bubble": Huh with speech bubbles
- "cinematic": Cinematic style with Huh
- "close_up_reaction": Close-up of Huh's reaction
- "wide_establishing_shot": Wide shot with Huh

### Voice Tones:
- "excited": Energetic and enthusiastic
- "curious": Questioning and inquisitive
- "serious": Professional and authoritative
- "friendly": Warm and approachable
- "sad": Emotional and empathetic
- "mysterious": Intriguing and suspenseful
- "surprised": Shocked and amazed
- "confident": Assured and knowledgeable

### Transition Types:
- "fade": Smooth fade transition
- "cut": Quick cut transition
- "slide": Slide transition
- "zoom": Zoom transition
- "dissolve": Dissolve transition

### Hook Techniques:
- "shocking_fact": Start with surprising information
- "question": Begin with a thought-provoking question
- "story": Start with a relatable story
- "statistic": Begin with an impressive statistic
- "controversy": Start with a controversial statement

### Image Create Prompts:
- Be very specific about visual elements
- Reference "Huh" (our fixed character) for consistency
- Describe setting, lighting, atmosphere in detail
- Include art style, mood, color palette
- Specify camera angle, framing, focal point
- IMPORTANT: Include character_pose, character_expression, and background_description fields
- Huh should be SMALL in the image (not dominating the frame)
- Focus on what Huh is DOING in the scene
- Make images meaningful and educational, not just decorative
- Add speech bubbles or text boxes with dialogue for Huh
- Keep Huh's original image style - don't change Huh's appearance
- Images will be in vertical ratio (9:16 format for mobile/social media) or horizontal ratio (16:9 format for desktop/widescreen)

### Output Format:
You MUST output a valid JSON object that matches this exact structure:

{
  "title": "Compelling title for the video",
  "main_character_description": "Huh - a cute, blob-like cartoon character",
  "character_cosplay_instructions": "Instructions for how to cosplay the main character (e.g., 'cosplay like Elon Musk', 'dress as a K-pop idol')",
  "overall_style": "educational",
  "scenes": [
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
      "image_style": "single_character",
      "image_create_prompt": "Very detailed description of the image including character, background, lighting, composition, and style. Include speech bubble with dialogue text",
      "character_pose": "What Huh is doing: 'pointing at screen', 'looking at camera', 'gesturing'",
      "character_expression": "Huh's emotional expression: 'smiling', 'winking', 'excited', 'surprised', 'confident'",
      "background_description": "Educational background: 'classroom', 'office', 'lab', 'outdoor setting'",
      "needs_animation": true,
      "video_prompt": "Detailed description of animation if needed",
      "transition_to_next": "fade",
      "hook_technique": "shocking_fact"
    }
    // ... more scenes ...
  ]
}

## Guidelines:
- **CRITICAL: Create exactly 6-8 scenes for a complete video**
- Each scene should be 8 seconds long (dialogue length should match)
- Make dialogue engaging and educational
- Use Huh character consistently throughout
- Include diverse scene types and transitions
- Ensure smooth flow between scenes
- Make content accessible and entertaining
- Focus on educational value while keeping it fun
- Use Huh's personality to make complex topics relatable
- **MUST include multiple scenes: hook, explanation, example, statistic, call_to_action, summary**
"""

    async def generate_script(self, subject: str, language: str = "English", max_video_scenes: int = 8) -> VideoScript:
        """
        Generate a video script using ADK Agent
        
        Args:
            subject: The topic for the video
            language: Language for the script (default: English)
            max_video_scenes: Maximum number of scenes (default: 8)
            
        Returns:
            VideoScript: Generated script object
        """
        try:
            logger.info(f"Generating script for subject: {subject}")
            
            # Create the prompt for the agent
            prompt = f"""
Create a video script about: {subject}

Language: {language}
REQUIRED: Create exactly {max_video_scenes} scenes for this video
Scene types to include: hook, explanation, example, statistic, call_to_action, summary

IMPORTANT: You MUST create multiple scenes (6-8 scenes minimum). Do not create just 1 scene.
Each scene must be detailed and educational with different scene types.

Please generate a complete video script following the format and guidelines provided in your instructions.
"""
            
            # Use ADK agent's built-in content generation
            # ADK LlmAgent handles the API calls internally
            response = await self.generate_content(prompt)
            
            if response and hasattr(response, 'text') and response.text:
                script_data = json.loads(response.text)
                script = VideoScript(**script_data)
            else:
                raise ValueError("No script text received from ADK agent.")
            
            logger.info(f"Script generated successfully with {len(script.scenes)} scenes")
            return script
            
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            # Return mock data as fallback
            return self._generate_mock_script(subject)
    
    async def _simulate_adk_response(self, prompt: str) -> str:
        """
        Simulate ADK response (placeholder for actual ADK integration)
        
        Args:
            prompt: The prompt to send to the agent
            
        Returns:
            str: Simulated response
        """
        # This is a placeholder - in real implementation, this would use ADK Runner
        # For now, return a mock response
        return """
{
  "title": "Understanding K-pop: A Global Phenomenon",
  "main_character_description": "Huh - a cute, blob-like cartoon character",
  "character_cosplay_instructions": "Dress Huh as a charismatic K-pop idol with a trendy, colorful stage outfit, sparkling accessories, and stylish hair",
  "overall_style": "educational",
  "scenes": [
    {
      "scene_number": 1,
      "scene_type": "hook",
      "dialogue": "Did you know that K-pop generates over $5 billion annually? Let me show you what makes this Korean music phenomenon so powerful!",
      "voice_tone": "excited",
      "elevenlabs_settings": {
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      },
      "image_style": "single_character",
      "image_create_prompt": "Huh dressed as a K-pop idol with sparkling outfit, pointing at a chart showing $5 billion, with speech bubble containing the dialogue",
      "character_pose": "pointing at screen",
      "character_expression": "excited",
      "background_description": "stage with charts and statistics",
      "needs_animation": true,
      "video_prompt": "Huh pointing at animated chart with growing numbers",
      "transition_to_next": "fade",
      "hook_technique": "shocking_fact"
    },
    {
      "scene_number": 2,
      "scene_type": "explanation",
      "dialogue": "K-pop stands for Korean pop music, but it's so much more than just music! It's a complete entertainment package with synchronized dancing, stunning visuals, and captivating storytelling.",
      "voice_tone": "informative",
      "elevenlabs_settings": {
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      },
      "image_style": "infographic",
      "image_create_prompt": "Huh dressed as a K-pop idol explaining with an infographic showing music, dance, visuals, and storytelling elements, with speech bubble",
      "character_pose": "gesturing towards infographic",
      "character_expression": "confident",
      "background_description": "modern studio with infographic displays",
      "needs_animation": false,
      "video_prompt": null,
      "transition_to_next": "cut"
    },
    {
      "scene_number": 3,
      "scene_type": "example",
      "dialogue": "Take BTS for example - they didn't just sing songs, they created a global movement! Their music videos tell stories, their performances are like mini-concerts, and they connect with fans worldwide.",
      "voice_tone": "enthusiastic",
      "elevenlabs_settings": {
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      },
      "image_style": "character_with_background",
      "image_create_prompt": "Huh dressed as a K-pop idol standing in front of a concert stage with BTS-style visuals, pointing at the stage, with speech bubble",
      "character_pose": "pointing at stage",
      "character_expression": "amazed",
      "background_description": "concert stage with lights and visuals",
      "needs_animation": true,
      "video_prompt": "Huh pointing at animated stage with lights and effects",
      "transition_to_next": "slide"
    },
    {
      "scene_number": 4,
      "scene_type": "statistic",
      "dialogue": "The numbers are incredible! K-pop has over 100 million fans worldwide, with groups like BLACKPINK reaching 1 billion views on YouTube. It's not just music - it's a cultural phenomenon!",
      "voice_tone": "impressed",
      "elevenlabs_settings": {
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      },
      "image_style": "infographic",
      "image_create_prompt": "Huh dressed as a K-pop idol next to a large infographic showing 100 million fans and 1 billion views statistics, with speech bubble",
      "character_pose": "gesturing at statistics",
      "character_expression": "surprised",
      "background_description": "data visualization studio with charts",
      "needs_animation": false,
      "video_prompt": null,
      "transition_to_next": "dissolve"
    },
    {
      "scene_number": 5,
      "scene_type": "call_to_action",
      "dialogue": "Want to dive deeper into K-pop? Check out the amazing choreography, explore different groups, and discover why this Korean wave has taken the world by storm!",
      "voice_tone": "encouraging",
      "elevenlabs_settings": {
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      },
      "image_style": "single_character",
      "image_create_prompt": "Huh dressed as a K-pop idol with arms spread wide, inviting gesture, with speech bubble and call-to-action text",
      "character_pose": "arms spread wide",
      "character_expression": "inviting",
      "background_description": "colorful stage with K-pop elements",
      "needs_animation": true,
      "video_prompt": "Huh with inviting gesture and animated background",
      "transition_to_next": "fade"
    },
    {
      "scene_number": 6,
      "scene_type": "summary",
      "dialogue": "So there you have it! K-pop is more than just music - it's a complete entertainment experience that combines music, dance, visuals, and storytelling to create something truly special. Thanks for watching!",
      "voice_tone": "friendly",
      "elevenlabs_settings": {
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      },
      "image_style": "single_character",
      "image_create_prompt": "Huh dressed as a K-pop idol waving goodbye with a warm smile, with speech bubble and thank you message",
      "character_pose": "waving goodbye",
      "character_expression": "smiling",
      "background_description": "warm, friendly setting",
      "needs_animation": false,
      "video_prompt": null,
      "transition_to_next": "fade"
    }
  ]
}
"""
    
    def _parse_response(self, response_text: str, subject: str) -> VideoScript:
        """
        Parse the ADK response into VideoScript object
        
        Args:
            response_text: Raw response from ADK agent
            subject: Original subject for fallback
            
        Returns:
            VideoScript: Parsed script object
        """
        try:
            # Clean the response text
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Parse JSON
            script_data = json.loads(response_text)
            
            # Convert to VideoScript object
            script = VideoScript.model_validate(script_data)
            
            return script
            
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            logger.info("Using mock script as fallback")
            return self._generate_mock_script(subject)
    
    def _generate_mock_script(self, subject: str) -> VideoScript:
        """
        Generate mock script as fallback
        
        Args:
            subject: The subject for the mock script
            
        Returns:
            VideoScript: Mock script object
        """
        return VideoScript(
            title=f"Understanding {subject}",
            main_character_description="Huh - a cute, blob-like cartoon character",
            character_cosplay_instructions=f"Dress Huh as an expert on {subject}",
            overall_style="educational",
            scenes=[
                Scene(
                    scene_number=1,
                    scene_type=SceneType.HOOK,
                    dialogue=f"Let me explain {subject} in a fun and engaging way!",
                    voice_tone=VoiceTone.EXCITED,
                    elevenlabs_settings=ElevenLabsSettings(
                        stability=0.3,
                        similarity_boost=0.8,
                        style=0.8,
                        speed=1.1,
                        loudness=0.2
                    ),
                    image_style=ImageStyle.SINGLE_CHARACTER,
                    image_create_prompt=f"Huh explaining {subject} with enthusiasm",
                    character_pose="pointing",
                    character_expression="smiling",
                    background_description="educational setting",
                    needs_animation=True,
                    video_prompt=f"Animated explanation of {subject}",
                    transition_to_next=TransitionType.FADE,
                    hook_technique=None
                ),
                Scene(
                    scene_number=2,
                    scene_type=SceneType.EXPLANATION,
                    dialogue=f"Here's what you need to know about {subject}. It's fascinating and important to understand!",
                    voice_tone=VoiceTone.INFORMATIVE,
                    elevenlabs_settings=ElevenLabsSettings(
                        stability=0.3,
                        similarity_boost=0.8,
                        style=0.8,
                        speed=1.1,
                        loudness=0.2
                    ),
                    image_style=ImageStyle.INFOGRAPHIC,
                    image_create_prompt=f"Huh with infographic explaining {subject}",
                    character_pose="gesturing at info",
                    character_expression="confident",
                    background_description="modern studio with displays",
                    needs_animation=False,
                    video_prompt=None,
                    transition_to_next=TransitionType.CUT
                ),
                Scene(
                    scene_number=3,
                    scene_type=SceneType.EXAMPLE,
                    dialogue=f"Let me give you a great example of {subject} in action!",
                    voice_tone=VoiceTone.ENTHUSIASTIC,
                    elevenlabs_settings=ElevenLabsSettings(
                        stability=0.3,
                        similarity_boost=0.8,
                        style=0.8,
                        speed=1.1,
                        loudness=0.2
                    ),
                    image_style=ImageStyle.CHARACTER_WITH_BACKGROUND,
                    image_create_prompt=f"Huh demonstrating {subject} with example",
                    character_pose="demonstrating",
                    character_expression="excited",
                    background_description="example setting",
                    needs_animation=True,
                    video_prompt=f"Animated example of {subject}",
                    transition_to_next=TransitionType.SLIDE
                ),
                Scene(
                    scene_number=4,
                    scene_type=SceneType.STATISTIC,
                    dialogue=f"The numbers behind {subject} are really impressive!",
                    voice_tone=VoiceTone.IMPRESSED,
                    elevenlabs_settings=ElevenLabsSettings(
                        stability=0.3,
                        similarity_boost=0.8,
                        style=0.8,
                        speed=1.1,
                        loudness=0.2
                    ),
                    image_style=ImageStyle.INFOGRAPHIC,
                    image_create_prompt=f"Huh with statistics about {subject}",
                    character_pose="pointing at stats",
                    character_expression="surprised",
                    background_description="data visualization",
                    needs_animation=False,
                    video_prompt=None,
                    transition_to_next=TransitionType.DISSOLVE
                ),
                Scene(
                    scene_number=5,
                    scene_type=SceneType.CALL_TO_ACTION,
                    dialogue=f"Want to learn more about {subject}? There's so much more to explore!",
                    voice_tone=VoiceTone.ENCOURAGING,
                    elevenlabs_settings=ElevenLabsSettings(
                        stability=0.3,
                        similarity_boost=0.8,
                        style=0.8,
                        speed=1.1,
                        loudness=0.2
                    ),
                    image_style=ImageStyle.SINGLE_CHARACTER,
                    image_create_prompt=f"Huh inviting viewers to learn more about {subject}",
                    character_pose="inviting gesture",
                    character_expression="encouraging",
                    background_description="inviting setting",
                    needs_animation=True,
                    video_prompt=f"Inviting animation for {subject}",
                    transition_to_next=TransitionType.FADE
                ),
                Scene(
                    scene_number=6,
                    scene_type=SceneType.SUMMARY,
                    dialogue=f"So there you have it! {subject} is truly fascinating. Thanks for watching!",
                    voice_tone=VoiceTone.FRIENDLY,
                    elevenlabs_settings=ElevenLabsSettings(
                        stability=0.3,
                        similarity_boost=0.8,
                        style=0.8,
                        speed=1.1,
                        loudness=0.2
                    ),
                    image_style=ImageStyle.SINGLE_CHARACTER,
                    image_create_prompt=f"Huh waving goodbye after explaining {subject}",
                    character_pose="waving goodbye",
                    character_expression="friendly",
                    background_description="warm setting",
                    needs_animation=False,
                    video_prompt=None,
                    transition_to_next=TransitionType.FADE
                )
            ]
        )

# Test function
async def test_adk_script_writer():
    """Test the ADK Script Writer Agent"""
    try:
        agent = ADKScriptWriterAgent()
        script = await agent.generate_script("What is K-pop?", "English", 3)
        print(f"✅ ADK Script generated successfully!")
        print(f"✅ Title: {script.title}")
        print(f"✅ Scenes: {len(script.scenes)}")
        print(f"✅ Character: {script.main_character_description}")
        return True
    except Exception as e:
        print(f"❌ ADK Script generation error: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_adk_script_writer())
