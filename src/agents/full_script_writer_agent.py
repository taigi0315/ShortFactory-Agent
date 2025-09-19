"""
Full Script Writer Agent - Proper ADK LlmAgent Pattern
Uses Google ADK LlmAgent with direct Pydantic output_schema
"""

import logging
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from model.input_models import FullScriptInput
from model.simple_models import SimpleFullScript

logger = logging.getLogger(__name__)


class FullScriptWriterAgent:
    """
    Full Script Writer Agent using proper ADK LlmAgent pattern
    No manual JSON parsing - automatic structured output via output_schema
    """
    
    def __init__(self):
        """Initialize Full Script Writer Agent with proper ADK pattern"""
        
        # Create LlmAgent with direct Pydantic schema - NO manual parsing!
        self.agent = LlmAgent(
            model="gemini-2.5-flash",
            name="full_script_writer",
            description="Creates comprehensive video scripts with multiple scenes and learning objectives",
            instruction="""You are a Full Script Writer Agent that creates comprehensive, educational video scripts with depth and real-world connections.

Given a topic and preferences, create a complete script structure that goes beyond surface-level information.

EDUCATIONAL DEPTH REQUIREMENTS:
- Connect topics to real-world examples and applications
- Include scientific, historical, or cultural context where relevant
- Use comparative learning (how X relates to Y, differences between A and B)
- Provide multiple perspectives or use cases
- Include "why this matters" explanations for practical relevance

STORY STRUCTURE REQUIREMENTS:
- Create 4-7 scenes with logical progression
- Start with engaging hooks that pose interesting questions
- Build knowledge incrementally from basic to advanced concepts
- Include concrete examples that viewers can relate to
- End with actionable insights or next steps for learning

ENHANCED SCENE TYPES:
- hook: Pose intriguing questions or present surprising facts
- context: Provide real-world background, history, or scientific basis
- explanation: Core educational content with clear explanations
- example: Concrete demonstrations, case studies, or practical applications
- deeper_dive: Advanced concepts, edge cases, or expert insights
- comparison: How this relates to other concepts or alternatives
- summary: Key takeaways with practical applications

CONTENT QUALITY GUIDELINES:
- Use specific examples rather than generic descriptions
- Include numbers, data, or measurable information when relevant
- Connect abstract concepts to familiar experiences
- Address common misconceptions or questions
- Provide multiple angles or perspectives on the topic

OUTPUT:
You MUST respond with a JSON object matching the FullScriptOutput schema.
Include title, overall_style, story_summary, and scenes array with rich, detailed content.""",
            output_schema=SimpleFullScript,  # Simple Gemini-compatible model!
            output_key="full_script_result"
        )
        
        # Setup ADK Runner for proper execution
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="shortfactory",
            session_service=self.session_service
        )
        
        # Legacy compatibility for tests
        self.input_schema = FullScriptInput.model_json_schema()
        self.output_schema = SimpleFullScript.model_json_schema()
        self.output_key = "full_script_result"
        
        logger.info("🚀 ADK Full Script Writer Agent initialized with structured output")
    
    async def generate_script(self, input_data: FullScriptInput) -> SimpleFullScript:
        """
        Generate full script using ADK LlmAgent - NO manual JSON parsing!
        
        Args:
            input_data: Type-safe input data
            
        Returns:
            FullScriptOutput: Automatically validated output from LlmAgent
        """
        try:
            logger.info(f"📝 Generating full script for topic: {input_data.topic}")
            
            # Create input prompt
            input_prompt = f"""
TOPIC: {input_data.topic}

PREFERENCES:
- Length: {input_data.length_preference}
- Style: {input_data.style_profile}
- Target Audience: {input_data.target_audience}
- Language: {input_data.language}

KNOWLEDGE REFERENCES:
{chr(10).join(f"- {ref}" for ref in input_data.knowledge_refs) if input_data.knowledge_refs else "- None provided"}

Create a comprehensive script structure for this topic.
"""
            
            # Use ADK Runner pattern - automatic structured output!
            # No manual JSON parsing needed!
            
            # Create session for this request
            session = await self.session_service.create_session(
                app_name="shortfactory",
                user_id="system",
                session_id=f"script_{hash(input_data.topic) % 100000}"
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
                            final_response = SimpleFullScript.model_validate_json(response_text)
                            logger.info(f"✅ Parsed structured response from event content")
                            break
                        except Exception as parse_error:
                            logger.warning(f"⚠️ Failed to parse event content: {parse_error}")
            
            if final_response:
                return final_response
            else:
                raise Exception("No structured response received from LlmAgent")
            
        except Exception as e:
            logger.error(f"❌ Script generation failed: {e}")
            return self._create_fallback_output(input_data)
    
    def _create_fallback_output(self, input_data: FullScriptInput) -> SimpleFullScript:
        """Create fallback output when generation fails"""
        logger.warning("⚠️ Creating fallback full script output")
        
        return SimpleFullScript(
            title=f"Script for {input_data.topic}",
            overall_style=input_data.style_profile,
            story_summary=f"This is a comprehensive educational video about {input_data.topic}, designed to provide viewers with clear understanding and practical knowledge.",
            scenes=[
                {
                    "scene_number": 1,
                    "scene_type": "hook",
                    "title": f"Introduction to {input_data.topic}",
                    "beats": [f"Introduce {input_data.topic}", "Capture viewer attention"]
                },
                {
                    "scene_number": 2,
                    "scene_type": "explanation",
                    "title": f"Understanding {input_data.topic}",
                    "beats": [f"Explain key concepts of {input_data.topic}"]
                },
                {
                    "scene_number": 3,
                    "scene_type": "summary",
                    "title": "Summary and Next Steps",
                    "beats": ["Summarize key points", "Suggest next steps"]
                }
            ]
        )
    
    def get_schemas(self) -> dict:
        """Get schemas (legacy compatibility)"""
        return {
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "output_key": self.output_key
        }
    
    def _create_instruction(self, input_data: FullScriptInput) -> str:
        """Create instruction (legacy compatibility)"""
        return self.agent.instruction