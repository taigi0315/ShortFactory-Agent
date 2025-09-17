"""
ADK-based Image Generate Agent
Uses Google Agent Development Kit for image generation
"""

import os
import base64
import json
import time
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import BaseTool
from google.genai import types
from core.session_manager import SessionManager
from model.models import VideoScript, Scene
import logging
from PIL import Image
from io import BytesIO
from pathlib import Path

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGenerationTool(BaseTool):
    """
    Tool for generating images using Google Flash 2.5
    """
    
    def __init__(self, session_manager: SessionManager):
        super().__init__(
            name="generate_image",
            description="Generate images using Google Flash 2.5 with Huh character"
        )
        self.session_manager = session_manager
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        
        # Get image settings
        self.image_ratio = os.getenv('IMAGE_RATIO', 'vertical')
        self.number_of_images_to_video = int(os.getenv('NUMBER_OF_IMAGE_TO_VIDEO', '5'))
        
        # Load Huh character image
        self.huh_image_path = Path("src/assets/huh.png")
        self.huh_image_data = self._load_huh_character()
        
        if self.huh_image_data:
            logger.info("Huh character loaded successfully")
        else:
            logger.error("Failed to load Huh character image")
    
    def _load_huh_character(self) -> Optional[bytes]:
        """Load Huh character image"""
        try:
            if self.huh_image_path.exists():
                with open(self.huh_image_path, 'rb') as f:
                    return f.read()
            else:
                logger.error(f"Huh character image not found at {self.huh_image_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading Huh character: {str(e)}")
            return None
    
    async def run(self, session_id: str, scene_number: int, scene_prompt: str, cosplay_instructions: str = None) -> Dict[str, Any]:
        """
        Generate an image for a scene
        
        Args:
            session_id: Session ID
            scene_number: Scene number
            scene_prompt: Prompt for image generation
            cosplay_instructions: Instructions for character cosplay
            
        Returns:
            Dict with image generation results
        """
        try:
            logger.info(f"Generating image for scene {scene_number}")
            
            # Create cosplayed Huh character if needed
            cosplayed_huh_image = self.huh_image_data
            if cosplay_instructions and self.huh_image_data:
                cosplayed_huh_image = await self._create_cosplayed_huh(cosplay_instructions)
            
            # Generate scene image
            if self.api_key:
                image_data = await self._generate_scene_with_huh(cosplayed_huh_image, scene_prompt)
            else:
                # Use mock generation as fallback
                logger.warning("No cosplayed Huh image available, using mock generation")
                image_data = self._generate_mock_scene_image(scene_prompt)
            
            # Save image to session
            image_path = self.session_manager.save_image(
                session_id=session_id,
                scene_number=scene_number,
                image_data=image_data,
                format="png"
            )
            
            # Save prompt for debugging
            self._save_prompt(session_id, scene_number, scene_prompt, "image")
            
            return {
                "success": True,
                "image_path": str(image_path),
                "scene_number": scene_number,
                "cosplay_applied": cosplay_instructions is not None
            }
            
        except Exception as e:
            logger.error(f"Error generating image for scene {scene_number}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "scene_number": scene_number
            }
    
    async def _create_cosplayed_huh(self, cosplay_instructions: str) -> bytes:
        """Create cosplayed Huh character using Gemini 2.5 Flash Image"""
        try:
            logger.info(f"Cosplay instructions: {cosplay_instructions}")
            
            # Use Gemini 2.5 Flash Image for cosplay transformation
            from google import genai
            from PIL import Image
            from io import BytesIO
            
            # Convert Huh image to PIL Image object
            huh_image_pil = Image.open(BytesIO(self.huh_image_data))
            
            # Create cosplay prompt
            cosplay_prompt = f"""
            Transform this character to look like: {cosplay_instructions}

            Requirements:
            - Keep the character's basic cute, blob-like cartoon character design
            - Apply the cosplay transformation as described (clothing, accessories)
            - Maintain the character's original image style and personality
            - Don't change the character's fundamental appearance - only add cosplay elements
            - Maintain high quality and professional appearance
            - Character should look natural in the new style
            - Image ratio: {self.image_ratio} ({'9:16 vertical format for mobile/social media' if self.image_ratio == 'vertical' else '16:9 horizontal format for desktop/widescreen'})
            - Professional photography quality
            - Preserve the character's cute, friendly character design
            """
            
            # Create client and generate cosplayed image
            client = genai.Client(api_key=self.api_key)
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[cosplay_prompt, huh_image_pil],
                config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            
            # Extract image data from response
            if response.candidates and response.candidates[0].content.parts:
                parts = response.candidates[0].content.parts
                if hasattr(parts, '__iter__'):
                    for part in parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            logger.info("✅ Cosplayed Huh generated successfully with Gemini 2.5 Flash Image")
                            return part.inline_data.data
                else:
                    # Single part
                    if hasattr(parts, 'inline_data') and parts.inline_data:
                        logger.info("✅ Cosplayed Huh generated successfully with Gemini 2.5 Flash Image")
                        return parts.inline_data.data
            
            logger.warning("No image data found in cosplay response, using original Huh")
            return self.huh_image_data
            
        except Exception as e:
            logger.error(f"Error creating cosplayed Huh: {str(e)}")
            logger.info("Using original Huh character")
            return self.huh_image_data
    
    async def _generate_scene_with_huh(self, cosplayed_huh_image: bytes, scene_prompt: str) -> bytes:
        """Generate scene image with Huh character using Gemini 2.5 Flash Image"""
        try:
            logger.info(f"Scene prompt: {scene_prompt[:100]}...")
            
            # Use Gemini 2.5 Flash Image for actual image generation
            from google import genai
            from PIL import Image
            from io import BytesIO
            
            # Convert cosplayed Huh image to PIL Image object
            cosplayed_huh_pil = Image.open(BytesIO(cosplayed_huh_image))
            
            # Create client and generate image
            client = genai.Client(api_key=self.api_key)
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[scene_prompt, cosplayed_huh_pil],
                config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            
            # Extract image data from response
            if response.candidates and response.candidates[0].content.parts:
                parts = response.candidates[0].content.parts
                if hasattr(parts, '__iter__'):
                    for part in parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            logger.info("✅ Scene image generated successfully with Gemini 2.5 Flash Image")
                            return part.inline_data.data
                else:
                    # Single part
                    if hasattr(parts, 'inline_data') and parts.inline_data:
                        logger.info("✅ Scene image generated successfully with Gemini 2.5 Flash Image")
                        return parts.inline_data.data
            
            logger.warning("No image data found in scene response, using mock image")
            return self._generate_mock_scene_image(scene_prompt)
            
        except Exception as e:
            logger.error(f"Error generating scene with Huh: {str(e)}")
            logger.info("Falling back to mock image generation")
            return self._generate_mock_scene_image(scene_prompt)
    
    async def generate_unified_scene(self, scene: Scene, cosplay_desc: str) -> bytes:
        """
        Generate scene with cosplayed character in one unified pass
        This addresses the architect feedback for unified image generation
        """
        try:
            logger.info(f"Generating unified scene for scene {scene.scene_number}")
            
            # Create unified prompt that includes both character and educational content
            unified_prompt = self._create_unified_prompt(scene, cosplay_desc)
            
            # Use the cosplayed Huh image as reference
            cosplayed_huh_pil = Image.open(BytesIO(self.huh_image_data))
            
            # Generate scene in one pass
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[unified_prompt, cosplayed_huh_pil],
                config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            
            # Extract image data from response
            if response.candidates and response.candidates[0].content.parts:
                parts = response.candidates[0].content.parts
                if hasattr(parts, '__iter__'):
                    for part in parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            logger.info("✅ Unified scene generated successfully")
                            return part.inline_data.data
                else:
                    # Single part
                    if hasattr(parts, 'inline_data') and parts.inline_data:
                        logger.info("✅ Unified scene generated successfully")
                        return parts.inline_data.data
            
            logger.warning("No image data found in unified scene generation response")
            return self._generate_mock_scene_image(unified_prompt)
            
        except Exception as e:
            logger.error(f"Error generating unified scene: {str(e)}")
            return self._generate_mock_scene_image(unified_prompt)
    
    def _create_unified_prompt(self, scene: Scene, cosplay_desc: str) -> str:
        """Create unified prompt that combines character and educational content"""
        
        # Extract educational elements for enhanced prompt
        educational_elements = self._extract_educational_elements(scene)
        
        unified_prompt = f"""
        Create an educational scene with these elements:
        
        CHARACTER (10-15% of image area):
        - A cute, blob-like cartoon character dressed as {cosplay_desc}
        - Character pose: {scene.character_pose}
        - Character expression: {scene.character_expression}
        - Keep character small and as a guide/presenter
        - Include speech bubble: "{scene.dialogue[:60]}..."
        
        EDUCATIONAL CONTENT (PRIMARY FOCUS - 85% of image):
        {scene.image_create_prompt}
        
        ENHANCED EDUCATIONAL ELEMENTS:
        {educational_elements}
        
        COMPOSITION REQUIREMENTS:
        - Image ratio: {self.image_ratio} ({'9:16' if self.image_ratio == 'vertical' else '16:9'})
        - Educational elements dominate the frame
        - Character acts as a guide pointing to educational content
        - Clear visual hierarchy with educational content as primary focus
        - Professional, clean layout suitable for educational content
        
        STYLE: {scene.image_style} approach
        - Maintain consistent visual style
        - Ensure high contrast for readability
        - Use appropriate colors for educational content
        - Include visual elements that support learning objectives
        
        TECHNICAL SPECIFICATIONS:
        - High resolution and quality
        - Clear, readable text if any
        - Professional educational design
        - Suitable for video production
        """
        
        return unified_prompt
    
    def _extract_educational_elements(self, scene: Scene) -> str:
        """Extract and format educational elements for enhanced prompt"""
        educational_content = scene.educational_content or {}
        
        elements = []
        
        # Add key concepts
        if educational_content.get("key_concepts"):
            concepts = ", ".join(educational_content["key_concepts"])
            elements.append(f"Key concepts to highlight: {concepts}")
        
        # Add specific facts
        if educational_content.get("specific_facts"):
            facts = "; ".join(educational_content["specific_facts"])
            elements.append(f"Specific facts to include: {facts}")
        
        # Add examples
        if educational_content.get("examples"):
            examples = "; ".join(educational_content["examples"])
            elements.append(f"Examples to demonstrate: {examples}")
        
        # Add statistics
        if educational_content.get("statistics"):
            stats = "; ".join(educational_content["statistics"])
            elements.append(f"Statistics to display: {stats}")
        
        # Add visual elements
        if scene.visual_elements:
            visual_elements = scene.visual_elements
            if visual_elements.get("primary_focus"):
                elements.append(f"Primary visual focus: {visual_elements['primary_focus']}")
            if visual_elements.get("secondary_elements"):
                secondary = ", ".join(visual_elements["secondary_elements"])
                elements.append(f"Secondary visual elements: {secondary}")
            if visual_elements.get("color_scheme"):
                elements.append(f"Color scheme: {visual_elements['color_scheme']}")
            if visual_elements.get("lighting"):
                elements.append(f"Lighting: {visual_elements['lighting']}")
        
        return "\n".join(elements) if elements else "Focus on clear, educational visual presentation"
    
    def _generate_mock_scene_image(self, scene_prompt: str) -> bytes:
        """Generate mock scene image"""
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Create a simple mock scene image with proper ratio
        if self.image_ratio == "vertical":
            width, height = 720, 1280  # 9:16 ratio
        elif self.image_ratio == "horizontal":
            width, height = 1280, 720  # 16:9 ratio
        else:
            width, height = 1024, 1024  # fallback to square
        
        image = Image.new('RGB', (width, height), color='lightgreen')
        draw = ImageDraw.Draw(image)
        
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Add text
        text = f"Mock Scene Image\n{scene_prompt[:50]}..."
        draw.text((50, 50), text, fill='black', font=font)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    def _save_prompt(self, session_id: str, scene_number: int, prompt: str, prompt_type: str) -> None:
        """Save prompt to session for debugging"""
        try:
            session_dir = self.session_manager.get_session_dir(session_id)
            prompts_dir = session_dir / "prompts"
            type_dir = prompts_dir / prompt_type
            
            # Create directories if they don't exist
            type_dir.mkdir(parents=True, exist_ok=True)
            
            # Save prompt to file
            prompt_file = type_dir / f"scene_{scene_number}.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(f"Scene {scene_number} - {prompt_type.upper()} Generation Prompt\n")
                f.write("=" * 50 + "\n\n")
                f.write(prompt)
            
            logger.info(f"Saved {prompt_type} prompt for scene {scene_number}: {prompt_file}")
            
        except Exception as e:
            logger.error(f"Failed to save {prompt_type} prompt for scene {scene_number}: {str(e)}")

