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
from model.models import SceneType, ImageStyle, VoiceTone, TransitionType, HookTechnique, VideoScript, StoryScript, Scene, ScenePlan, ElevenLabsSettings
from core.shared_context import SharedContextManager, SharedContext, VisualStyle
from core.story_validator import StoryValidator, StoryValidationResult
from core.story_focus_engine import StoryFocusEngine, StoryFocusResult

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
    
    def __init__(self, shared_context_manager: SharedContextManager = None):
        """
        Initialize ADK Script Writer Agent
        
        Args:
            shared_context_manager: SharedContextManager for maintaining consistency
        
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
        
        # Store shared context manager, story validator, and story focus engine
        self._shared_context_manager = shared_context_manager or SharedContextManager()
        self._story_validator = StoryValidator()
        self._story_focus_engine = StoryFocusEngine()
        
        logger.info("ADK Script Writer Agent initialized with Gemini 2.5 Flash, Shared Context, Story Validator, and Story Focus Engine")
    
    def _get_instruction(self) -> str:
        """
        Get the instruction prompt for the agent
        
        Returns:
            str: The instruction prompt
        """
        return """
You are a professional video script writer specializing in creating engaging, educational short videos. Your primary role is to:

1. **Story Development**: Take a broad subject and develop a specific, focused story
2. **Scene Planning**: Divide the story into logical scenes for video production
3. **Overall Coordination**: Provide context for scene writers to create detailed scripts

## Story Development Process:

### Step 1: Subject Analysis
- Take the given subject and analyze it deeply
- Identify the most interesting, educational, or surprising angle
- Find a specific story or narrative within the broader topic

### Step 2: Story Scoping
- Narrow down to a focused, specific story
- Choose a particular aspect, event, or perspective
- Make it concrete and relatable

### Examples:
- Subject: "Elon Musk" → Story: "How Elon Musk bought a house in Austin and moved Tesla headquarters there"
- Subject: "Machine Learning" → Story: "How Netflix uses machine learning to recommend movies you'll love"
- Subject: "K-pop" → Story: "How BTS broke into the American market and changed K-pop forever"
- Subject: "Climate Change" → Story: "How a small island nation is fighting rising sea levels with innovative solutions"

### Step 3: Scene Division
- Divide the story into 6-8 logical scenes
- Each scene should have a clear purpose and educational value
- Ensure smooth flow and narrative progression

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
- PRIMARY FOCUS: Educational content and information delivery
- SECONDARY FOCUS: Character from given image (not "Huh" - use "character from given image")
- Create detailed, informative visual content that teaches the topic
- Include specific educational elements: charts, diagrams, examples, statistics
- Describe setting, lighting, atmosphere in detail
- Include art style, mood, color palette
- Specify camera angle, framing, focal point
- IMPORTANT: Include character_pose, character_expression, and background_description fields
- Character should be SMALL in the image (not dominating the frame)
- Focus on EDUCATIONAL CONTENT - what information are we teaching?
- Make images 100% informative and educational
- Character is just a guide/helper, not the main focus
- Add speech bubbles or text boxes with dialogue for character
- Keep character's original image style - don't change character's appearance
- Images will be in vertical ratio (9:16 format for mobile/social media) or horizontal ratio (16:9 format for desktop/widescreen)
- Each image should have a clear educational purpose and message

### Output Format:
You MUST output a valid JSON object that matches this exact structure:

{
  "title": "Compelling title for the video",
  "main_character_description": "Huh - a cute, blob-like cartoon character",
  "character_cosplay_instructions": "Instructions for how to cosplay the main character (e.g., 'cosplay like Elon Musk', 'dress as a K-pop idol')",
  "overall_style": "educational",
  "overall_story": "The specific, focused story you developed from the subject",
  "story_summary": "Brief summary of the overall narrative and key points",
  "scene_plan": [
    {
      "scene_number": 1,
      "scene_type": "hook",
      "scene_purpose": "What this scene aims to achieve",
      "key_content": "Main educational content for this scene",
      "scene_focus": "Specific aspect or angle this scene covers"
    }
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

    async def generate_story_script(self, subject: str, language: str = "English", max_video_scenes: int = 8, 
                                   target_audience: str = "general", visual_style: VisualStyle = VisualStyle.MODERN) -> StoryScript:
        """
        Generate a story script using ADK Agent
        
        Args:
            subject: The topic for the video
            language: Language for the script (default: English)
            max_video_scenes: Maximum number of scenes (default: 8)
            
        Returns:
            StoryScript: Generated story script with scene plan
        """
        try:
            logger.info(f"Generating script for subject: {subject}")
            
            # First, refine the story focus using the Story Focus Engine
            initial_story = f"The story of {subject} and how it works"
            focus_result = self._story_focus_engine.refine_story_focus(
                broad_subject=subject,
                initial_story=initial_story,
                target_audience=target_audience
            )
            
            logger.info(f"Story focus refined: {focus_result.applied_pattern.value} pattern applied")
            logger.info(f"Focus score: {focus_result.focus_score:.2f}")
            
            # Create the prompt for the agent with focused story
            prompt = f"""
Create a story script about: {subject}

Language: {language}
REQUIRED: Create exactly {max_video_scenes} scenes for this video

FOCUSED STORY ANGLE:
{focus_result.focused_story}

IMPORTANT STORY DEVELOPMENT PROCESS:
1. Use the focused story angle above as your foundation
2. Develop this specific, engaging narrative
3. Choose scenes that support this focused story
4. Make it concrete and relatable
5. Divide into {max_video_scenes} logical scenes

STORY FOCUS REQUIREMENTS:
- Follow the focused story angle: "{focus_result.focused_story}"
- Keep the story specific and engaging (not broad overview)
- Choose scenes that build the focused narrative
- Ensure each scene supports the main story angle
- Make sure the story can be told through visual scenes

STORY VALIDATION REQUIREMENTS:
- Keep the story focused and achievable in {max_video_scenes} scenes
- Avoid overly complex topics that require extensive background
- Choose stories with clear beginning, middle, and end
- Ensure the story has educational value and entertainment factor
- Make sure the story can be told through visual scenes

Please generate a complete story script following the format and guidelines provided in your instructions.
"""
            
            # Use ADK agent's built-in content generation
            # ADK LlmAgent handles the API calls internally
            response = await self._simulate_adk_response(prompt)
            
            if response:
                if hasattr(response, 'text') and response.text:
                    script_data = json.loads(response.text)
                else:
                    # Response is already a string
                    script_data = json.loads(response)
                story_script = StoryScript(**script_data)
            else:
                raise ValueError("No story script text received from ADK agent.")
            
            logger.info(f"Story script generated successfully with {len(story_script.scene_plan)} scenes")
            
            # Update the story script with the focused story
            story_script.overall_story = focus_result.focused_story
            
            # Validate the generated story
            validation_result = self._story_validator.validate_story(
                subject=subject,
                story=story_script.overall_story,
                target_audience=target_audience
            )
            
            logger.info(f"Story validation: {validation_result.feasibility.value} feasibility, {validation_result.complexity_level.value} complexity")
            
            # If story is not feasible, try to regenerate with suggestions
            if not validation_result.is_valid:
                logger.warning(f"Story validation failed: {validation_result.validation_notes}")
                # For now, we'll continue with the story but log the issues
                # In a full implementation, we could regenerate with simplified prompts
            
            # Log focus engine results
            logger.info(f"Story focus engine results:")
            logger.info(f"  - Applied pattern: {focus_result.applied_pattern.value}")
            logger.info(f"  - Focus score: {focus_result.focus_score:.2f}")
            logger.info(f"  - Specificity improvement: +{focus_result.specificity_improvement:.2f}")
            logger.info(f"  - Engagement improvement: +{focus_result.engagement_improvement:.2f}")
            
            # Create shared context for the story
            shared_context = self._shared_context_manager.create_context(
                character_emotion="excited",
                character_pose="pointing",
                visual_style=visual_style,
                target_audience=target_audience,
                video_duration=60,
                scene_count=max_video_scenes
            )
            
            # Store shared context for use by scene writers
            self._shared_context_manager.context = shared_context
            
            return story_script
            
        except Exception as e:
            logger.error(f"Error generating story script: {str(e)}")
            # Return mock data as fallback
            return self._generate_mock_story_script(subject)
    
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
  "title": "The Secret Story of Coca-Cola: From Medicine to Global Empire",
  "main_character_description": "Huh - a cute, blob-like cartoon character",
  "character_cosplay_instructions": "Dress Huh as a 19th century pharmacist with a white lab coat, vintage glasses, and a Coca-Cola bottle",
  "overall_style": "educational",
  "overall_story": "How Coca-Cola evolved from a medicinal 'brain tonic' created by a pharmacist in 1886 to become the world's most recognized brand and global beverage empire",
  "story_summary": "The fascinating journey of Coca-Cola from its humble beginnings as a medicine in an Atlanta pharmacy to becoming a global phenomenon that sells 1.9 billion servings daily worldwide",
  "scene_plan": [
    {
      "scene_number": 1,
      "scene_type": "hook",
      "scene_purpose": "Grab attention with surprising origin story",
      "key_content": "Coca-Cola was originally created as medicine by Dr. John Pemberton in 1886",
      "scene_focus": "Pharmaceutical beginnings and original recipe"
    },
    {
      "scene_number": 2,
      "scene_type": "explanation",
      "scene_purpose": "Explain the original formula and ingredients",
      "key_content": "Original recipe contained coca leaves, kola nuts, and was sold as a 'brain tonic'",
      "scene_focus": "Historical ingredients and medicinal claims"
    },
    {
      "scene_number": 3,
      "scene_type": "example",
      "scene_purpose": "Show the evolution from medicine to beverage",
      "key_content": "How Asa Candler transformed it from medicine to popular soft drink",
      "scene_focus": "Business transformation and marketing strategy"
    },
    {
      "scene_number": 4,
      "scene_type": "statistic",
      "scene_purpose": "Share impressive global reach statistics",
      "key_content": "1.9 billion servings daily, sold in 200+ countries, $43 billion annual revenue",
      "scene_focus": "Global impact and market dominance"
    },
    {
      "scene_number": 5,
      "scene_type": "call_to_action",
      "scene_purpose": "Encourage learning about business and marketing",
      "key_content": "Explore how brands can achieve global recognition and cultural impact",
      "scene_focus": "Lessons in branding and global expansion"
    },
    {
      "scene_number": 6,
      "scene_type": "summary",
      "scene_purpose": "Summarize the incredible transformation",
      "key_content": "From $0.05 medicine to world's most valuable brand",
      "scene_focus": "Key takeaways about innovation and business success"
    }
  ]
}
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
      "image_create_prompt": "Educational infographic showing K-pop industry statistics: $5 billion global market value, major companies (HYBE, SM, JYP, YG), with character from given image as small guide pointing at the data",
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
      "image_create_prompt": "Detailed educational diagram showing K-pop core elements: synchronized choreography, vocal harmonies, visual storytelling, fashion trends, with character from given image as small guide explaining each element",
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
      "image_create_prompt": "Educational visual showing K-pop concert production: stage design, lighting effects, fan engagement, choreography coordination, with character from given image as small guide demonstrating the process",
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
      "image_create_prompt": "Comprehensive data visualization showing K-pop global impact: 100+ million fans worldwide, 1+ billion YouTube views, cultural influence metrics, with character from given image as small guide highlighting key statistics",
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
      "image_create_prompt": "Educational summary infographic showing K-pop learning resources: recommended groups, music platforms, cultural aspects to explore, with character from given image as small guide encouraging further learning",
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
      "image_create_prompt": "Final educational summary showing key K-pop takeaways: global phenomenon, cultural impact, entertainment industry innovation, with character from given image as small guide waving goodbye with warm smile",
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
    
    def _generate_mock_story_script(self, subject: str) -> StoryScript:
        """Generate mock story script for fallback"""
        logger.info("Generating mock story script")
        
        return StoryScript(
            title=f"Understanding {subject}",
            main_character_description="Huh - a cute, blob-like cartoon character",
            character_cosplay_instructions=f"Dress Huh as an expert on {subject}",
            overall_style="educational",
            overall_story=f"The fascinating story of {subject} and its impact on the world",
            story_summary=f"A comprehensive exploration of {subject}, covering its origins, development, and significance",
            scene_plan=[
                ScenePlan(
                    scene_number=1,
                    scene_type=SceneType.HOOK,
                    scene_purpose="Grab attention and introduce the topic",
                    key_content=f"Introduction to {subject}",
                    scene_focus="Opening hook with surprising fact"
                ),
                ScenePlan(
                    scene_number=2,
                    scene_type=SceneType.EXPLANATION,
                    scene_purpose="Explain the core concepts",
                    key_content=f"Core concepts of {subject}",
                    scene_focus="Educational explanation"
                ),
                ScenePlan(
                    scene_number=3,
                    scene_type=SceneType.EXAMPLE,
                    scene_purpose="Provide concrete examples",
                    key_content=f"Real-world examples of {subject}",
                    scene_focus="Practical applications"
                ),
                ScenePlan(
                    scene_number=4,
                    scene_type=SceneType.STATISTIC,
                    scene_purpose="Share impressive statistics",
                    key_content=f"Statistics about {subject}",
                    scene_focus="Data and numbers"
                ),
                ScenePlan(
                    scene_number=5,
                    scene_type=SceneType.CALL_TO_ACTION,
                    scene_purpose="Encourage further learning",
                    key_content=f"Next steps for learning about {subject}",
                    scene_focus="Call to action"
                ),
                ScenePlan(
                    scene_number=6,
                    scene_type=SceneType.SUMMARY,
                    scene_purpose="Summarize key points",
                    key_content=f"Summary of {subject}",
                    scene_focus="Final takeaways"
                )
            ]
        )

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
                    image_create_prompt=f"Educational introduction infographic showing key concepts about {subject}, with character from given image as small guide explaining with enthusiasm",
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
                    image_create_prompt=f"Detailed educational infographic breaking down {subject} into key components and concepts, with character from given image as small guide pointing at information",
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
                    image_create_prompt=f"Educational visual demonstration showing practical examples of {subject} in action, with character from given image as small guide demonstrating the process",
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
                    image_create_prompt=f"Comprehensive data visualization showing important statistics and metrics about {subject}, with character from given image as small guide highlighting key numbers",
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
                    image_create_prompt=f"Educational resource guide showing learning paths and next steps for {subject}, with character from given image as small guide encouraging further exploration",
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
                    image_create_prompt=f"Final educational summary showing key takeaways and main points about {subject}, with character from given image as small guide waving goodbye with warm smile",
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
