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
                                   target_audience: str = "general", visual_style: VisualStyle = VisualStyle.MODERN, 
                                   max_retries: int = 3) -> StoryScript:
        """
        Generate a story script using ADK Agent
        
        Args:
            subject: The topic for the video
            language: Language for the script (default: English)
            max_video_scenes: Maximum number of scenes (default: 8)
            
        Returns:
            StoryScript: Generated story script with scene plan
        """
        import asyncio
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating script for subject: {subject} (attempt {attempt + 1}/{max_retries})")
                
                # First, refine the story focus using the Story Focus Engine
                initial_story = f"The story of {subject} and how it works"
                focus_result = self._story_focus_engine.refine_story_focus(
                    broad_subject=subject,
                    initial_story=initial_story,
                    target_audience=target_audience
                )
                
                logger.info(f"Story focus refined: {focus_result.applied_pattern.value} pattern applied")
                logger.info(f"Focus score: {focus_result.focus_score:.2f}")
                
                # Create a more specific and detailed prompt
                prompt = f"""
You are creating an educational video story about: {subject}

CRITICAL REQUIREMENTS:
1. You MUST create content ONLY about {subject}
2. You MUST follow this EXACT JSON format
3. You MUST NOT create stories about other topics like Coca-Cola, K-pop, or any other subject
4. Output ONLY the JSON, no other text

Create a story that focuses specifically on {subject}. Think about:
- What makes {subject} interesting or important?
- What are the key facts, concepts, or aspects of {subject}?
- How can you tell an engaging story about {subject}?

Output ONLY this JSON (no other text):

{{
  "title": "The Story of {subject}",
  "main_character_description": "Huh - a cute, blob-like cartoon character",
  "character_cosplay_instructions": "Dress Huh as an expert or character related to {subject}",
  "overall_style": "educational",
  "overall_story": "A specific, engaging story about {subject} that explains its importance, history, or key concepts",
  "story_summary": "A brief summary of the story about {subject}",
  "scene_plan": [
    {{
      "scene_number": 1,
      "scene_type": "hook",
      "scene_purpose": "Grab attention with an interesting fact about {subject}",
      "key_content": "Surprising or important facts about {subject}",
      "scene_focus": "What makes {subject} worth learning about"
    }},
    {{
      "scene_number": 2,
      "scene_type": "explanation",
      "scene_purpose": "Explain the core concepts of {subject}",
      "key_content": "Main concepts, definitions, or principles of {subject}",
      "scene_focus": "Understanding the basics of {subject}"
    }},
    {{
      "scene_number": 3,
      "scene_type": "example",
      "scene_purpose": "Show real-world examples of {subject}",
      "key_content": "Concrete examples, case studies, or applications of {subject}",
      "scene_focus": "How {subject} works in practice"
    }},
    {{
      "scene_number": 4,
      "scene_type": "statistic",
      "scene_purpose": "Share impressive statistics about {subject}",
      "key_content": "Numbers, data, and statistics related to {subject}",
      "scene_focus": "The scale and impact of {subject}"
    }},
    {{
      "scene_number": 5,
      "scene_type": "call_to_action",
      "scene_purpose": "Encourage further learning about {subject}",
      "key_content": "Ways to learn more about {subject}",
      "scene_focus": "Next steps for exploring {subject}"
    }},
    {{
      "scene_number": 6,
      "scene_type": "summary",
      "scene_purpose": "Summarize key points about {subject}",
      "key_content": "Main takeaways and key points about {subject}",
      "scene_focus": "What viewers should remember about {subject}"
    }}
  ]
}}

REMEMBER: This story must be about {subject} and {subject} only. Do not create content about any other topic.
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
                    
                    # Parse response safely
                    script_data = self._parse_response_safely(response, subject)
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
                
                logger.info(f"Script generated successfully on attempt {attempt + 1}")
                return story_script
                
            except Exception as e:
                logger.error(f"Error generating story script (attempt {attempt + 1}): {str(e)}")
                
                # If this is the last attempt, raise error
                if attempt == max_retries - 1:
                    logger.error("All attempts failed")
                    raise ValueError(f"Failed to generate story script after {max_retries} attempts: {str(e)}")
                else:
                    # Wait before retrying (exponential backoff)
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
    
    async def _simulate_adk_response(self, prompt: str) -> str:
        """
        Use actual ADK API to generate response
        
        Args:
            prompt: The prompt to send to the agent
            
        Returns:
            str: AI-generated response
        """
        try:
            logger.info("Using actual ADK API for script generation")
            
            # Try different ADK Agent methods
            response = None
            
            # Method 1: Try run method
            try:
                response = await self.run(prompt)
                logger.info("Successfully used run() method")
            except AttributeError:
                logger.info("run() method not available, trying generate_content()")
                # Method 2: Try generate_content method
                try:
                    response = await self.generate_content(prompt)
                    logger.info("Successfully used generate_content() method")
                except AttributeError:
                    logger.info("generate_content() method not available, trying direct model call")
                    # Method 3: Try direct model call
                    try:
                        import google.genai as genai
                        client = genai.Client()
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[prompt],
                            config={
                                "temperature": 0.7,
                                "top_p": 0.8,
                                "top_k": 40,
                                "max_output_tokens": 8192,
                                "response_mime_type": "application/json"
                            }
                        )
                        logger.info("Successfully used direct model call")
                    except Exception as direct_error:
                        logger.error(f"Direct model call failed: {str(direct_error)}")
                        raise direct_error
            
            # Process response
            if response:
                if hasattr(response, 'text') and response.text:
                    logger.info("Successfully received response from ADK API")
                    return response.text
                elif isinstance(response, str):
                    logger.info("Successfully received string response from ADK API")
                    return response
                else:
                    logger.error("Unexpected response format from ADK API")
                    raise ValueError("Invalid response format from ADK API")
            else:
                logger.error("No response from ADK API")
                raise ValueError("No response received from ADK API")
                
        except Exception as e:
            logger.error(f"ADK API call failed: {str(e)}")
            raise ValueError(f"ADK API call failed: {str(e)}")
    
    def _extract_subject_from_prompt(self, prompt: str) -> str:
        """Extract subject from prompt"""
        # Look for "about: {subject}" pattern
        import re
        match = re.search(r'about:\s*([^\n]+)', prompt)
        if match:
            return match.group(1).strip()
        
        # Fallback: look for "The Story of {subject}" pattern
        match = re.search(r'The Story of ([^"]+)', prompt)
        if match:
            return match.group(1).strip()
        
        # Default fallback
        return "Unknown Topic"
    
    
    def _parse_response_safely(self, response: str, subject: str) -> dict:
        """
        Safely parse JSON response with error handling and subject validation
        
        Args:
            response: Raw response from AI
            subject: Original subject for validation
            
        Returns:
            dict: Parsed script data
        """
        try:
            # Extract response text if it's an object
            if hasattr(response, 'text') and response.text:
                response_text = response.text
            else:
                response_text = str(response)
            
            # Find JSON boundaries
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.error("No valid JSON found in response")
                raise ValueError("No valid JSON found in AI response")
            
            # Extract clean JSON
            clean_json = response_text[start_idx:end_idx]
            logger.info(f"Extracted JSON: {clean_json[:200]}...")
            
            # Parse JSON
            script_data = json.loads(clean_json)
            
            # Validate subject match
            title = script_data.get('title', '').lower()
            if subject.lower() not in title and not any(word in title for word in subject.lower().split()):
                logger.warning(f"Generated content doesn't match subject: {subject}")
                logger.warning(f"Generated title: {script_data.get('title', 'No title')}")
                raise ValueError(f"Generated content doesn't match requested subject: {subject}")
            
            logger.info("JSON parsing successful and subject validated")
            return script_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Raw response: {response_text[:500]}...")
            raise ValueError(f"Failed to parse JSON response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in JSON parsing: {e}")
            raise ValueError(f"Unexpected error in JSON parsing: {e}")
    

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
            logger.error(f"Raw response: {response_text[:500]}...")
            # Don't fall back to mock - let the error propagate
            raise ValueError(f"Failed to parse AI response: {str(e)}")
    


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