class ADKImageGenerateAgent(Agent):
    """
    ADK-based Image Generate Agent
    
    This agent generates images using Google ADK with Gemini 2.5
    """
    
    def __init__(self, session_manager: SessionManager):
        """
        Initialize ADK Image Generate Agent
        
        Args:
            session_manager: SessionManager instance for file operations
        """
        # Check if API key is available
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        # Create image generation tool
        image_tool = ImageGenerationTool(session_manager)
        
        # Initialize ADK Agent
        super().__init__(
            name="image_generator",
            description="Generates images using Gemini 2.5 with Huh character",
                model="gemini-2.5-flash-image-preview",
            instruction=self._get_instruction(),
            tools=[image_tool],
            generate_content_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 4096
            }
        )
        
        # Store references in a way that works with ADK
        self._session_manager = session_manager
        self._image_tool = image_tool
        logger.info("ADK Image Generate Agent initialized with Gemini 2.5 Flash and Unified Generation")
    
    def _get_instruction(self) -> str:
        """Get the instruction prompt for the agent"""
        return """
You are a professional image generation agent specializing in creating educational images with a character from given image.

## Your Role:
- Generate images for video scenes using the character from given image
- Apply cosplay transformations to the character based on the topic
- Create educational, engaging visuals with focus on information delivery
- Maintain character consistency across all images

## Available Tools:
- generate_image: Generate images for scenes with character from given image

## Guidelines:
- PRIMARY FOCUS: Educational content and information delivery
- SECONDARY FOCUS: Character from given image (not "Huh" - use "character from given image")
- Always use the character from given image in images
- Apply cosplay instructions when provided
- Create educational, meaningful visuals that teach the topic
- Maintain high quality and professional appearance
- Keep character's original design and personality
- Add speech bubbles or text boxes when appropriate
- Focus on educational content, not just decorative images

## Image Requirements:
- Character should be small in the image (not dominating)
- Background should be educational and informative
- High quality, professional result
- Proper aspect ratio (vertical or horizontal)
- Character consistency maintained
- Speech bubbles or text boxes included
"""
    
    async def generate_images_for_session(self, session_id: str, script: VideoScript) -> Dict[str, Any]:
        """
        Generate images for all scenes in a script
        
        Args:
            session_id: Session ID
            script: VideoScript object
            
        Returns:
            Dict with generation results
        """
        try:
            logger.info(f"Generating images for session: {session_id}")
            
            results = {
                "session_id": session_id,
                "total_scenes": len(script.scenes),
                "generated_images": [],
                "failed_images": [],
                "generation_time": 0,
                "model_used": "Google Flash 2.5 (Nano Banana) - Huh Character",
                "character": "Huh",
                "cosplay_instructions": script.character_cosplay_instructions
            }
            
            start_time = time.time()
            
            # Generate cosplayed Huh character first
            cosplayed_huh_image = None
            if script.character_cosplay_instructions:
                cosplayed_huh_image = await self._image_tool._create_cosplayed_huh(
                    script.character_cosplay_instructions
                )
            
            # Generate images for each scene
            for scene in script.scenes:
                try:
                    # Create comprehensive scene prompt
                    scene_prompt = self._create_comprehensive_scene_prompt(scene, script)
                    
                    # Generate image using tool
                    result = await self._image_tool.run(
                        session_id=session_id,
                        scene_number=scene.scene_number,
                        scene_prompt=scene_prompt,
                        cosplay_instructions=script.character_cosplay_instructions
                    )
                    
                    if result["success"]:
                        results["generated_images"].append({
                            "scene_number": scene.scene_number,
                            "image_path": result["image_path"],
                            "scene_type": scene.scene_type,
                            "character_pose": scene.character_pose,
                            "background_description": scene.background_description,
                            "character": "Huh (cosplayed)" if result["cosplay_applied"] else "Huh",
                            "cosplay_applied": result["cosplay_applied"]
                        })
                        logger.info(f"✅ ADK image generated for scene {scene.scene_number}: {result['image_path']}")
                    else:
                        results["failed_images"].append({
                            "scene_number": scene.scene_number,
                            "error": result["error"]
                        })
                        logger.error(f"❌ Failed to generate image for scene {scene.scene_number}: {result['error']}")
                        
                except Exception as e:
                    error_msg = f"Error generating image for scene {scene.scene_number}: {str(e)}"
                    results["failed_images"].append({
                        "scene_number": scene.scene_number,
                        "error": error_msg
                    })
                    logger.error(error_msg)
            
            results["generation_time"] = time.time() - start_time
            
            logger.info(f"ADK image generation completed for session {session_id}")
            logger.info(f"Generated: {len(results['generated_images'])} images")
            logger.info(f"Failed: {len(results['failed_images'])} images")
            logger.info(f"Time: {results['generation_time']:.2f} seconds")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in generate_images_for_session: {str(e)}")
            return {
                "session_id": session_id,
                "error": str(e),
                "generated_images": [],
                "failed_images": []
            }
    
    def _create_comprehensive_scene_prompt(self, scene: Scene, script: VideoScript) -> str:
        """Create comprehensive scene prompt using all available information"""
        
        # Base scene information
        scene_info = f"""
Scene {scene.scene_number}: {scene.scene_type}
Dialogue: {scene.dialogue}
Character Pose: {scene.character_pose or 'natural pose'}
Character Expression: {scene.character_expression or 'neutral'}
Background: {scene.background_description or 'educational setting'}
Image Style: {scene.image_style}
"""
        
        # Add style-specific instructions
        style_instructions = self._get_style_instructions(scene.image_style, scene.scene_type)
        
        # Combine all information
        comprehensive_prompt = f"""
{scene_info}

{style_instructions}

{scene.image_create_prompt}

CRITICAL REQUIREMENTS:
- Character (Huh) should be SMALL in the image (not dominating the frame)
- Focus on educational content and meaningful visuals
- Character should be doing something relevant to the scene
- Background should be educational and informative
- High quality, professional result
- Image ratio: {self._image_tool.image_ratio} ({'9:16 vertical format for mobile/social media' if self._image_tool.image_ratio == 'vertical' else '16:9 horizontal format for desktop/widescreen'})
- Character consistency maintained
- KEEP HUH'S ORIGINAL IMAGE STYLE - don't change Huh's appearance or design
- Add speech bubbles or text boxes with dialogue
- Maintain Huh's cute, blob-like cartoon character design
"""
        
        return comprehensive_prompt.strip()
    
    def _get_style_instructions(self, image_style: str, scene_type: str) -> str:
        """Get style-specific instructions based on image style and scene type"""
        
        style_instructions = {
            "single_character": "Focus on educational content with character from given image as small guide",
            "character_with_background": "Show educational background elements with character from given image as guide",
            "infographic": "Create comprehensive informative visual with character from given image explaining data",
            "diagram_explanation": "Show character from given image pointing to or explaining a detailed diagram",
            "before_after_comparison": "Show character from given image with before/after visual comparison",
            "step_by_step_visual": "Show character from given image demonstrating step-by-step process",
            "four_cut_cartoon": "Create comic-style panel with character from given image",
            "comic_panel": "Design comic panel layout with character from given image",
            "speech_bubble": "Include prominent speech bubbles with character from given image",
            "cinematic": "Create cinematic composition with character from given image",
            "close_up_reaction": "Show close-up of character from given image's facial expression",
            "wide_establishing_shot": "Show wide shot with character from given image in educational setting"
        }
        
        return style_instructions.get(image_style, "Create educational visual with character from given image")

