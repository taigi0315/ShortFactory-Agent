"""
ADK-based Main Application
Uses Google Agent Development Kit for complete workflow
"""

import os
import asyncio
import logging
import json
from typing import Optional
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService

from core.session_manager import SessionManager
from agents.adk_script_writer_agent import ADKScriptWriterAgent
from agents.adk_scene_writer_agent import ADKSceneWriterAgent
from agents.adk_image_generate_agent import ADKImageGenerateAgent
# Removed non-ADK import
from model.models import VideoScript

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ADKShortFactoryRunner:
    """
    ADK-based ShortFactory Runner
    
    This class orchestrates the complete video creation workflow using Google ADK
    """
    
    def __init__(self):
        """Initialize ADK ShortFactory Runner"""
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        # Initialize services
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        self.memory_service = InMemoryMemoryService()
        
        # Initialize session manager first
        self.session_manager = SessionManager()
        
        # Initialize agents
        self.script_writer_agent = ADKScriptWriterAgent()
        self.scene_writer_agent = ADKSceneWriterAgent(self.session_manager)
        self.image_generate_agent = ADKImageGenerateAgent(self.session_manager)
        
        # Create ADK Runner with primary agent
        self.runner = Runner(
            app_name="shortfactory",
            agent=self.script_writer_agent,
            session_service=self.session_service,
            artifact_service=self.artifact_service,
            memory_service=self.memory_service
        )
        
        logger.info("ADK ShortFactory Runner initialized successfully")
    
    async def create_video(self, subject: str, language: str = "English", max_scenes: int = 8, cost_saving_mode: bool = False) -> dict:
        """
        Create a complete video using ADK workflow
        
        Args:
            subject: The topic for the video
            language: Language for the script
            max_scenes: Maximum number of scenes
            cost_saving_mode: If True, use mock images instead of AI generation
            
        Returns:
            Dict with creation results
        """
        try:
            logger.info(f"Starting ADK video creation for subject: {subject}")
            
            # Create session in SessionManager first
            session_id = self.session_manager.create_session(subject, language)
            user_id = "default_user"
            
            # Use ADK agents directly for multi-agent workflow
            logger.info("Step 1: Running multi-agent workflow with ADK agents...")
            
            # Step 1: Generate script using ADK Script Writer Agent
            logger.info("Step 1a: Generating script with ADK Script Writer Agent...")
            script = await self._generate_script_with_adk(subject, language, max_scenes, session_id)
            
            # Save script to session
            self.session_manager.save_script(session_id, script)
            
            # Step 1b: Generate detailed scene scripts using ADK Scene Writer Agent
            logger.info("Step 1b: Generating detailed scene scripts with ADK Scene Writer Agent...")
            enhanced_script = await self._generate_scene_scripts_with_adk(session_id, script, subject)
            
            # Step 2: Generate images using ADK Image Generate Agent
            logger.info("Step 1c: Generating images with ADK Image Generate Agent...")
            image_results = await self._generate_images_with_adk_agent(session_id, enhanced_script, cost_saving_mode)
            
            # Step 3: Prepare results
            results = {
                "session_id": session_id,
                "subject": subject,
                "language": language,
                "script": script,
                "image_results": image_results,
                "status": "completed",
                "workflow": "ADK-based"
            }
            
            logger.info(f"ADK video creation completed for session: {session_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error in ADK video creation: {str(e)}")
            return {
                "session_id": session_id if 'session_id' in locals() else None,
                "subject": subject,
                "error": str(e),
                "status": "failed",
                "workflow": "ADK-based"
            }
    
    async def _extract_script_from_adk_session(self, adk_session) -> Optional[VideoScript]:
        """Extract script from ADK session"""
        try:
            # Get artifacts from ADK session
            artifacts = await self.artifact_service.get_artifacts(adk_session.id)
            
            # Look for script artifact
            for artifact in artifacts:
                if artifact.type == "script" or "script" in artifact.name.lower():
                    script_data = json.loads(artifact.content)
                    return VideoScript(**script_data)
            
            return None
        except Exception as e:
            logger.error(f"Error extracting script from ADK session: {str(e)}")
            return None
    
    async def _extract_images_from_adk_session(self, adk_session) -> dict:
        """Extract images from ADK session"""
        try:
            # Get artifacts from ADK session
            artifacts = await self.artifact_service.get_artifacts(adk_session.id)
            
            image_results = {
                "generated_images": [],
                "total_images": 0,
                "failed_images": 0,
                "time_taken": 0,
                "model_used": "ADK Multi-Agent",
                "character": "Huh"
            }
            
            # Look for image artifacts
            for artifact in artifacts:
                if artifact.type == "image" or "image" in artifact.name.lower():
                    image_results["generated_images"].append({
                        "scene_number": len(image_results["generated_images"]) + 1,
                        "image_path": artifact.name,
                        "status": "generated",
                        "character": "Huh (ADK generated)"
                    })
            
            image_results["total_images"] = len(image_results["generated_images"])
            return image_results
            
        except Exception as e:
            logger.error(f"Error extracting images from ADK session: {str(e)}")
            return {"generated_images": [], "total_images": 0, "failed_images": 0, "time_taken": 0, "model_used": "ADK Multi-Agent", "character": "Huh"}
    
    async def _generate_script_with_adk(self, subject: str, language: str, max_scenes: int, session_id: str) -> VideoScript:
        """Generate script using ADK Script Writer Agent"""
        try:
            # Use ADK agent to generate story script
            story_script = await self.script_writer_agent.generate_story_script(subject, session_id, language, max_scenes)
            logger.info(f"Story script generated with {len(story_script.scene_plan)} scenes")
            
            # Convert StoryScript to VideoScript for compatibility
            from model.models import VideoScript, Scene, SceneType, ImageStyle, VoiceTone
            
            # Create scenes from scene plan
            from model.models import ElevenLabsSettings
            scenes = []
            for scene_plan in story_script.scene_plan:
                scene = Scene(
                    scene_number=scene_plan.scene_number,
                    scene_type=scene_plan.scene_type,
                    dialogue=f"Scene {scene_plan.scene_number}: {scene_plan.key_content}",
                    voice_tone=VoiceTone.FRIENDLY,
                    elevenlabs_settings=ElevenLabsSettings(
                        stability=0.3,
                        similarity_boost=0.8,
                        style=0.8,
                        speed=1.1,
                        loudness=0.2
                    ),
                    image_style=ImageStyle.SINGLE_CHARACTER,
                    image_create_prompt=f"Educational scene about {scene_plan.key_content}",
                    character_pose="pointing",
                    character_expression="smiling",
                    background_description="educational setting",
                    needs_animation=True,
                    video_prompt=f"Animated explanation of {scene_plan.key_content}",
                    transition_to_next="fade"
                )
                scenes.append(scene)
            
            # Create VideoScript
            video_script = VideoScript(
                title=story_script.title,
                main_character_description=story_script.main_character_description,
                character_cosplay_instructions=story_script.character_cosplay_instructions,
                overall_style=story_script.overall_style,
                overall_story=story_script.overall_story,
                story_summary=story_script.story_summary,
                scenes=scenes
            )
            
            return video_script
        except Exception as e:
            logger.error(f"Error generating script with ADK: {str(e)}")
            raise
    
    async def _generate_scene_scripts_with_adk(self, session_id: str, script: VideoScript, subject: str) -> VideoScript:
        """Generate detailed scene scripts using ADK Scene Writer Agent"""
        try:
            logger.info(f"Generating detailed scene scripts for {len(script.scenes)} scenes")
            
            # Create full script context for scene writers
            full_script_context = f"""
Title: {script.title}
Overall Story: {script.overall_story}
Story Summary: {script.story_summary}
Character: {script.main_character_description}
Cosplay Instructions: {script.character_cosplay_instructions}
Overall Style: {script.overall_style}
"""
            
            # Generate detailed scripts for each scene
            enhanced_scenes = []
            for scene in script.scenes:
                try:
                    logger.info(f"Generating detailed script for scene {scene.scene_number}")
                    
                    # Use Scene Writer Agent to enhance the scene
                    scene_result = await self.scene_writer_agent.write_scene_script(
                        scene_number=scene.scene_number,
                        scene_type=scene.scene_type,
                        overall_story=script.overall_story,
                        full_script_context=full_script_context,
                        subject=subject,
                        session_id=session_id
                    )
                    
                    # Update scene with enhanced details
                    if scene_result and 'success' in scene_result and scene_result['success']:
                        # Keep original scene but with enhanced details
                        enhanced_scene = scene
                        enhanced_scenes.append(enhanced_scene)
                        logger.info(f"Scene {scene.scene_number} enhanced successfully")
                    else:
                        # Fallback to original scene
                        enhanced_scenes.append(scene)
                        logger.warning(f"Scene {scene.scene_number} enhancement failed, using original")
                        
                except Exception as e:
                    logger.error(f"Error enhancing scene {scene.scene_number}: {str(e)}")
                    # Fallback to original scene
                    enhanced_scenes.append(scene)
            
            # Create enhanced VideoScript
            enhanced_script = VideoScript(
                title=script.title,
                main_character_description=script.main_character_description,
                character_cosplay_instructions=script.character_cosplay_instructions,
                overall_style=script.overall_style,
                overall_story=script.overall_story,
                story_summary=script.story_summary,
                scenes=enhanced_scenes
            )
            
            logger.info(f"Scene script generation completed for {len(enhanced_scenes)} scenes")
            return enhanced_script
            
        except Exception as e:
            logger.error(f"Error generating scene scripts with ADK: {str(e)}")
            # Return original script as fallback
            return script
    
    async def _generate_images_with_adk_agent(self, session_id: str, script: VideoScript, cost_saving_mode: bool = False) -> dict:
        """Generate images using ADK Image Generate Agent"""
        try:
            # Use ADK image agent to generate images
            results = await self.image_generate_agent.generate_images_for_session(session_id, script, cost_saving_mode=cost_saving_mode)
            logger.info(f"Images generated: {len(results.get('generated_images', []))}")
            return results
        except Exception as e:
            logger.error(f"Error generating images with ADK agent: {str(e)}")
            return {"generated_images": [], "total_images": 0, "failed_images": 0, "time_taken": 0, "model_used": "ADK Agent", "character": "Huh"}
    
    async def _generate_images_with_working_agent(self, session_id: str) -> dict:
        """Generate images using working Image Generate Agent"""
        try:
            # Use working image agent to generate images
            results = self.image_generate_agent.generate_images_for_session(session_id)
            logger.info(f"Images generated: {len(results.get('generated_images', []))}")
            return results
        except Exception as e:
            logger.error(f"Error generating images with working agent: {str(e)}")
            raise
    
    def _create_session_id(self) -> str:
        """Create a unique session ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def close(self):
        """Close the ADK Runner"""
        try:
            await self.runner.close()
            logger.info("ADK Runner closed successfully")
        except Exception as e:
            logger.error(f"Error closing ADK Runner: {str(e)}")

async def main_adk(subject: Optional[str] = None, cost_saving_mode: bool = False):
    """
    Main function for ADK-based ShortFactory
    
    Args:
        subject: Optional subject for automated testing
        cost_saving_mode: If True, use mock images instead of AI generation
    """
    print("🚀 ADK-based ShortFactory Agent")
    print("=" * 50)
    
    try:
        # Initialize ADK Runner
        runner = ADKShortFactoryRunner()
        
        # Get user input if not provided
        if subject is None:
            print("\n📝 Enter your video subject:")
            subject = input("Subject: ").strip()
            
            if not subject:
                print("❌ No subject provided. Exiting.")
                return
        
        print(f"\n🎯 Creating video for: {subject}")
        if cost_saving_mode:
            print("💰 Cost-saving mode enabled - using mock images")
        print("🔄 Using Google ADK workflow...")
        
        # Create video
        results = await runner.create_video(subject, cost_saving_mode=cost_saving_mode)
        
        if results["status"] == "completed":
            print("\n✅ Video creation completed successfully!")
            print(f"📁 Session ID: {results['session_id']}")
            print(f"📝 Script: {results['script'].title}")
            print(f"🖼️  Images: {len(results['image_results'].get('generated_images', []))}")
            print(f"⏱️  Total time: {results['image_results'].get('generation_time', 0):.2f} seconds")
        else:
            print(f"\n❌ Video creation failed: {results.get('error', 'Unknown error')}")
        
        # Close runner
        await runner.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

# Test function
async def test_adk_workflow():
    """Test the complete ADK workflow"""
    try:
        print("🧪 Testing ADK workflow...")
        runner = ADKShortFactoryRunner()
        
        # Test with a simple subject
        results = await runner.create_video("What is music industry?", "English", 3)
        
        if results["status"] == "completed":
            print("✅ ADK workflow test completed successfully!")
            print(f"Session: {results['session_id']}")
            print(f"Script: {results['script'].title}")
            print(f"Images: {len(results['image_results'].get('generated_images', []))}")
        else:
            print(f"❌ ADK workflow test failed: {results.get('error')}")
        
        await runner.close()
        return results["status"] == "completed"
        
    except Exception as e:
        print(f"❌ ADK workflow test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test
        asyncio.run(test_adk_workflow())
    else:
        # Run main application
        asyncio.run(main_adk())
