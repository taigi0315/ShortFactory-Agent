"""
Full Script Writer Agent - New Architecture
Responsible for high-level story structure and scene planning only.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from google.adk import Agent
import google.genai as genai
from model.models import SceneType, FullScript
from core.shared_context import SharedContextManager
from core.story_validator import StoryValidator
from core.story_focus_engine import StoryFocusEngine
from core.json_parser import RobustJSONParser, JSONParsingError, parse_full_script
from core.cost_optimizer import CostOptimizer, validate_and_optimize_prompt, validate_response_quality

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FullScriptWriterAgent(Agent):
    """
    Full Script Writer Agent - New Architecture
    
    Mission: Draft the whole story and high-level pacing. Decide on scene count, 
    type, and macro flags like needs_animation, transition_to_next, and scene_importance.
    
    Does NOT specify:
    - Low-level prompts
    - TTS settings
    - Detailed visual descriptions
    - Character poses/expressions
    """
    
    def __init__(self, shared_context_manager: SharedContextManager = None):
        """Initialize Full Script Writer Agent"""
        # Check if API key is available
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        # Initialize ADK Agent
        super().__init__(
            name="full_script_writer",
            description="Creates high-level story structure and scene planning",
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
        
        # Store dependencies
        self._shared_context_manager = shared_context_manager or SharedContextManager()
        self._story_validator = StoryValidator()
        self._story_focus_engine = StoryFocusEngine()
        
        logger.info("Full Script Writer Agent initialized with new architecture")
    
    def _save_prompt_and_response(self, session_id: str, prompt: str, response: str, attempt: int = 1):
        """Save prompt and response to session directory"""
        try:
            session_dir = Path(f"sessions/{session_id}")
            prompts_dir = session_dir / "prompts"
            prompts_dir.mkdir(parents=True, exist_ok=True)
            
            # Save prompt
            prompt_file = prompts_dir / f"full_script_writer_prompt_attempt_{attempt}.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            # Save response
            response_file = prompts_dir / f"full_script_writer_response_attempt_{attempt}.txt"
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(response)
            
            logger.info(f"Saved FSW prompt and response for attempt {attempt} to {prompts_dir}")
            
        except Exception as e:
            logger.error(f"Failed to save FSW prompt and response: {str(e)}")
    
    def _get_instruction(self) -> str:
        """Get the instruction prompt for the agent"""
        return """
You are the Full Script Writer (FSW) in a multi-agent video production system.

Your mission is to create HIGH-LEVEL story structure and scene planning ONLY.

You are responsible for:
- Overall story arc and pacing
- Scene count, types, and order
- High-level story beats for each scene
- Learning objectives
- Scene importance levels (1-5)
- Animation needs and transitions

You are NOT responsible for:
- Detailed narration scripts
- TTS/voice settings
- Specific image prompts
- Character poses/expressions
- Low-level production details

