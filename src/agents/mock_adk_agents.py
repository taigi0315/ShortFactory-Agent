"""
Mock ADK Agents for Testing
Uses existing test_output data to avoid API costs
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from google.adk.agents import Agent
from model.models import VideoScript, Scene, SceneType, VoiceTone, ImageStyle, TransitionType
from core.session_manager import SessionManager

logger = logging.getLogger(__name__)

class MockADKScriptWriterAgent:
    """Mock ADK Script Writer Agent that returns pre-generated script"""
    
    def __init__(self):
        self.name = "mock_script_writer"
        self.description = "Mock script writer for testing - returns pre-generated script"
        self.test_output_path = Path("test_output")
        self.script_path = self.test_output_path / "script.json"
        
    async def generate_script(self, subject: str, language: str = "English", max_video_scenes: int = 8) -> VideoScript:
        """Generate script using pre-generated test data"""
        logger.info(f"Mock script generation for subject: {subject}")
        
        try:
            # Load pre-generated script
            if self.script_path.exists():
                with open(self.script_path, 'r', encoding='utf-8') as f:
                    script_data = json.load(f)
                
                # Update title to match subject
                script_data['title'] = f"Understanding {subject}"
                script_data['character_cosplay_instructions'] = f"Dress Huh as an expert on {subject}"
                
                # Update scene dialogues to match subject
                for scene in script_data['scenes']:
                    scene['dialogue'] = scene['dialogue'].replace("What is music industry?", subject)
                    scene['image_create_prompt'] = scene['image_create_prompt'].replace("What is music industry?", subject)
                    scene['video_prompt'] = scene['video_prompt'].replace("What is music industry?", subject) if scene['video_prompt'] else None
                    
                    # Update image prompts to focus on educational content
                    if 'image_create_prompt' in scene:
                        scene['image_create_prompt'] = scene['image_create_prompt'].replace("Huh", "character from given image")
                        scene['image_create_prompt'] = scene['image_create_prompt'].replace("huh", "character from given image")
                
                script = VideoScript(**script_data)
                logger.info(f"Mock script loaded successfully with {len(script.scenes)} scenes")
                return script
            else:
                logger.error(f"Test script not found at {self.script_path}")
                return self._generate_fallback_script(subject)
                
        except Exception as e:
            logger.error(f"Error loading mock script: {str(e)}")
            return self._generate_fallback_script(subject)
    
    def _generate_fallback_script(self, subject: str) -> VideoScript:
        """Generate a simple fallback script if test data is not available"""
        logger.info("Generating fallback script")
        return VideoScript(
            title=f"Understanding {subject}",
            main_character_description="Huh - a cute, blob-like cartoon character",
            character_cosplay_instructions=f"Dress Huh as an expert on {subject}",
            overall_style="educational",
            scenes=[
                Scene(
                    scene_number=1,
                    scene_type=SceneType.HOOK,
                    dialogue=f"Let me explain {subject} in a fun way!",
                    voice_tone=VoiceTone.EXCITED,
                    elevenlabs_settings={
                        "stability": 0.3,
                        "similarity_boost": 0.8,
                        "style": 0.8,
                        "speed": 1.1,
                        "loudness": 0.2
                    },
                    image_style=ImageStyle.SINGLE_CHARACTER,
                    image_create_prompt=f"Huh explaining {subject}",
                    character_pose="pointing",
                    character_expression="smiling",
                    background_description="educational setting",
                    needs_animation=True,
                    video_prompt=f"Animated explanation of {subject}",
                    transition_to_next=TransitionType.FADE,
                    hook_technique=None
                )
            ]
        )


class MockADKImageGenerateAgent:
    """Mock ADK Image Generate Agent that copies pre-generated images"""
    
    def __init__(self, session_manager: SessionManager):
        self.name = "mock_image_generator"
        self.description = "Mock image generator for testing - copies pre-generated images"
        self.session_manager = session_manager
        self.test_output_path = Path("test_output")
        self.test_images_path = self.test_output_path / "images"
        
    async def generate_images_for_session(self, session_id: str, script: VideoScript) -> Dict[str, Any]:
        """Generate images by copying pre-generated test images"""
        logger.info(f"Mock image generation for session: {session_id}")
        
        results = {
            "generated_images": [],
            "total_images": 0,
            "failed_images": 0,
            "time_taken": 0,
            "model_used": "Mock (Test Images)",
            "character": "Huh"
        }
        
        start_time = time.time()
        
        try:
            # Copy test images to session
            for scene in script.scenes:
                try:
                    scene_number = scene.scene_number
                    test_image_path = self.test_images_path / f"scene_{scene_number}.png"
                    
                    if test_image_path.exists():
                        # Read test image
                        with open(test_image_path, 'rb') as f:
                            image_data = f.read()
                        
                        # Save to session
                        image_path = self.session_manager.save_image(
                            session_id=session_id,
                            scene_number=scene_number,
                            image_data=image_data,
                            format="png"
                        )
                        
                        # Save prompt for debugging
                        self._save_prompt(session_id, scene_number, scene.image_create_prompt, "image")
                        
                        results["generated_images"].append(str(image_path))
                        results["total_images"] += 1
                        
                        logger.info(f"Mock image copied for scene {scene_number}: {image_path}")
                    else:
                        logger.warning(f"Test image not found: {test_image_path}")
                        results["failed_images"] += 1
                        
                except Exception as e:
                    logger.error(f"Error copying image for scene {scene_number}: {str(e)}")
                    results["failed_images"] += 1
            
            results["time_taken"] = time.time() - start_time
            logger.info(f"Mock image generation completed: {results['total_images']} images, {results['failed_images']} failed")
            
        except Exception as e:
            logger.error(f"Error in mock image generation: {str(e)}")
            results["time_taken"] = time.time() - start_time
        
        return results
    
    def _save_prompt(self, session_id: str, scene_number: int, prompt: str, prompt_type: str) -> None:
        """Save prompt for debugging"""
        try:
            # Create prompts directory structure
            session_path = Path("sessions") / session_id
            prompts_dir = session_path / "prompts" / prompt_type
            prompts_dir.mkdir(parents=True, exist_ok=True)
            
            # Save prompt file
            prompt_file = prompts_dir / f"scene_{scene_number}.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            logger.debug(f"Mock prompt saved: {prompt_file}")
        except Exception as e:
            logger.warning(f"Could not save mock prompt: {str(e)}")


class MockADKShortFactoryRunner:
    """Mock ADK Runner that uses mock agents for testing"""
    
    def __init__(self):
        logger.info("Initializing Mock ADK ShortFactory Runner")
        
        # Initialize session manager
        self.session_manager = SessionManager()
        
        # Initialize mock agents
        self.script_writer_agent = MockADKScriptWriterAgent()
        self.image_generate_agent = MockADKImageGenerateAgent(self.session_manager)
        
        logger.info("Mock ADK ShortFactory Runner initialized successfully")
    
    async def create_video(self, subject: str, language: str = "English", max_scenes: int = 8) -> dict:
        """Create video using mock agents (no API calls)"""
        logger.info(f"Starting mock video creation for subject: {subject}")
        
        try:
            # Create session
            session_id = self.session_manager.create_session(subject, language)
            logger.info(f"Mock session created: {session_id}")
            
            # Step 1: Generate script using mock agent
            logger.info("Step 1: Generating script with mock agent...")
            script = await self.script_writer_agent.generate_script(subject, language, max_scenes)
            
            # Save script to session
            self.session_manager.save_script(session_id, script)
            
            # Step 2: Generate images using mock agent
            logger.info("Step 2: Generating images with mock agent...")
            image_results = await self.image_generate_agent.generate_images_for_session(session_id, script)
            
            # Update session metadata
            self.session_manager._update_metadata(session_id, {
                "status": "completed",
                "script_generated": True,
                "images_generated": image_results["total_images"],
                "videos_generated": 0,
                "audios_generated": 0,
                "total_scenes": len(script.scenes)
            })
            
            result = {
                "success": True,
                "session_id": session_id,
                "script": script,
                "images": image_results,
                "total_time": image_results.get("time_taken", 0),
                "model_used": "Mock (Test Data)"
            }
            
            logger.info(f"Mock video creation completed for session: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in mock video creation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": None
            }
    
    async def close(self):
        """Close mock runner"""
        logger.info("Mock ADK Runner closed")