# Test function
async def test_adk_image_generate():
    """Test the ADK Image Generate Agent"""
    try:
        session_manager = SessionManager()
        agent = ADKImageGenerateAgent(session_manager)
        
        # Create test session
        session_id = session_manager.create_session("Test ADK Image Generation", "English")
        print(f"✅ Test session created: {session_id}")
        
        # Create test script
        from model.models import VideoScript, Scene, SceneType, ImageStyle, VoiceTone, TransitionType
        
        test_script = VideoScript(
            title="Test ADK Video",
            main_character_description="Huh - a cute, blob-like cartoon character",
            character_cosplay_instructions="cosplay like a music industry idol",
            overall_style="educational",
            scenes=[
                Scene(
                    scene_number=1,
                    scene_type=SceneType.HOOK,
                    dialogue="Hello, this is a test scene!",
                    voice_tone=VoiceTone.EXCITED,
                    elevenlabs_settings={'stability': 0.3, 'similarity_boost': 0.8, 'style': 0.8, 'speed': 1.1, 'loudness': 0.2},
                    image_style=ImageStyle.SINGLE_CHARACTER,
                    image_create_prompt="Test image prompt",
                    character_pose="pointing",
                    character_expression="smiling",
                    background_description="test background",
                    needs_animation=True,
                    video_prompt="test video prompt",
                    transition_to_next=TransitionType.FADE,
                    hook_technique=None
                )
            ]
        )
        
        # Save script to session
        script_path = session_manager.get_session_dir(session_id) / 'script.json'
        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(test_script.model_dump(), f, indent=2, ensure_ascii=False)
        
        # Generate images
        result = await agent.generate_images_for_session(session_id, test_script)
        print(f"✅ ADK Image generation result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ ADK Image generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_adk_image_generate())
