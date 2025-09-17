"""
ADK Scene Writer Agent
Generates detailed scene scripts with comprehensive information for image/video generation
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from google.adk.agents import Agent
from google.adk.tools import BaseTool

from model.models import VideoScript, Scene, SceneType, VoiceTone, ImageStyle, TransitionType
from core.session_manager import SessionManager
from core.shared_context import SharedContextManager, SharedContext
from core.scene_continuity_manager import SceneContinuityManager
from core.image_style_selector import ImageStyleSelector, StyleSelectionResult
from core.educational_enhancer import EducationalEnhancer, EnhancedEducationalContent

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
    
    def __init__(self, session_manager: SessionManager, shared_context_manager: SharedContextManager = None, 
                 continuity_manager: SceneContinuityManager = None, style_selector: ImageStyleSelector = None,
                 educational_enhancer: EducationalEnhancer = None):
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
        self._continuity_manager = continuity_manager or SceneContinuityManager()
        self._style_selector = style_selector or ImageStyleSelector()
        self._educational_enhancer = educational_enhancer or EducationalEnhancer()
        self._previous_styles = []  # Track previous styles for variety
        
        logger.info("ADK Scene Writer Agent initialized with Gemini 2.5 Flash, Shared Context, Continuity Manager, Image Style Selector, and Educational Enhancer")
    
    def _save_prompt_and_response(self, session_id: str, scene_number: int, prompt: str, response: str):
        """
        Save prompt and response to session directory
        
        Args:
            session_id: Session ID for the current run
            scene_number: Scene number being processed
            prompt: The prompt sent to the AI
            response: The response received from the AI
        """
        try:
            # Create prompts directory in session
            session_dir = Path(f"sessions/{session_id}")
            prompts_dir = session_dir / "prompts"
            prompts_dir.mkdir(parents=True, exist_ok=True)
            
            # Save prompt
            prompt_file = prompts_dir / f"scene_writer_scene_{scene_number}_prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            # Save response
            response_file = prompts_dir / f"scene_writer_scene_{scene_number}_response.txt"
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(response)
            
            logger.info(f"Saved scene {scene_number} prompt and response to {prompts_dir}")
            
        except Exception as e:
            logger.error(f"Failed to save scene {scene_number} prompt and response: {str(e)}")
    
    def _get_instruction(self) -> str:
        """Get the instruction prompt for the scene writer agent"""
        return """
You are a master of educational storytelling who creates INFORMATION-RICH, VISUALLY-SPECIFIC scenes.

## SCENE CREATION RULES:

### 1. DIALOGUE REQUIREMENTS
- Start with the most surprising/important fact
- Use conversational language, not teacher-speak
- Include specific numbers, names, dates
- React to information like a real person would

GOOD: "Wait, Netflix watched 30 MILLION hours of user data before greenlighting House of Cards? They literally knew it would succeed before filming a single scene!"

BAD: "Let me tell you about how Netflix uses data to make decisions."

### 2. VISUAL PROMPT REQUIREMENTS
Must specify:
- Exact data visualizations (charts, graphs, comparisons)
- Specific visual metaphors (e.g., "1 billion users shown as Earth's population")
- Before/after comparisons with real images/data
- Timeline visualizations with specific dates
- Size comparisons for scale understanding

### 3. EDUCATIONAL CONTENT STRUCTURE
educational_content must contain:
- key_concepts: Technical terms with definitions
- specific_facts: Numbers, dates, names (minimum 3)
- examples: Real-world applications
- statistics: Comparative data, growth metrics

### 4. IMAGE CREATE PROMPT FORMULA
"[PRIMARY CONTENT: Educational visualization showing X] + [SPECIFIC DATA: Include numbers Y, Z] + [VISUAL METAPHOR: Represent as A] + [CHARACTER: Small guide in corner reacting with B emotion] + [STYLE: C approach with D color scheme]"

### 5. SCENE-TO-SCENE FLOW
Each scene must:
- Reference the previous scene's revelation
- Build tension toward the next reveal
- Maintain narrative momentum
- Increase complexity progressively

## Output Format:
You MUST output a valid JSON object with this structure:

{
  "scene_number": 1,
  "scene_type": "hook",
  "dialogue": "Conversational dialogue with specific facts and reactions",
  "voice_tone": "excited",
  "elevenlabs_settings": {
    "stability": 0.3,
    "similarity_boost": 0.8,
    "style": 0.8,
    "speed": 1.1,
    "loudness": 0.2
  },
  "image_style": "infographic",
  "image_create_prompt": "[PRIMARY CONTENT: Educational visualization showing X] + [SPECIFIC DATA: Include numbers Y, Z] + [VISUAL METAPHOR: Represent as A] + [CHARACTER: Small guide in corner reacting with B emotion] + [STYLE: C approach with D color scheme]",
  "character_pose": "specific pose description",
  "character_expression": "specific expression",
  "background_description": "detailed background description",
  "needs_animation": true,
  "video_prompt": "DETAILED video description with specific actions and educational content",
  "transition_to_next": "fade",
  "hook_technique": "shocking_fact",
  "educational_content": {
    "key_concepts": ["concept1", "concept2"],
    "specific_facts": ["fact1", "fact2", "fact3"],
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

## VALIDATION CHECK:
✓ Can someone screenshot this scene and learn something?
✓ Are there at least 3 specific facts visible?
✓ Would this visual go viral on its own?
✓ Does the character add value, not distraction?
"""

    async def write_scene_script(self, scene_number: int, scene_type: str, 
                                overall_story: str, full_script_context: str, 
                                subject: str, session_id: str, shared_context: SharedContext = None) -> Dict[str, Any]:
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
            
            # Enhance educational content
            scene_data_for_enhancement = {
                "dialogue": f"Scene {scene_number} dialogue for {subject}",
                "educational_content": {},
                "image_create_prompt": f"Educational scene about {subject}"
            }
            
            enhanced_educational_content = self._educational_enhancer.enhance_educational_content(
                scene_data_for_enhancement, 
                target_audience=shared_context.target_audience if shared_context else "general"
            )
            
            educational_enhancement_info = f"""

EDUCATIONAL ENHANCEMENT GUIDELINES:
{self._educational_enhancer.generate_enhanced_prompt(enhanced_educational_content)}

IMPORTANT: Use these enhanced educational elements to create rich, detailed content!
"""
            
            # Create comprehensive prompt for scene writing
            prompt = f"""
You are a master scene writer specializing in ELABORATION and HOOKING techniques.

Scene Details:
- Scene Number: {scene_number}
- Scene Type: {scene_type}
- Subject: {subject}
- Overall Story: {overall_story}

Full Script Context:
{full_script_context}
{context_info}
{educational_enhancement_info}

ELABORATION & HOOKING MISSION:
Your job is to ELABORATE the story and ADD HOOKING elements to make each scene compelling and engaging.

ELABORATION REQUIREMENTS:
- EXPAND on the basic scene content with rich details, interesting facts, and compelling narratives
- ADD depth to the story with specific examples, case studies, and real-world applications
- INCLUDE fascinating details, surprising facts, and intriguing information
- CREATE vivid descriptions and compelling storytelling elements
- DEVELOP the scene content into something truly engaging and memorable

HOOKING REQUIREMENTS:
- START with attention-grabbing elements (questions, surprising facts, intriguing statements)
- USE compelling storytelling techniques to maintain viewer interest
- INCLUDE emotional hooks, curiosity gaps, and engaging narrative elements
- CREATE moments that make viewers want to keep watching
- ADD suspense, intrigue, or compelling questions throughout the scene

TECHNICAL REQUIREMENTS:
- Write a comprehensive scene script with ALL details needed for image/video generation
- Include specific facts, examples, and data points
- Provide detailed visual and technical information for image generation
- Ensure character from given image is used as a small guide
- MAINTAIN CONSISTENCY with shared context provided above
- Avoid repeating facts from previous scenes
- Build upon established visual elements and character state
- Include data points, visual metaphors, and compelling visual elements

VOICE & TONE SPECIFICATIONS:
- Add appropriate voice tone (excited, informative, enthusiastic, impressed, encouraging, friendly)
- Include elevenlabs settings for voice generation
- Specify character expressions and poses for visual consistency

OUTPUT FORMAT:
Generate a complete scene script in JSON format with all required fields for image/video generation.

Remember: Your primary goal is to ELABORATE the content and ADD HOOKING elements to make this scene truly compelling and engaging!
"""
            
            # Use ADK agent's built-in content generation
            response = await self._simulate_adk_response(prompt)
            
            # Save prompt and response
            if response:
                response_text = response.text if hasattr(response, 'text') else str(response)
                self._save_prompt_and_response(session_id, scene_number, prompt, response_text)
            
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
                
                # Add scene to continuity manager
                self._continuity_manager.add_scene(scene_data)
                
                # Check continuity with previous scene if available
                if len(self._continuity_manager.scene_data) > 1:
                    prev_scene = self._continuity_manager.scene_data[-2]
                    continuity_issues = self._continuity_manager.validate_scene_transition(prev_scene, scene_data)
                    
                    if continuity_issues:
                        logger.warning(f"Found {len(continuity_issues)} continuity issues in scene {scene_number}")
                        for issue in continuity_issues:
                            if issue.severity.value in ["high", "critical"]:
                                logger.error(f"Critical continuity issue: {issue.description}")
                
                # Select optimal image style using intelligent style selector
                style_result = self._style_selector.select_optimal_style(
                    scene_data=scene_data,
                    previous_styles=self._previous_styles,
                    target_audience=shared_context.target_audience if shared_context else "general"
                )
                
                # Update scene data with selected style
                scene_data["image_style"] = style_result.selected_style.value
                scene_data["style_selection_reasoning"] = style_result.reasoning
                scene_data["style_confidence"] = style_result.confidence_score
                
                # Track style for future selections
                self._previous_styles.append(style_result.selected_style)
                
                logger.info(f"Selected image style: {style_result.selected_style.value} (confidence: {style_result.confidence_score:.2f})")
                logger.info(f"Style reasoning: {style_result.reasoning}")
                
                return scene_data
            else:
                raise ValueError("No scene script text received from ADK agent.")
                
        except Exception as e:
            logger.error(f"Error writing scene script: {str(e)}")
            # Re-raise the error instead of using fallback
            raise e
    
    def get_continuity_report(self) -> Dict[str, Any]:
        """Get continuity report for all generated scenes"""
        return self._continuity_manager.get_continuity_report()
    
    def get_continuity_issues(self) -> List[Dict[str, Any]]:
        """Get all continuity issues found"""
        report = self.get_continuity_report()
        all_issues = []
        
        for severity in ["critical", "high", "medium", "low"]:
            issues = report.get(f"{severity}_issues", [])
            all_issues.extend(issues)
        
        return all_issues
    
    
    async def _simulate_adk_response(self, prompt: str) -> str:
        """
        Use actual ADK API to generate scene response
        
        Args:
            prompt: The prompt to send to the agent
            
        Returns:
            str: AI-generated response
        """
        try:
            logger.info("Using actual ADK API for scene generation")
            
            # Try different methods to call the ADK agent
            response = None
            
            # Method 1: Try run() method
            try:
                response = await self.run(prompt)
                logger.info("Successfully used run() method")
            except AttributeError:
                logger.info("run() method not available, trying generate_content()")
                
                # Method 2: Try generate_content() method
                try:
                    response = await self.generate_content(prompt)
                    logger.info("Successfully used generate_content() method")
                except AttributeError:
                    logger.info("generate_content() method not available, trying direct model call")
                    
                    # Method 3: Direct model call
                    import google.genai as genai
                    client = genai.Client()
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[prompt],
                        config={
                            "temperature": 0.8,
                            "top_p": 0.9,
                            "top_k": 40,
                            "max_output_tokens": 8192,
                            "response_mime_type": "application/json"
                        }
                    )
                    logger.info("Successfully used direct model call")
            
            if response and hasattr(response, 'text') and response.text:
                logger.info("Successfully received scene response from ADK API")
                return response.text
            elif response and isinstance(response, str):
                logger.info("Successfully received string scene response from ADK API")
                return response
            else:
                logger.error("No response text from ADK API")
                raise ValueError("No response received from ADK API")
                
        except Exception as e:
            logger.error(f"ADK API call failed for scene: {str(e)}")
            raise ValueError(f"ADK API call failed for scene: {str(e)}")
    

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
