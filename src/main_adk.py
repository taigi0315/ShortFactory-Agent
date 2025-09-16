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
from agents.adk_image_generate_agent import ADKImageGenerateAgent
from agents.image_generate_agent import ImageGenerateAgent
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
        
        # Initialize agents
        self.script_writer_agent = ADKScriptWriterAgent()
        self.session_manager = SessionManager()
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
    
    async def create_video(self, subject: str, language: str = "English", max_scenes: int = 8) -> dict:
        """
        Create a complete video using ADK workflow
        
        Args:
            subject: The topic for the video
            language: Language for the script
            max_scenes: Maximum number of scenes
            
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
            script = await self._generate_script_with_adk(subject, language, max_scenes)
            
            # Save script to session
            self.session_manager.save_script(session_id, script)
            
            # Step 2: Generate images using ADK Image Generate Agent
            logger.info("Step 1b: Generating images with ADK Image Generate Agent...")
            image_results = await self._generate_images_with_adk_agent(session_id, script)
            
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
    
    async def _generate_script_with_adk(self, subject: str, language: str, max_scenes: int) -> VideoScript:
        """Generate script using ADK Script Writer Agent"""
        try:
            # Use ADK agent to generate script
            script = await self.script_writer_agent.generate_script(subject, language, max_scenes)
            logger.info(f"Script generated with {len(script.scenes)} scenes")
            return script
        except Exception as e:
            logger.error(f"Error generating script with ADK: {str(e)}")
            raise
    
    async def _generate_images_with_adk_agent(self, session_id: str, script: VideoScript) -> dict:
        """Generate images using ADK Image Generate Agent"""
        try:
            # Use ADK image agent to generate images
            results = await self.image_generate_agent.generate_images_for_session(session_id, script)
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

async def main_adk(subject: Optional[str] = None):
    """
    Main function for ADK-based ShortFactory
    
    Args:
        subject: Optional subject for automated testing
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
        print("🔄 Using Google ADK workflow...")
        
        # Create video
        results = await runner.create_video(subject)
        
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
        results = await runner.create_video("What is K-pop?", "English", 3)
        
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