Focus on creating a compelling, well-structured narrative framework that other agents can build upon.
"""
    
    async def generate_full_script(self, 
                                 topic: str, 
                                 session_id: str,
                                 length_preference: str = "60-90s",
                                 style_profile: str = "educational and engaging",
                                 target_audience: str = "general",
                                 language: str = "English",
                                 knowledge_refs: Optional[List[str]] = None,
                                 max_retries: int = 3) -> Dict[str, Any]:
        """
        Generate a high-level full script structure
        
        Args:
            topic: The subject for the video
            session_id: Session ID for saving prompts/responses
            length_preference: Desired video length (e.g., "60-90s")
            style_profile: Overall style and tone
            target_audience: Target audience description
            knowledge_refs: Optional list of reference sources
            max_retries: Maximum retry attempts
            
        Returns:
            Dict: Full script structure following FullScript.json schema
        """
        import asyncio
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating full script for topic: {topic} (attempt {attempt + 1}/{max_retries})")
                
                # Apply story focus engine
                focus_result = self._story_focus_engine.refine_story_focus(
                    broad_subject=topic,
                    initial_story=f"The story of {topic} and how it works",
                    target_audience=target_audience
                )
                
                logger.info(f"Story focus refined: {focus_result.applied_pattern.value} pattern applied")
                logger.info(f"Focus score: {focus_result.focus_score:.2f}")
                
                # Create the prompt
                prompt = self._create_fsw_prompt(
                    topic=topic,
                    length_preference=length_preference,
                    style_profile=style_profile,
                    target_audience=target_audience,
                    language=language,
                    knowledge_refs=knowledge_refs
                )
                
                # Validate and optimize prompt before sending
                is_valid, optimized_prompt, validation_message = validate_and_optimize_prompt(
                    prompt, "full_script"
                )
                
                if not is_valid:
                    logger.error(f"❌ Prompt validation failed for full script: {validation_message}")
                    raise ValueError(f"Invalid prompt for full script: {validation_message}")
                
                # Log the prompt
                logger.info(f"FSW PROMPT BEING SENT TO AI:")
                logger.info(f"Length: {len(optimized_prompt)} (optimized from {len(prompt)})")
                logger.info(f"Validation: {validation_message}")
                logger.info(f"Content: {optimized_prompt}")
                
                # Generate response using ADK
                response = await self._simulate_adk_response(optimized_prompt)
                
                if response:
                    # Save prompt and response
                    self._save_prompt_and_response(session_id, prompt, response, attempt + 1)
                    
                    # Log response
                    logger.info(f"AI Response length: {len(response)}")
                    logger.info(f"AI Response preview: {response[:200]}...")
                    
                    # Parse and validate response using robust JSON parser
                    script_data = self._parse_response_with_pydantic(response, topic)
                    
                    # Validate with story validator
                    validation_result = self._story_validator.validate_story(
                        subject=topic,
                        story=script_data.get('story_summary', ''),
                        target_audience=target_audience
                    )
                    
                    logger.info(f"Story validation: {validation_result.feasibility.value} feasibility, {validation_result.complexity_level.value} complexity")
                    
                    # Add focus engine results
                    script_data['focus_results'] = {
                        'applied_pattern': focus_result.applied_pattern.value,
                        'focus_score': focus_result.focus_score,
                        'focused_story': focus_result.focused_story
                    }
                    
                    logger.info(f"Full script generated successfully with {len(script_data.get('scenes', []))} scenes")
                    return script_data
                else:
                    raise ValueError("No response received from ADK agent.")
                    
            except Exception as e:
                logger.error(f"Error generating full script (attempt {attempt + 1}): {str(e)}")
                
                if attempt == max_retries - 1:
                    logger.error("All attempts failed")
                    raise ValueError(f"Failed to generate full script after {max_retries} attempts: {str(e)}")
                else:
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
    
    def _create_fsw_prompt(self, topic: str, length_preference: str, style_profile: str, 
                          target_audience: str, language: str, knowledge_refs: Optional[List[str]] = None) -> str:
        """Create the FSW prompt"""
        
        knowledge_section = ""
        if knowledge_refs:
            knowledge_section = f"""
KNOWLEDGE REFERENCES:
{chr(10).join([f"- {ref}" for ref in knowledge_refs])}

Use these references to ground your facts and ensure accuracy.
"""
        
        return f"""
You are the Full Script Writer (FSW) creating a high-level story structure.

TOPIC: {topic}
LENGTH PREFERENCE: {length_preference}
STYLE PROFILE: {style_profile}
TARGET AUDIENCE: {target_audience}
LANGUAGE: {language}

{knowledge_section}

MISSION:
Create a compelling story structure with high-level beats and scene planning.
Focus on narrative flow, educational value, and engagement.
Generate content in {language} language.

OUTPUT REQUIREMENTS:
- Follow FullScript.json schema exactly
- 3-8 scenes depending on topic complexity
- Each scene should have clear learning objectives
- Vary scene types for engagement
- Include scene importance levels (1-5)
- Specify animation needs and transitions

AVAILABLE SCENE TYPES:
hook, explanation, story, analysis, revelation, summary, credits, example, controversy, comparison, timeline, interview, demonstration, prediction, debate, journey, transformation, conflict, resolution

CREATIVE GUIDELINES:
- Start with a strong hook
- Build logical narrative progression with smooth transitions
- Each scene should flow naturally into the next
- Include surprising or counterintuitive elements
- End with memorable takeaways
- Consider visual storytelling opportunities

NARRATIVE FLOW REQUIREMENTS:
- Each scene's beats should logically connect to the next scene
- Avoid abrupt topic changes or disconnected content
- Create smooth transitions between concepts and ideas
- Ensure each scene builds upon previous knowledge
- Maintain consistent tone and pacing throughout

TTS-FRIENDLY CONTENT GUIDELINES:
- Plan content that avoids complex numerical expressions
- Focus on concepts that can be expressed in natural language
- Consider how technical terms will sound when spoken aloud
- Ensure story beats can be narrated smoothly without awkward number pronunciations

OUTPUT FORMAT: JSON only, following FullScript.json schema

EXAMPLE STRUCTURE:
{{
  "title": "Engaging title about {topic}",
  "logline": "One-sentence summary",
  "overall_style": "{style_profile}",
  "main_character": "Glowbie - a cute, blob-like cartoon character",
  "cosplay_instructions": "How to dress Glowbie for this topic",
  "story_summary": "120-180 word comprehensive summary",
  "scenes": [
    {{
      "scene_number": 1,
      "scene_type": "hook",
      "beats": ["Surprising opening fact", "Curiosity gap creation", "Promise of revelation"],
      "learning_objectives": ["Capture attention", "Introduce core mystery"],
      "needs_animation": true,
      "transition_to_next": "fade",
      "scene_importance": 5
    }}
  ]
}}

