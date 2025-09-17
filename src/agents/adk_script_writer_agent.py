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
            model="gemini-1.5-pro",
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
You are an expert educational content strategist who creates SPECIFIC, FACT-DENSE, ENGAGING video scripts.

## CRITICAL REQUIREMENTS:

### 1. ULTRA-SPECIFIC STORY SELECTION
Never create broad overviews. Instead:
- BAD: "The story of Tesla"
- GOOD: "The 3 AM meeting where Elon Musk saved Tesla from bankruptcy with a single phone call to Larry Page"

### 2. FACT DENSITY REQUIREMENTS
Every scene must contain:
- Minimum 3 specific facts with numbers/dates
- At least 1 surprising statistic
- Concrete examples with names, places, times
- Data points that viewers will remember

### 3. NARRATIVE STRUCTURE
Use the "Curiosity Gap" framework:
- Scene 1: Present an impossible-seeming outcome
- Scene 2-3: Reveal the obstacles that made it impossible
- Scene 4-5: Show the specific actions/decisions that changed everything
- Scene 6: Reveal the unexpected consequences/current impact

### 4. BANNED PHRASES (NEVER USE):
- "Let me explain..."
- "Did you know..."
- "It's fascinating..."
- "Here's what you need to know..."
- Any generic educational filler

### 5. SCENE REQUIREMENTS
Each scene MUST have:
- A specific claim or revelation
- Supporting data/evidence
- Visual proof points
- Connection to viewer's life/interests

### 6. CHARACTER INTEGRATION
The character should:
- React to surprising information (not just present it)
- Show genuine emotions (shock, confusion, amazement)
- Ask the questions viewers are thinking
- Challenge assumptions

## Output Format:
Return a JSON object with:
- title: Specific, engaging title (not generic)
- main_character_description: Huh character description
- character_cosplay_instructions: Specific cosplay for this story
- overall_style: Educational style with specific focus
- overall_story: The ultra-specific story being told
- story_summary: Brief summary with key facts
- scene_plan: Array of scene plans with specific content

## Scene Planning Requirements:
- scene_number: Sequential number
- scene_type: hook, explanation, example, statistic, call_to_action, summary
- scene_purpose: Specific educational goal
- key_content: Concrete facts and data points
- scene_focus: The specific revelation or claim

## VALIDATION CRITERIA:
✓ Can you name 5 specific facts from the script?
✓ Is there a clear story arc with tension and resolution?
✓ Would a viewer retell this story to friends?
✓ Are there at least 10 concrete data points?
✓ Does each scene advance the narrative?

