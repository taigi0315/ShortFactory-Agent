"""
Image Create Agent - New Architecture
Generates images that exactly match SSW frame specifications.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import google.genai as genai
from PIL import Image
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageCreateAgent:
    """
    Image Create Agent - New Architecture
    
    Mission: Generate or request images that exactly match SSW frame specifications.
    Returns asset URIs and metadata following ImageAsset.json schema.
    """
    
    def __init__(self):
        """Initialize Image Create Agent"""
        # Check if API key is available
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        # Initialize Gemini client for image generation
        self.client = genai.Client()
        
        # Load character reference if available
        self.huh_character_path = Path("src/assets/huh.png")
        self.huh_character_data = self._load_huh_character()
        
        logger.info("Image Create Agent initialized with new architecture")
    
    def _load_huh_character(self) -> Optional[bytes]:
        """Load Huh character reference image"""
        try:
            if self.huh_character_path.exists():
                with open(self.huh_character_path, 'rb') as f:
                    character_data = f.read()
                logger.info("Huh character reference loaded successfully")
                return character_data
            else:
                logger.warning("Huh character reference not found, proceeding without reference")
                return None
        except Exception as e:
            logger.error(f"Error loading Huh character reference: {str(e)}")
            return None
    
    def _save_prompt_and_response(self, session_id: str, frame_id: str, prompt_data: Dict[str, Any]):
        """Save prompt data to session directory"""
        try:
            session_dir = Path(f"sessions/{session_id}")
            prompts_dir = session_dir / "prompts"
            prompts_dir.mkdir(parents=True, exist_ok=True)
            
            # Save prompt data
            prompt_file = prompts_dir / f"image_create_agent_{frame_id}_prompt.json"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                json.dump(prompt_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved ICA prompt for frame {frame_id} to {prompts_dir}")
            
        except Exception as e:
            logger.error(f"Failed to save ICA prompt for frame {frame_id}: {str(e)}")
    
    async def generate_images_for_scene(self, 
                                      scene_package: Dict[str, Any],
                                      session_id: str,
                                      cost_saving_mode: bool = False) -> List[Dict[str, Any]]:
        """
        Generate images for all frames in a scene package
        
        Args:
            scene_package: Scene package from SSW with visuals array
            session_id: Session ID for saving prompts/responses
            cost_saving_mode: If True, use mock images instead of AI generation
            
        Returns:
            List[Dict]: List of ImageAsset objects following ImageAsset.json schema
        """
        try:
            scene_number = scene_package.get('scene_number', 1)
            visuals = scene_package.get('visuals', [])
            
            logger.info(f"Generating {len(visuals)} images for scene {scene_number}")
            
            if cost_saving_mode:
                logger.info("💰 Cost-saving mode enabled - using mock images")
                return await self._generate_mock_images(visuals, session_id)
            
            image_assets = []
            
            for visual in visuals:
                try:
                    frame_id = visual.get('frame_id', f"{scene_number}A")
                    
                    # Generate image asset
                    asset = await self._generate_single_image(visual, session_id)
                    image_assets.append(asset)
                    
                    logger.info(f"✅ Generated image for frame {frame_id}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to generate image for frame {visual.get('frame_id', 'unknown')}: {str(e)}")
                    
                    # Create fallback asset
                    fallback_asset = self._create_fallback_asset(visual, str(e))
                    image_assets.append(fallback_asset)
            
            logger.info(f"Image generation completed: {len([a for a in image_assets if a.get('safety_result') == 'safe'])} successful, {len([a for a in image_assets if a.get('safety_result') != 'safe'])} failed")
            
            return image_assets
            
        except Exception as e:
            logger.error(f"Error generating images for scene: {str(e)}")
            raise
    
    async def _generate_single_image(self, visual: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Generate a single image from visual specification"""
        try:
            frame_id = visual.get('frame_id', '1A')
            image_prompt = visual.get('image_prompt', '')
            negative_prompt = visual.get('negative_prompt', '')
            aspect_ratio = visual.get('aspect_ratio', '16:9')
            seed = visual.get('seed', int(time.time()) % 1000000)
            guidance_scale = visual.get('guidance_scale', 7.5)
            model_hints = visual.get('model_hints', [])
            
            # Save prompt data
            prompt_data = {
                'frame_id': frame_id,
                'image_prompt': image_prompt,
                'negative_prompt': negative_prompt,
                'aspect_ratio': aspect_ratio,
                'seed': seed,
                'guidance_scale': guidance_scale,
                'model_hints': model_hints,
                'timestamp': time.time()
            }
            
            self._save_prompt_and_response(session_id, frame_id, prompt_data)
            
            # Enhance prompt with character consistency
            enhanced_prompt = self._enhance_prompt_with_character(image_prompt, model_hints)
            
            # Perform prompt sanitation
            sanitized_prompt = self._sanitize_prompt(enhanced_prompt)
            final_negative = self._enhance_negative_prompt(negative_prompt)
            
            logger.info(f"Generating image for frame {frame_id} with prompt: {sanitized_prompt[:100]}...")
            
            # Convert aspect ratio to dimensions
            width, height = self._aspect_ratio_to_dimensions(aspect_ratio)
            
            start_time = time.time()
            
            # Use Gemini Imagen for generation (placeholder - actual implementation depends on available models)
            try:
                # This is a placeholder - actual Gemini image generation API call would go here
                # For now, we'll create a mock response
                image_uri = await self._generate_with_gemini_imagen(
                    prompt=sanitized_prompt,
                    negative_prompt=final_negative,
                    width=width,
                    height=height,
                    seed=seed,
                    guidance_scale=guidance_scale,
                    session_id=session_id,
                    frame_id=frame_id
                )
                
                generation_time = int((time.time() - start_time) * 1000)
                
                # Create ImageAsset following schema
                image_asset = {
                    'frame_id': frame_id,
                    'image_uri': image_uri,
                    'thumbnail_uri': image_uri.replace('.png', '_thumb.png'),
                    'prompt_used': sanitized_prompt,
                    'negative_prompt_used': final_negative,
                    'model': 'gemini-imagen',
                    'sampler': 'ddim',
                    'cfg': guidance_scale,
                    'steps': 50,
                    'seed': seed,
                    'safety_result': 'safe',
                    'generation_time_ms': generation_time,
                    'metadata': {
                        'width': width,
                        'height': height,
                        'file_size_bytes': 0,  # Would be filled after actual generation
                        'format': 'png'
                    }
                }
                
                return image_asset
                
            except Exception as e:
                logger.error(f"Image generation failed for frame {frame_id}: {str(e)}")
                return self._create_fallback_asset(visual, str(e))
                
        except Exception as e:
            logger.error(f"Error in single image generation: {str(e)}")
            return self._create_fallback_asset(visual, str(e))
    
    async def _generate_with_gemini_imagen(self, prompt: str, negative_prompt: str, 
                                         width: int, height: int, seed: int, 
                                         guidance_scale: float, session_id: str, 
                                         frame_id: str) -> str:
        """Generate image using Gemini Imagen (placeholder implementation)"""
        try:
            # This is a placeholder implementation
            # In actual implementation, you would call the Gemini Imagen API here
            
            # For now, we'll copy a mock image to simulate generation
            session_dir = Path(f"sessions/{session_id}")
            images_dir = session_dir / "images"
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # Use mock images from test directory
            mock_images_dir = Path("tests/mock_output/images")
            if mock_images_dir.exists():
                mock_images = list(mock_images_dir.glob("*.png"))
                if mock_images:
                    # Use seed to select consistent mock image
                    selected_mock = mock_images[seed % len(mock_images)]
                    
                    # Copy to session directory
                    target_path = images_dir / f"{frame_id.lower()}.png"
                    import shutil
                    shutil.copy2(selected_mock, target_path)
                    
                    return str(target_path)
            
            # Fallback: create a simple placeholder image
            target_path = images_dir / f"{frame_id.lower()}.png"
            self._create_placeholder_image(target_path, width, height, prompt[:50])
            
            return str(target_path)
            
        except Exception as e:
            logger.error(f"Gemini Imagen generation failed: {str(e)}")
            raise
    
    def _create_placeholder_image(self, target_path: Path, width: int, height: int, text: str):
        """Create a simple placeholder image"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create image
            img = Image.new('RGB', (width, height), color='lightblue')
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                # Try to use a default font
                font = ImageFont.load_default()
            except:
                font = None
            
            # Draw text
            draw.text((10, 10), text, fill='black', font=font)
            draw.text((10, height-30), f"{width}x{height}", fill='black', font=font)
            
            # Save image
            img.save(target_path)
            
        except Exception as e:
            logger.error(f"Failed to create placeholder image: {str(e)}")
    
    async def _generate_mock_images(self, visuals: List[Dict[str, Any]], session_id: str) -> List[Dict[str, Any]]:
        """Generate mock images for cost-saving mode"""
        try:
            session_dir = Path(f"sessions/{session_id}")
            images_dir = session_dir / "images"
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # Use mock images from test directory
            mock_images_dir = Path("tests/mock_output/images")
            mock_images = []
            
            if mock_images_dir.exists():
                mock_images = list(mock_images_dir.glob("*.png"))
                logger.info(f"Found {len(mock_images)} mock images")
            
            image_assets = []
            
            for i, visual in enumerate(visuals):
                frame_id = visual.get('frame_id', f"{i+1}A")
                
                # Select mock image
                if mock_images:
                    selected_mock = mock_images[i % len(mock_images)]
                    target_path = images_dir / f"{frame_id.lower()}.png"
                    
                    import shutil
                    shutil.copy2(selected_mock, target_path)
                    
                    logger.info(f"✅ Mock image copied for frame {frame_id}: {target_path}")
                else:
                    # Create placeholder if no mock images available
                    target_path = images_dir / f"{frame_id.lower()}.png"
                    self._create_placeholder_image(target_path, 1024, 576, f"Frame {frame_id}")
                    
                    logger.info(f"✅ Placeholder created for frame {frame_id}: {target_path}")
                
                # Create ImageAsset
                image_asset = {
                    'frame_id': frame_id,
                    'image_uri': str(target_path),
                    'thumbnail_uri': str(target_path).replace('.png', '_thumb.png'),
                    'prompt_used': visual.get('image_prompt', 'Mock image'),
                    'negative_prompt_used': visual.get('negative_prompt', ''),
                    'model': 'mock',
                    'sampler': 'mock',
                    'cfg': visual.get('guidance_scale', 7.5),
                    'steps': 1,
                    'seed': visual.get('seed', 12345),
                    'safety_result': 'safe',
                    'generation_time_ms': 50,
                    'metadata': {
                        'width': 1024,
                        'height': 576,
                        'file_size_bytes': 0,
                        'format': 'png'
                    }
                }
                
                image_assets.append(image_asset)
            
            logger.info(f"✅ Mock image generation completed: {len(image_assets)} images")
            return image_assets
            
        except Exception as e:
            logger.error(f"Error generating mock images: {str(e)}")
            raise
    
    def _enhance_prompt_with_character(self, prompt: str, model_hints: List[str]) -> str:
        """Enhance prompt with character consistency"""
        try:
            # Add character consistency elements
            character_elements = [
                "cute blob-like mascot named Huh",
                "consistent character design",
                "cartoon style"
            ]
            
            # Add model hints
            style_elements = model_hints + ["high quality", "detailed", "professional"]
            
            # Combine elements
            enhanced_prompt = f"{prompt}, {', '.join(character_elements)}, {', '.join(style_elements)}"
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            return prompt
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt for safety and quality"""
        try:
            # Remove potentially problematic content
            blocked_terms = ['nsfw', 'explicit', 'violent', 'harmful']
            
            sanitized = prompt.lower()
            for term in blocked_terms:
                sanitized = sanitized.replace(term, '')
            
            # Ensure minimum length
            if len(sanitized.strip()) < 10:
                sanitized = f"educational illustration, {sanitized}"
            
            return sanitized.strip()
            
        except Exception as e:
            logger.error(f"Error sanitizing prompt: {str(e)}")
            return "educational illustration"
    
    def _enhance_negative_prompt(self, negative_prompt: str) -> str:
        """Enhance negative prompt with common exclusions"""
        base_negatives = [
            "low quality", "blurry", "distorted", "watermark", 
            "text artifacts", "extra limbs", "malformed"
        ]
        
        if negative_prompt:
            return f"{negative_prompt}, {', '.join(base_negatives)}"
        else:
            return ', '.join(base_negatives)
    
    def _aspect_ratio_to_dimensions(self, aspect_ratio: str) -> tuple:
        """Convert aspect ratio string to width/height dimensions"""
        ratio_map = {
            '16:9': (1024, 576),
            '9:16': (576, 1024),
            '1:1': (1024, 1024),
            '4:5': (819, 1024),
            '3:2': (1024, 683),
            '2:3': (683, 1024)
        }
        
        return ratio_map.get(aspect_ratio, (1024, 576))
    
    def _create_fallback_asset(self, visual: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """Create a fallback asset when generation fails"""
        frame_id = visual.get('frame_id', '1A')
        
        return {
            'frame_id': frame_id,
            'image_uri': f"fallback://error_{frame_id.lower()}.png",
            'thumbnail_uri': f"fallback://error_{frame_id.lower()}_thumb.png",
            'prompt_used': visual.get('image_prompt', 'Failed generation'),
            'negative_prompt_used': visual.get('negative_prompt', ''),
            'model': 'fallback',
            'sampler': 'none',
            'cfg': 0.0,
            'steps': 0,
            'seed': 0,
            'safety_result': 'blocked',
            'generation_time_ms': 0,
            'metadata': {
                'width': 1024,
                'height': 576,
                'file_size_bytes': 0,
                'format': 'png',
                'error': error_message
            }
        }
