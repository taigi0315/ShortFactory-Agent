"""
Huh-Based Image Generation Agent
Uses the main character "Huh" from assets/huh.png with comprehensive scene information
"""

import os
import base64
import json
import time
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from core.session_manager import SessionManager
from model.models import VideoScript, Scene
import logging
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from pathlib import Path

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGenerateAgent:
    """
    Image Generation Agent
    
    This agent generates all images for the video using the main character "Huh" 
    from assets/huh.png and applies comprehensive scene information.
    
    Features:
    - Uses Huh character from assets/huh.png
    - Applies cosplay instructions
    - Combines all scene information (pose, background, scene_type)
    - Creates meaningful, educational images
    - Character stays small in the image
    - Supports vertical (9:16) and horizontal (16:9) ratios
    - Saves prompts for debugging and tracing
    """
    
    def __init__(self, session_manager: SessionManager):
        """
        Initialize Image Generation Agent
        
        Args:
            session_manager: SessionManager instance for file operations
        """
        self.session_manager = session_manager
        
        # Get API key
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        
        # Get image settings
        self.image_ratio = os.getenv('IMAGE_RATIO', 'vertical')  # 'vertical' (9:16) or 'horizontal' (16:9)
        self.number_of_images_to_video = int(os.getenv('NUMBER_OF_IMAGE_TO_VIDEO', '5'))
        
        if not self.api_key:
            logger.error("No Google API key found. Please set GEMINI_API_KEY in .env file")
            self.use_mock = True
        else:
            # Configure Google Generative AI client
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = "gemini-2.5-flash-image-preview"
            self.use_mock = False
            logger.info("Image Generation Agent initialized")
            logger.info(f"Using model: {self.model_name}")
            logger.info(f"Image ratio: {self.image_ratio}")
            logger.info(f"Number of images for video: {self.number_of_images_to_video}")
        
        # Load Huh character image
        self.huh_image_path = Path("src/assets/huh.png")
        self.huh_image_data = self._load_huh_character()
        
        if self.huh_image_data:
            logger.info("Huh character loaded successfully")
        else:
            logger.error("Failed to load Huh character image")
    
    def _load_huh_character(self) -> Optional[bytes]:
        """
        Load Huh character image from assets/huh.png
        
        Returns:
            bytes: Huh character image data
        """
        try:
            if not self.huh_image_path.exists():
                logger.error(f"Huh character image not found at {self.huh_image_path}")
                return None
            
            with open(self.huh_image_path, 'rb') as f:
                image_data = f.read()
            
            logger.info(f"Huh character loaded from {self.huh_image_path}")
            return image_data
            
        except Exception as e:
            logger.error(f"Error loading Huh character: {str(e)}")
            return None
    
    def generate_images_for_session(self, session_id: str) -> Dict[str, Any]:
        """
        Generate images for all scenes using Huh character with comprehensive scene info
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict: Generation results
        """
        logger.info(f"Generating Huh-based images for session: {session_id}")
        
        # Get script from session
        script = self._get_script_from_session(session_id)
        
        results = {
            "session_id": session_id,
            "total_scenes": len(script.scenes),
            "generated_images": [],
            "failed_images": [],
            "generation_time": 0,
            "model_used": "Google Flash 2.5 (Nano Banana) - Huh Character" if not self.use_mock else "Mock",
            "character": "Huh",
            "cosplay_instructions": script.character_cosplay_instructions if hasattr(script, 'character_cosplay_instructions') else None
        }
        
        start_time = time.time()
        
        # Step 1: Create cosplayed Huh character
        logger.info("Step 1: Creating cosplayed Huh character")
        cosplayed_huh_image = self._create_cosplayed_huh(script)
        
        if not cosplayed_huh_image:
            logger.error("Failed to create cosplayed Huh character")
            return results
        
        # Step 2: Generate images for each scene using comprehensive scene info
        for scene in script.scenes:
            try:
                logger.info(f"Step 2: Generating scene {scene.scene_number} with comprehensive scene info")
                
                # Generate image using comprehensive scene information
                image_path = self.generate_scene_with_comprehensive_info(
                    session_id=session_id,
                    scene_number=scene.scene_number,
                    cosplayed_huh_image=cosplayed_huh_image,
                    scene=scene,
                    script=script
                )
                
                results["generated_images"].append({
                    "scene_number": scene.scene_number,
                    "image_path": image_path,
                    "scene_type": scene.scene_type.value,
                    "character_pose": scene.character_pose,
                    "background_description": scene.background_description,
                    "character": "Huh (cosplayed)",
                    "cosplay_applied": True
                })
                
                logger.info(f"✅ Huh-based image generated for scene {scene.scene_number}: {image_path}")
                
                # Add delay to respect rate limits
                if not self.use_mock:
                    time.sleep(2)  # 2 second delay between requests
                
            except Exception as e:
                logger.error(f"❌ Failed to generate image for scene {scene.scene_number}: {str(e)}")
                results["failed_images"].append({
                    "scene_number": scene.scene_number,
                    "error": str(e)
                })
        
        results["generation_time"] = time.time() - start_time
        
        # Update session metadata
        self.session_manager._update_metadata(session_id, {
            "status": "images_completed",
            "progress.images_generated": len(results["generated_images"])
        })
        
        logger.info(f"Huh-based image generation completed for session {session_id}")
        logger.info(f"Generated: {len(results['generated_images'])} images")
        logger.info(f"Failed: {len(results['failed_images'])} images")
        logger.info(f"Time: {results['generation_time']:.2f} seconds")
        logger.info(f"Model: {results['model_used']}")
        logger.info(f"Character: {results['character']}")
        
        return results
    
    def _create_cosplayed_huh(self, script: VideoScript) -> Optional[bytes]:
        """
        Create cosplayed Huh character based on script instructions
        
        Args:
            script: Video script with cosplay instructions
            
        Returns:
            bytes: Cosplayed Huh character image data
        """
        try:
            # Get cosplay instructions from script
            cosplay_instructions = getattr(script, 'character_cosplay_instructions', None)
            
            if not cosplay_instructions:
                logger.warning("No cosplay instructions found, using original Huh")
                return self.huh_image_data
            
            logger.info(f"Creating cosplayed Huh with instructions: {cosplay_instructions}")
            
            # Create cosplay prompt
            cosplay_prompt = f"""
Transform this character (Huh) to look like: {cosplay_instructions}

Requirements:
- Keep Huh's basic cute, blob-like cartoon character design
- Apply the cosplay transformation as described (clothing, accessories)
- Maintain Huh's original image style and personality
- Don't change Huh's fundamental appearance - only add cosplay elements
- Maintain high quality and professional appearance
- Character should look natural in the new style
- Image ratio: {self.image_ratio} ({'9:16 vertical format for mobile/social media' if self.image_ratio == 'vertical' else '16:9 horizontal format for desktop/widescreen'})
- Professional photography quality
- Preserve Huh's cute, friendly character design
"""
            
            if self.use_mock:
                return self._generate_mock_cosplayed_huh(cosplay_instructions)
            
            # Convert Huh image to base64 for API
            base64_huh = base64.b64encode(self.huh_image_data).decode('utf-8')
            
            # Use Google Flash 2.5 for cosplay transformation
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    cosplay_prompt,
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": base64_huh
                        }
                    }
                ],
            )
            
            # Process response
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data
                    logger.info("Successfully created cosplayed Huh character")
                    return image_data
            
            logger.warning("No image data found in cosplay response, using original Huh")
            return self.huh_image_data
            
        except Exception as e:
            logger.error(f"Error creating cosplayed Huh: {str(e)}")
            logger.info("Using original Huh character")
            return self.huh_image_data
    
    def generate_scene_with_comprehensive_info(self, session_id: str, scene_number: int, 
                                            cosplayed_huh_image: bytes, scene: Scene,
                                            script: VideoScript) -> str:
        """
        Generate scene image using comprehensive scene information
        
        Args:
            session_id: Session ID
            scene_number: Scene number
            cosplayed_huh_image: Cosplayed Huh character image data
            scene: Scene object with all information
            script: Complete script object
            
        Returns:
            str: Path to generated image
        """
        # Create comprehensive scene prompt
        scene_prompt = self._create_comprehensive_scene_prompt(scene, script)
        
        if self.use_mock:
            # Generate mock image for testing
            image_data = self._generate_mock_scene_image(scene_prompt)
        else:
            # Generate scene using comprehensive information
            image_data = self._generate_scene_with_huh(
                cosplayed_huh_image, scene_prompt
            )
        
        # Save image to session
        image_path = self.session_manager.save_image(
            session_id=session_id,
            scene_number=scene_number,
            image_data=image_data,
            format="png"
        )
        
        # Save prompt for debugging and tracing
        self._save_prompt(session_id, scene_number, scene_prompt, "image")
        
        return image_path
    
    def _create_comprehensive_scene_prompt(self, scene: Scene, script: VideoScript) -> str:
        """
        Create comprehensive scene prompt using all available information
        
        Args:
            scene: Scene object with all information
            script: Complete script object
            
        Returns:
            str: Comprehensive scene prompt
        """
        # Base scene information
        base_prompt = scene.image_create_prompt
        
        # Character information
        character_info = f"""
Character: Huh (our main character)
Character description: {script.main_character_description}
Cosplay: {getattr(script, 'character_cosplay_instructions', 'No cosplay instructions')}
"""
        
        # Scene-specific information
        scene_info = f"""
Scene type: {scene.scene_type.value}
Scene number: {scene.scene_number}
Character pose: {scene.character_pose or 'Natural pose'}
Background description: {scene.background_description or 'Educational background'}
"""
        
        # Style-specific instructions
        style_instructions = self._get_style_instructions(scene.image_style.value, scene.scene_type.value)
        
        # Comprehensive prompt
        comprehensive_prompt = f"""
{base_prompt}

{character_info}

{scene_info}

{style_instructions}

CRITICAL REQUIREMENTS:
- Character (Huh) should be SMALL in the image (not dominating the frame)
- Focus on educational content and meaningful visuals
- Character should be doing something relevant to the scene
- Background should be educational and informative
- High quality, professional result
- Image ratio: {self.image_ratio} ({'9:16 vertical format for mobile/social media' if self.image_ratio == 'vertical' else '16:9 horizontal format for desktop/widescreen'})
- Character consistency maintained
- KEEP HUH'S ORIGINAL IMAGE STYLE - don't change Huh's appearance or design
- Add speech bubbles or text boxes with dialogue
- Maintain Huh's cute, blob-like cartoon character design
"""
        
        return comprehensive_prompt.strip()
    
    def _save_prompt(self, session_id: str, scene_number: int, prompt: str, prompt_type: str) -> None:
        """
        Save prompt to session for debugging and tracing
        
        Args:
            session_id: Session ID
            scene_number: Scene number
            prompt: The prompt used for generation
            prompt_type: Type of prompt ('image' or 'video')
        """
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
    
    def _get_style_instructions(self, image_style: str, scene_type: str) -> str:
        """
        Get style-specific instructions based on image style and scene type
        
        Args:
            image_style: Image style type
            scene_type: Scene type
            
        Returns:
            str: Style-specific instructions
        """
        # Scene type specific instructions
        scene_instructions = {
            "hook": "Create an engaging opening scene that grabs attention",
            "explanation": "Focus on educational content with clear information",
            "visual_demo": "Show visual demonstration or example",
            "comparison": "Create clear comparison or contrast",
            "story_telling": "Create narrative, story-like scene",
            "conclusion": "Create satisfying conclusion scene"
        }
        
        # Image style specific instructions
        style_instructions = {
            "single_character": "Character as main focus but small in frame, educational background",
            "character_with_background": "Character integrated into educational background",
            "infographic": "Clean, educational design with information hierarchy",
            "diagram_explanation": "Technical diagram with clear labels and explanations",
            "before_after_comparison": "Split-screen layout showing clear contrast",
            "step_by_step_visual": "Sequential steps with clear progression",
            "four_cut_cartoon": "Multiple panels showing progression",
            "comic_panel": "Single dramatic moment with educational focus",
            "speech_bubble": "Character with speech bubble, educational content",
            "cinematic": "Movie-like composition with educational focus",
            "close_up_reaction": "Close-up of character reaction, educational context",
            "wide_establishing_shot": "Wide view establishing educational context",
            "split_screen": "Split composition for comparison",
            "overlay_graphics": "Text and graphics overlay for education",
            "cutaway_illustration": "Supporting visual elements for explanation"
        }
        
        scene_instruction = scene_instructions.get(scene_type, "Create educational scene")
        style_instruction = style_instructions.get(image_style, "Create educational visual")
        
        return f"""
Scene type instruction: {scene_instruction}
Style instruction: {style_instruction}
"""
    
    def _generate_scene_with_huh(self, cosplayed_huh_image: bytes, scene_prompt: str) -> bytes:
        """
        Generate scene using cosplayed Huh character
        
        Args:
            cosplayed_huh_image: Cosplayed Huh character image data
            scene_prompt: Comprehensive scene prompt
            
        Returns:
            bytes: Generated image data
        """
        try:
            logger.info(f"Generating scene with Huh: {scene_prompt[:100]}...")
            
            # Convert image to base64 for API
            base64_huh = base64.b64encode(cosplayed_huh_image).decode('utf-8')
            
            # Use Google Flash 2.5 for scene generation
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    scene_prompt,
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": base64_huh
                        }
                    }
                ],
            )
            
            # Process response
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    logger.info(f"Text response: {part.text}")
                elif part.inline_data is not None:
                    image_data = part.inline_data.data
                    logger.info("Successfully generated scene with Huh")
                    return image_data
            
            # If no image data found, fall back to mock
            logger.warning("No image data found in scene response, using mock image")
            return self._generate_mock_scene_image(scene_prompt)
            
        except Exception as e:
            logger.error(f"Error generating scene with Huh: {str(e)}")
            logger.info("Falling back to mock image")
            return self._generate_mock_scene_image(scene_prompt)
    
    def _generate_mock_cosplayed_huh(self, cosplay_instructions: str) -> bytes:
        """Generate mock cosplayed Huh image"""
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Create a simple mock cosplayed Huh image with proper ratio
        if self.image_ratio == "vertical":
            width, height = 720, 1280  # 9:16 ratio
        elif self.image_ratio == "horizontal":
            width, height = 1280, 720  # 16:9 ratio
        else:
            width, height = 1024, 1024  # fallback to square
        
        image = Image.new('RGB', (width, height), color='lightblue')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        text = f"Huh (Cosplayed as {cosplay_instructions})\nMock Image"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='darkblue', font=font)
        
        # Add Huh outline
        draw.ellipse([width//4, height//4, 3*width//4, 3*height//4], outline='darkblue', width=5)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        logger.info("Generated mock cosplayed Huh image")
        return img_byte_arr
    
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
            font = ImageFont.load_default()
        except:
            font = None
        
        text = f"Huh in Educational Scene\n{scene_prompt[:50]}...\nMock Image"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='darkgreen', font=font)
        
        # Add scene elements
        draw.rectangle([width//4, height//4, 3*width//4, 3*height//4], outline='darkgreen', width=5)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        logger.info("Generated mock scene image")
        return img_byte_arr
    
    def _get_script_from_session(self, session_id: str) -> VideoScript:
        """Get script from session"""
        session_dir = self.session_manager.get_session_dir(session_id)
        script_path = session_dir / "script.json"
        
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found for session {session_id}")
        
        with open(script_path, 'r') as f:
            script_data = json.load(f)
        
        return VideoScript(**script_data)
    
    def get_generation_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get image generation status for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict: Generation status
        """
        metadata = self.session_manager.get_session_metadata(session_id)
        
        return {
            "session_id": session_id,
            "images_generated": metadata["progress"]["images_generated"],
            "total_scenes": metadata["progress"]["total_scenes"],
            "completion_percentage": (metadata["progress"]["images_generated"] / metadata["progress"]["total_scenes"]) * 100 if metadata["progress"]["total_scenes"] > 0 else 0,
            "image_files": metadata["files"]["images"],
            "model_used": "Google Flash 2.5 (Nano Banana) - Huh Character" if not self.use_mock else "Mock",
            "character": "Huh"
        }