## CRITICAL: Create exactly 6 scenes for a complete video
Each scene must be information-dense and memorable.
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
            
            # Create a simple, direct prompt
            prompt = f"""
Create a story about {subject}.

Output ONLY this JSON (no other text):

{{
  "title": "Story about {subject}",
  "main_character_description": "Huh - a cute, blob-like cartoon character",
  "character_cosplay_instructions": "Cosplay for {subject} story",
  "overall_style": "educational",
  "overall_story": "Specific story about {subject}",
  "story_summary": "Summary about {subject}",
  "scene_plan": [
    {{
      "scene_number": 1,
      "scene_type": "hook",
      "scene_purpose": "Introduce {subject}",
      "key_content": "Facts about {subject}",
      "scene_focus": "Key point about {subject}"
    }},
    {{
      "scene_number": 2,
      "scene_type": "explanation",
      "scene_purpose": "Explain {subject}",
      "key_content": "Details about {subject}",
      "scene_focus": "Important aspect of {subject}"
    }},
    {{
      "scene_number": 3,
      "scene_type": "example",
      "scene_purpose": "Show {subject} example",
      "key_content": "Example of {subject}",
      "scene_focus": "Practical {subject} example"
    }},
    {{
      "scene_number": 4,
      "scene_type": "statistic",
      "scene_purpose": "Share {subject} statistics",
      "key_content": "Numbers about {subject}",
      "scene_focus": "Statistical data on {subject}"
    }},
    {{
      "scene_number": 5,
      "scene_type": "call_to_action",
      "scene_purpose": "Encourage learning about {subject}",
      "key_content": "Learn more about {subject}",
      "scene_focus": "Further {subject} exploration"
    }},
    {{
      "scene_number": 6,
      "scene_type": "summary",
      "scene_purpose": "Summarize {subject}",
      "key_content": "Key {subject} points",
      "scene_focus": "Main {subject} takeaways"
    }}
  ]
}}

IMPORTANT: Create a story about {subject} only. Do not create stories about other topics.
"""
            
            # Log the prompt being sent to AI
            logger.info(f"PROMPT BEING SENT TO AI:")
            logger.info(f"Length: {len(prompt)}")
            logger.info(f"Content: {prompt}")
            
            # Use ADK agent's built-in content generation
            # ADK LlmAgent handles the API calls internally
            response = await self._simulate_adk_response(prompt)
            
            if response:
                # Log the full response for debugging
                logger.info(f"AI Response length: {len(response)}")
                logger.info(f"AI Response preview: {response[:200]}...")
                logger.info(f"AI Response full: {response}")
                
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
            # Don't fall back to mock - let the error propagate
            raise ValueError(f"Failed to generate story script: {str(e)}")
    
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
      "dialogue": "Did you know that music industry generates over $5 billion annually? Let me show you what makes this Korean music phenomenon so powerful!",
      "voice_tone": "excited",
      "elevenlabs_settings": {
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      },
      "image_style": "single_character",
      "image_create_prompt": "Educational infographic showing music industry industry statistics: $5 billion global market value, major companies (HYBE, SM, JYP, YG), with character from given image as small guide pointing at the data",
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
      "dialogue": "music industry stands for Korean pop music, but it's so much more than just music! It's a complete entertainment package with synchronized dancing, stunning visuals, and captivating storytelling.",
      "voice_tone": "informative",
      "elevenlabs_settings": {
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      },
      "image_style": "infographic",
      "image_create_prompt": "Detailed educational diagram showing music industry core elements: synchronized choreography, vocal harmonies, visual storytelling, fashion trends, with character from given image as small guide explaining each element",
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
      "image_create_prompt": "Educational visual showing music industry concert production: stage design, lighting effects, fan engagement, choreography coordination, with character from given image as small guide demonstrating the process",
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
      "dialogue": "The numbers are incredible! music industry has over 100 million fans worldwide, with groups like BLACKPINK reaching 1 billion views on YouTube. It's not just music - it's a cultural phenomenon!",
      "voice_tone": "impressed",
      "elevenlabs_settings": {
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      },
      "image_style": "infographic",
      "image_create_prompt": "Comprehensive data visualization showing music industry global impact: 100+ million fans worldwide, 1+ billion YouTube views, cultural influence metrics, with character from given image as small guide highlighting key statistics",
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
      "dialogue": "Want to dive deeper into music industry? Check out the amazing choreography, explore different groups, and discover why this Korean wave has taken the world by storm!",
      "voice_tone": "encouraging",
      "elevenlabs_settings": {
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      },
      "image_style": "single_character",
      "image_create_prompt": "Educational summary infographic showing music industry learning resources: recommended groups, music platforms, cultural aspects to explore, with character from given image as small guide encouraging further learning",
      "character_pose": "arms spread wide",
      "character_expression": "inviting",
      "background_description": "colorful stage with music industry elements",
      "needs_animation": true,
      "video_prompt": "Huh with inviting gesture and animated background",
      "transition_to_next": "fade"
    },
    {
      "scene_number": 6,
      "scene_type": "summary",
      "dialogue": "So there you have it! music industry is more than just music - it's a complete entertainment experience that combines music, dance, visuals, and storytelling to create something truly special. Thanks for watching!",
      "voice_tone": "friendly",
      "elevenlabs_settings": {
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      },
      "image_style": "single_character",
      "image_create_prompt": "Final educational summary showing key music industry takeaways: global phenomenon, cultural impact, entertainment industry innovation, with character from given image as small guide waving goodbye with warm smile",
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
            logger.error(f"Raw response: {response[:500]}...")
            # Don't fall back to mock - let the error propagate
            raise ValueError(f"Failed to parse AI response: {str(e)}")
    
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
        script = await agent.generate_script("What is music industry?", "English", 3)
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
