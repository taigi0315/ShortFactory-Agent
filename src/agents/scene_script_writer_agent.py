"""
Scene Script Writer Agent - Proper ADK LlmAgent Pattern
Uses Google ADK LlmAgent with direct Pydantic output_schema
"""

import logging
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from model.input_models import SceneExpansionInput
from model.simple_models import SimpleScenePackage

logger = logging.getLogger(__name__)


class SceneScriptWriterAgent:
    """
    Scene Script Writer Agent using proper ADK LlmAgent pattern
    No manual JSON parsing - automatic structured output via output_schema
    """
    
    def __init__(self):
        """Initialize Scene Script Writer Agent with proper ADK pattern"""
        
        # Create LlmAgent with direct Pydantic schema - NO manual parsing!
        self.agent = LlmAgent(
            model="gemini-2.5-flash",
            name="scene_script_writer",
            description="Transforms scene beats into production-ready packages with narration, visuals, and timing",
            instruction="""You are a Scene Script Writer Agent that transforms scene beats into production-ready packages.

Given scene information and context, create detailed narration, visuals, TTS settings, and timing.

REQUIREMENTS:
- Create engaging narration script with precise timing (at_ms, pause_ms)
- Design 1-6 visual frames with detailed image prompts (40+ characters each)
- Configure TTS settings (LemonFox engine, voice, speed)
- Calculate realistic timing based on narration length
- Maintain character consistency (use main character from context)

NARRATION GUIDELINES:
- Use conversational, engaging language
- Write numbers as words ("five" not "5")
- Plan realistic pacing (150-180 words per minute)
- Add appropriate pauses for emphasis

VISUAL GUIDELINES:
- Create 1-6 frames per scene for visual variety
- Each frame represents 3-5 seconds of content
- Include main character in appropriate context
- Specify shot types, poses, expressions, backgrounds
- Image prompts must be 40+ characters minimum

TTS CONFIGURATION:
- Engine: "lemonfox" (preferred)
- Voice: "sarah" (default)
- Speed: 1.0-1.2 (slightly faster for engagement)
- Language: "en-US"

OUTPUT:
You MUST respond with a JSON object matching the ScenePackageOutput schema.
Include scene_number, narration_script, visuals, tts, and timing.""",
            output_schema=SimpleScenePackage,  # Simple Gemini-compatible model!
            output_key="scene_package_result"
        )
        
        # Setup ADK Runner for proper execution
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="shortfactory",
            session_service=self.session_service
        )
        
        # Legacy compatibility for tests
        self.input_schema = SceneExpansionInput.model_json_schema()
        self.output_schema = SimpleScenePackage.model_json_schema()
        self.output_key = "scene_package_result"
        
        logger.info("🚀 ADK Scene Script Writer Agent initialized with structured output")
    
    async def expand_scene(self, input_data: SceneExpansionInput) -> SimpleScenePackage:
        """
        Expand scene using ADK LlmAgent - NO manual JSON parsing!
        
        Args:
            input_data: Type-safe scene expansion input
            
        Returns:
            ScenePackageOutput: Automatically validated output from LlmAgent
        """
        try:
            scene_data = input_data.scene_data
            scene_number = scene_data.get('scene_number', 1)
            scene_type = scene_data.get('scene_type', 'explanation')
            
            logger.info(f"🎬 Expanding scene {scene_number} ({scene_type})")
            
            # Create input prompt
            input_prompt = self._create_context_prompt(input_data)
            
            # Use ADK Runner pattern - automatic structured output!
            # No manual JSON parsing needed!
            
            # Create session for this request
            session = await self.session_service.create_session(
                app_name="shortfactory",
                user_id="system",
                session_id=f"scene_{scene_number}_{hash(str(input_data.scene_data)) % 100000}"
            )
            
            # Create user message
            user_message = types.Content(
                role='user',
                parts=[types.Part(text=input_prompt)]
            )
            
            # Run through ADK Runner
            events = self.runner.run(
                user_id="system",
                session_id=session.id,
                new_message=user_message
            )
            
            # Extract final response from events (based on ADK manual)
            final_response = None
            for event in events:
                if event.is_final_response() and event.content:
                    # Try session state first (output_key)
                    if self.output_key in session.state:
                        final_response = session.state[self.output_key]
                        logger.info(f"✅ Found structured response in session state")
                        break
                    # Fallback: extract from event content and parse manually
                    elif event.content.parts:
                        response_text = event.content.parts[0].text.strip()
                        try:
                            final_response = SimpleScenePackage.model_validate_json(response_text)
                            logger.info(f"✅ Parsed structured response from event content")
                            break
                        except Exception as parse_error:
                            logger.warning(f"⚠️ Failed to parse event content: {parse_error}")
            
            if final_response:
                logger.info(f"✅ Scene {scene_number} expansion completed with structured output")
                return final_response
            else:
                raise Exception("No structured response received from LlmAgent")
                
        except Exception as e:
            logger.error(f"❌ Scene expansion failed: {e}")
            return self._create_fallback_output(input_data)
    
    def _create_context_prompt(self, input_data: SceneExpansionInput) -> str:
        """Create context prompt from input data"""
        scene_data = input_data.scene_data
        global_context = input_data.global_context
        
        scene_number = scene_data.get('scene_number', 1)
        scene_type = scene_data.get('scene_type', 'explanation')
        beats = scene_data.get('beats', [])
        learning_objectives = scene_data.get('learning_objectives', [])
        
        main_character = global_context.get('main_character', 'Glowbie')
        overall_style = global_context.get('overall_style', 'educational and engaging')
        target_audience = global_context.get('target_audience', 'general')
        
        context = f"""
SCENE TO EXPAND:
- Scene {scene_number}: {scene_type}
- Story beats: {', '.join(beats)}
- Learning objectives: {', '.join(learning_objectives)}

CONTEXT:
- Character: {main_character}
- Style: {overall_style}
- Audience: {target_audience}
"""
        
        # Add previous scenes context if available
        if input_data.previous_scenes:
            context += "\nPREVIOUS SCENES:\n"
            for prev_scene in input_data.previous_scenes:
                context += f"- Scene {prev_scene.get('scene_number', '?')}: {prev_scene.get('summary', 'No summary')}\n"
        
        context += "\nCreate a detailed, timed, production-ready scene package."
        
        return context
    
    def _create_fallback_output(self, input_data: SceneExpansionInput) -> SimpleScenePackage:
        """Create fallback output when generation fails"""
        scene_data = input_data.scene_data
        scene_number = scene_data.get('scene_number', 1)
        
        logger.warning(f"⚠️ Creating fallback scene package for scene {scene_number}")
        
        return SimpleScenePackage(
            scene_number=scene_number,
            narration_script=[
                {
                    "line": f"This is scene {scene_number}. Content generation encountered an issue, but we're providing a basic structure.",
                    "at_ms": 0
                }
            ],
            visuals=[
                {
                    "frame_id": f"{scene_number}A",
                    "shot_type": "medium",
                    "image_prompt": "Educational scene with friendly character explaining a concept in a clear and engaging manner with colorful background"
                }
            ],
            tts={
                "engine": "lemonfox",
                "voice": "sarah",
                "speed": 1.0
            },
            timing={
                "total_ms": 5000,
                "estimated": True
            }
        )
    
    def get_schemas(self) -> dict:
        """Get schemas (legacy compatibility)"""
        return {
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "output_key": self.output_key
        }
    
    def _create_instruction(self, input_data: SceneExpansionInput) -> str:
        """Create instruction (legacy compatibility)"""
        return self.agent.instruction