Remember: You are creating the FRAMEWORK. Other agents will handle detailed scripts, visuals, and audio.
Focus on story structure, learning flow, and engagement strategy.

Output ONLY valid JSON following the FullScript.json schema.
"""
    
    async def _simulate_adk_response(self, prompt: str) -> str:
        """Use actual ADK API to generate response with structured output schema"""
        try:
            logger.info("🎯 Using ADK API with output schema for full script generation")
            
            # Try different methods to call the ADK agent
            response = None
            
            # Method 1: Try run() method
            try:
                response = await self.run(prompt)
                logger.info("✅ Successfully used run() method")
            except AttributeError:
                logger.info("run() method not available, trying generate_content()")
                
                # Method 2: Try generate_content() method
                try:
                    response = await self.generate_content(prompt)
                    logger.info("✅ Successfully used generate_content() method")
                except AttributeError:
                    logger.info("generate_content() method not available, trying direct model call")
                    
                    # Method 3: Direct model call with structured output
                    client = genai.Client()
                    # Load FullScript schema for structured output
                    schema_path = Path("schemas/FullScript.json")
                    script_schema = None
                    if schema_path.exists():
                        with open(schema_path, 'r') as f:
                            script_schema = json.load(f)
                            logger.info("📋 Loaded FullScript JSON schema")
                    
                    config = {
                        "temperature": 0.6,  # Lower temperature for more consistent JSON
                        "top_p": 0.8,
                        "top_k": 30,
                        "max_output_tokens": 8192,
                        "response_mime_type": "application/json"
                    }
                    
                    # Enable schema for structured output
                    if script_schema:
                        config["response_schema"] = script_schema
                        logger.info("🎯 Using JSON schema for structured output")
                    else:
                        logger.warning("⚠️ Schema not found, using standard JSON output")
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[prompt],
                        config=config
                    )
                    logger.info("✅ Successfully used direct model call with schema")
            
            if response and hasattr(response, 'text') and response.text:
                logger.info("Successfully received response from ADK API")
                return response.text
            elif response and isinstance(response, str):
                logger.info("Successfully received string response from ADK API")
                return response
            else:
                logger.error("No response text from ADK API")
                raise ValueError("No response received from ADK API")
                
        except Exception as e:
            logger.error(f"ADK API call failed: {str(e)}")
            raise ValueError(f"ADK API call failed: {str(e)}")
    
    def _parse_response_with_pydantic(self, response_text: str, topic: str) -> Dict[str, Any]:
        """Parse AI response using robust JSON parser with Pydantic validation"""
        try:
            # Use the robust JSON parser with Pydantic validation
            full_script_model = parse_full_script(response_text)
            
            # Convert Pydantic model back to dict for compatibility
            script_data = full_script_model.model_dump()
            
            # Validate topic match
            title = script_data.get('title', '').lower()
            if topic.lower() not in title and not any(word in title for word in topic.lower().split()):
                logger.warning(f"Generated content doesn't match topic: {topic}")
                logger.warning(f"Generated title: {script_data.get('title', 'No title')}")
                # Don't raise error, just warn - let it continue
            
            logger.info(f"✅ Full script parsed and validated successfully with Pydantic")
            return script_data
            
        except JSONParsingError as e:
            logger.error(f"❌ JSON parsing failed for full script: {e}")
            logger.error(f"Raw response preview: {response_text[:500]}...")
            
            # Try to create fallback data
            try:
                logger.warning(f"⚠️ Creating fallback data for full script")
                fallback_model = RobustJSONParser.create_fallback_data(
                    FullScript,
                    context_name="full_script",
                    title=f"Generated Content: {topic}",
                    overall_style="educational",
                    story_summary=f"A brief educational video about {topic}."
                )
                fallback_dict = fallback_model.model_dump()
                return fallback_dict
            except Exception as fallback_error:
                logger.error(f"❌ Even fallback creation failed for full script: {fallback_error}")
                raise ValueError(f"Complete parsing failure for full script: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error parsing full script: {e}")
            raise ValueError(f"Unexpected parsing error for full script: {e}")
    
    def _parse_response_safely_legacy(self, response_text: str, topic: str) -> Dict[str, Any]:
        """Parse AI response safely and validate against topic"""
        try:
            # Find JSON in response
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
            
            # Validate topic match
            title = script_data.get('title', '').lower()
            if topic.lower() not in title and not any(word in title for word in topic.lower().split()):
                logger.warning(f"Generated content doesn't match topic: {topic}")
                logger.warning(f"Generated title: {script_data.get('title', 'No title')}")
                # Don't raise error, just warn - let it continue
            
            logger.info("JSON parsing successful and topic validated")
            return script_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Raw response: {response_text[:500]}...")
            raise ValueError(f"Failed to parse JSON response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in JSON parsing: {e}")
            raise ValueError(f"Unexpected error in JSON parsing: {e}")
