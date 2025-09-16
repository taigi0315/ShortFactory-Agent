"""
Gemini-Powered Script Writer Agent
This agent uses Google's Generative AI SDK with Gemini model to generate real video scripts
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from model.models import SceneType, ImageStyle, VoiceTone, TransitionType, HookTechnique, VideoScript, Scene, ElevenLabsSettings

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScriptWriterAgent:
    """
    Gemini-Powered Script Writer Agent
    
    This agent generates real video scripts using Google's Gemini model
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini Script Writer Agent
        
        Args:
            api_key: Google API key (if not provided, will use environment variable)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable or pass api_key parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        logger.info("Script Writer Agent initialized with Gemini 2.0 Flash")
    
    def generate_script(self, subject: str, language: str = "English", max_video_scenes: int = 8) -> VideoScript:
        """
        Generate a video script using Gemini model
        
        Args:
            subject: The topic for the video
            language: Target language (default: English)
            max_video_scenes: Maximum number of scenes (default: 8)
            
        Returns:
            VideoScript: Complete video script with scenes
        """
        try:
            logger.info(f"Generating script for subject: {subject}")
            
            # Create the prompt for Gemini
            prompt = self._create_gemini_prompt(subject, language, max_video_scenes)
            
            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response into VideoScript object
            script = self._parse_gemini_response(response.text, subject)
            
            logger.info(f"Script generated successfully with {len(script.scenes)} scenes")
            return script
            
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            # Fallback to mock data if AI fails
            logger.info("Falling back to mock data")
            return self._create_fallback_script(subject, language, max_video_scenes)
    
    def _create_gemini_prompt(self, subject: str, language: str, max_scenes: int) -> str:
        """Create a detailed prompt for Gemini"""
        
        # Extract enum values
        scene_types = [e.value for e in SceneType]
        image_styles = [e.value for e in ImageStyle]
        voice_tones = [e.value for e in VoiceTone]
        transition_types = [e.value for e in TransitionType]
        hook_techniques = [e.value for e in HookTechnique]
        
        prompt = f"""
You are an expert video script writer and creative director. Create a comprehensive video script for the subject: "{subject}"

## Requirements:
- Language: {language}
- Maximum scenes: {max_scenes}
- Target duration: 1-3 minutes
- Style: Educational and engaging

## Story Structure:
1. FIRST SCENE (HOOK): Must grab attention immediately
2. SETUP SCENES: Establish context and background
3. DEVELOPMENT SCENES: Core content delivery with detailed information
4. CLIMAX SCENE: The "aha!" moment or most important revelation
5. RESOLUTION SCENES: Summarize key learnings and provide closure

## Character Requirements:
- Use ONLY the character "Huh" - a cute, blob-like cartoon character
- Huh is the main character who appears in all scenes
- Include character_cosplay_instructions: Describe how Huh should be cosplayed/dressed for this topic (e.g., "dress Huh as a scientist with lab coat", "dress Huh as a programmer with glasses", etc.)
- Include character_expression for each scene: Describe Huh's emotional expression (e.g., "smiling", "winking", "excited", "surprised", "confident")
- Huh should be relatable and engaging
- Add speech bubbles or text boxes with dialogue for Huh in each scene

## Available Options:

Scene Types: {', '.join(scene_types)}
Image Styles: {', '.join(image_styles)}
Voice Tones: {', '.join(voice_tones)}
Transition Types: {', '.join(transition_types)}
Hook Techniques: {', '.join(hook_techniques)}

## Critical Requirements:

### Dialogue Quality:
- Each scene should have 2-4 sentences of dialogue
- Include specific facts, examples, and engaging information
- Make dialogue sound natural and conversational
- Ensure each scene teaches something valuable

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

### Output Format:
You MUST output a valid JSON object that matches this exact structure:

{{
  "title": "Compelling title for the video",
      "main_character_description": "Huh - a cute, blob-like cartoon character",
  "character_cosplay_instructions": "Instructions for how to cosplay the main character (e.g., 'cosplay like Elon Musk', 'dress as a K-pop idol')",
  "overall_style": "educational",
  "scenes": [
    {{
      "scene_number": 1,
      "scene_type": "hook",
      "dialogue": "2-4 sentences of engaging dialogue with specific information",
      "voice_tone": "excited",
      "elevenlabs_settings": {{
        "stability": 0.3,
        "similarity_boost": 0.8,
        "style": 0.8,
        "speed": 1.1,
        "loudness": 0.2
      }},
      "image_style": "single_character",
      "image_create_prompt": "Very detailed description of the image including character, background, lighting, composition, and style. Include speech bubble with dialogue text",
      "character_pose": "What Huh is doing: 'pointing at screen', 'looking at camera', 'gesturing'",
      "character_expression": "Huh's emotional expression: 'smiling', 'winking', 'excited', 'surprised', 'confident'",
      "background_description": "Educational background: 'classroom', 'office', 'lab', 'outdoor setting'",
      "needs_animation": true,
      "video_prompt": "Detailed description of animation if needed",
      "transition_to_next": "fade",
      "hook_technique": "shocking_fact"
    }}
  ]
}}

## Important Notes:
- Use exact lowercase enum values (e.g., 'excited', not 'EXCITED')
- First scene MUST be hook scene with hook_technique
- Create engaging, informative content that viewers will want to watch
- Make each scene serve a clear purpose in the overall story
- Ensure visual variety across scenes
- Balance information delivery with entertainment value
- Include specific facts and details about the subject
- Make dialogue natural and conversational

Generate a complete, engaging video script about "{subject}" that will captivate viewers and provide real educational value.
"""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str, subject: str) -> VideoScript:
        """
        Parse Gemini response into VideoScript object
        
        Args:
            response_text: Raw response from Gemini
            subject: Original subject for fallback
            
        Returns:
            VideoScript: Parsed script object
        """
        try:
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_str = response_text[json_start:json_end]
            else:
                raise ValueError("No JSON found in response")
            
            # Parse JSON
            script_data = json.loads(json_str)
            
            # Fix enum values that might be incorrect
            script_data = self._fix_enum_values(script_data)
            
            # Convert to VideoScript object
            script = VideoScript(**script_data)
            
            return script
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            logger.info(f"Response content: {response_text[:500]}")
            raise
    
    def _fix_enum_values(self, script_data: dict) -> dict:
        """
        Fix enum values that might be incorrect in AI response
        
        Args:
            script_data: Raw script data from AI
            
        Returns:
            dict: Fixed script data
        """
        # Valid enum values
        valid_scene_types = [e.value for e in SceneType]
        valid_image_styles = [e.value for e in ImageStyle]
        valid_voice_tones = [e.value for e in VoiceTone]
        valid_transition_types = [e.value for e in TransitionType]
        valid_hook_techniques = [e.value for e in HookTechnique]
        
        # Fix scenes
        if 'scenes' in script_data:
            for scene in script_data['scenes']:
                # Fix scene_type
                if 'scene_type' in scene:
                    if scene['scene_type'] not in valid_scene_types:
                        # Map common incorrect values
                        if scene['scene_type'] == 'climax':
                            scene['scene_type'] = 'explanation'
                        elif scene['scene_type'] == 'setup':
                            scene['scene_type'] = 'explanation'
                        else:
                            scene['scene_type'] = 'explanation'  # Default fallback
                
                # Fix image_style
                if 'image_style' in scene:
                    if scene['image_style'] not in valid_image_styles:
                        scene['image_style'] = 'single_character'  # Default fallback
                
                # Fix voice_tone
                if 'voice_tone' in scene:
                    if scene['voice_tone'] not in valid_voice_tones:
                        scene['voice_tone'] = 'friendly'  # Default fallback
                
                # Fix transition_to_next
                if 'transition_to_next' in scene:
                    if scene['transition_to_next'] not in valid_transition_types:
                        scene['transition_to_next'] = 'fade'  # Default fallback
                
                # Fix hook_technique
                if 'hook_technique' in scene and scene['hook_technique']:
                    if scene['hook_technique'] not in valid_hook_techniques:
                        scene['hook_technique'] = 'shocking_fact'  # Default fallback
        
        return script_data
    
    def _create_fallback_script(self, subject: str, language: str, max_scenes: int) -> VideoScript:
        """Create fallback script if AI fails"""
        
        # Create a basic script structure
        scenes = []
        
        # Scene 1: Hook
        hook_scene = Scene(
            scene_number=1,
            scene_type=SceneType.HOOK,
            dialogue=f"Did you know that {subject.lower()} has a fascinating story that most people don't know? Let me share the incredible details that will change how you think about this topic.",
            voice_tone=VoiceTone.EXCITED,
            elevenlabs_settings=ElevenLabsSettings.for_tone(VoiceTone.EXCITED),
            image_style=ImageStyle.SINGLE_CHARACTER,
            image_create_prompt=f"Our fixed character with an excited expression, pointing at the camera with wide eyes. The background shows subtle {subject.lower()} related elements floating gently. Clean, modern cartoon style with vibrant colors.",
            needs_animation=True,
            video_prompt="Character starts with a curious expression, then points excitedly at the camera as floating elements appear around them",
            transition_to_next=TransitionType.FADE,
            hook_technique=HookTechnique.SHOCKING_FACT
        )
        scenes.append(hook_scene)
        
        # Scene 2: Setup
        setup_scene = Scene(
            scene_number=2,
            scene_type=SceneType.EXPLANATION,
            dialogue=f"To understand {subject.lower()}, we need to start with the basics. This topic is more complex than it appears, and the implications are far-reaching. Let me break it down step by step.",
            voice_tone=VoiceTone.FRIENDLY,
            elevenlabs_settings=ElevenLabsSettings.for_tone(VoiceTone.FRIENDLY),
            image_style=ImageStyle.CHARACTER_WITH_BACKGROUND,
            image_create_prompt=f"Our fixed character in a friendly pose, sitting in a comfortable setting with {subject.lower()} related objects in the background. Warm, inviting lighting with a cozy atmosphere. Clean cartoon style.",
            needs_animation=False,
            transition_to_next=TransitionType.SLIDE_LEFT
        )
        scenes.append(setup_scene)
        
        # Create the script
        script = VideoScript(
            title=f"Understanding {subject}: A Complete Guide",
            main_character_description="A friendly, knowledgeable character with expressive features, wearing casual clothes, designed in a clean, modern cartoon style with vibrant colors and smooth animations.",
            overall_style="educational",
            scenes=scenes
        )
        
        return script
    
    def validate_script(self, script: VideoScript) -> Dict[str, Any]:
        """
        Validate a generated script for quality and completeness
        
        Args:
            script: The VideoScript to validate
            
        Returns:
            Dict with validation results
        """
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "scene_count": len(script.scenes),
            "has_hook_scene": False,
            "animation_scenes": 0,
            "total_dialogue_length": 0,
            "estimated_duration": 0
        }
        
        # Check if we have scenes
        if not script.scenes:
            validation_results["is_valid"] = False
            validation_results["errors"].append("No scenes found in script")
            return validation_results
        
        # Check first scene is hook scene
        first_scene = script.scenes[0]
        if first_scene.hook_technique is not None:
            validation_results["has_hook_scene"] = True
        else:
            validation_results["warnings"].append("First scene should be a hook scene")
        
        # Analyze scenes
        for scene in script.scenes:
            if scene.needs_animation:
                validation_results["animation_scenes"] += 1
            
            # Count dialogue words
            if scene.dialogue:
                validation_results["total_dialogue_length"] += len(scene.dialogue.split())
        
        # Estimate duration (150 words per minute)
        if validation_results["total_dialogue_length"] > 0:
            validation_results["estimated_duration"] = (validation_results["total_dialogue_length"] / 150) * 60
        
        # Check scene count
        if len(script.scenes) < 3:
            validation_results["warnings"].append("Script has very few scenes")
        elif len(script.scenes) > 15:
            validation_results["warnings"].append("Script has many scenes, consider reducing")
        
        # Check dialogue quality
        if validation_results["total_dialogue_length"] < 100:
            validation_results["warnings"].append("Dialogue seems too short for 1-3 minute video")
        elif validation_results["total_dialogue_length"] > 500:
            validation_results["warnings"].append("Dialogue seems too long for 1-3 minute video")
        
        return validation_results
    
    def export_script(self, script: VideoScript, format: str = "json") -> str:
        """
        Export script in different formats
        
        Args:
            script: The VideoScript to export
            format: Export format ("json", "yaml", "text")
            
        Returns:
            String representation of the script
        """
        if format == "json":
            return script.model_dump_json(indent=2)
        elif format == "text":
            return self._script_to_text(script)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _script_to_text(self, script: VideoScript) -> str:
        """Convert script to human-readable text format"""
        text = f"# {script.title}\n\n"
        text += f"**Character**: {script.main_character_description}\n"
        text += f"**Style**: {script.overall_style}\n\n"
        
        for scene in script.scenes:
            text += f"## Scene {scene.scene_number}: {scene.scene_type.value}\n"
            text += f"**Dialogue**: {scene.dialogue}\n"
            text += f"**Voice Tone**: {scene.voice_tone.value}\n"
            text += f"**Image Style**: {scene.image_style.value}\n"
            text += f"**Animation**: {'Yes' if scene.needs_animation else 'No'}\n"
            if scene.hook_technique:
                text += f"**Hook Technique**: {scene.hook_technique.value}\n"
            text += f"**Image Prompt**: {scene.image_create_prompt}\n"
            if scene.video_prompt:
                text += f"**Video Prompt**: {scene.video_prompt}\n"
            text += "\n"
        
        return text


# Example usage and testing
if __name__ == "__main__":
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set!")
        print("Please set your Google API key in .env file:")
        print("GEMINI_API_KEY='your-api-key-here'")
        exit(1)
    
    # Create agent instance
    agent = ScriptWriterAgent(api_key=api_key)
    
    # Test with sample subject
    test_subject = "How Elon Musk became CEO of Tesla"
    print(f"🤖 Testing Script Writer Agent with subject: {test_subject}")
    print("=" * 60)
    
    try:
        # Generate script
        script = agent.generate_script(
            subject=test_subject,
            language="English",
            max_video_scenes=8
        )
        
        # Validate script
        validation = agent.validate_script(script)
        print(f"✅ Validation Results: {validation}")
        print()
        
        # Export as text
        text_output = agent.export_script(script, format="text")
        print("📄 Generated Script:")
        print(text_output)
        
        # Save as JSON
        json_output = agent.export_script(script, format="json")
        filename = f"script_{test_subject.replace(' ', '_').lower()}.json"
        with open(filename, 'w') as f:
            f.write(json_output)
        print(f"💾 Saved as: {filename}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Test failed: {str(e)}")
