"""
Main Application - New Multi-Agent Architecture
Uses the redesigned agent system with proper separation of concerns.
"""

import os
import asyncio
import logging
import json
from typing import Optional, List
from dotenv import load_dotenv
from agents.orchestrator_agent import OrchestratorAgent

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewArchitectureRunner:
    """
    New Architecture Runner
    
    Uses the redesigned multi-agent system:
    - Full Script Writer (FSW): High-level story structure
    - Scene Script Writer (SSW): Detailed scene packages  
    - Image Create Agent (ICA): Production-ready image assets
    - Orchestrator: Pipeline management and validation
    """
    
    def __init__(self):
        """Initialize New Architecture Runner"""
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        # Initialize orchestrator (manages all other agents)
        self.orchestrator = OrchestratorAgent()
        
        logger.info("New Architecture Runner initialized successfully")
    
    async def create_video(self, 
                          topic: str,
                          length_preference: str = "60-90s",
                          style_profile: str = "educational and engaging",
                          target_audience: str = "general",
                          language: str = "English",
                          knowledge_refs: Optional[List[str]] = None,
                          cost_saving_mode: bool = False) -> dict:
        """
        Create a complete video using the new multi-agent architecture
        
        Args:
            topic: The subject for the video
            length_preference: Desired video length (e.g., "60-90s", "2-3min")
            style_profile: Overall style and tone
            target_audience: Target audience description
            language: Content language (e.g., "English", "Korean", "Spanish")
            knowledge_refs: Optional list of reference sources for grounding facts
            cost_saving_mode: Use mock images to save costs
            
        Returns:
            dict: Complete video creation results
        """
        try:
            logger.info(f"🎬 Creating video with new architecture")
            logger.info(f"📖 Topic: {topic}")
            logger.info(f"⏱️ Length: {length_preference}")
            logger.info(f"🎨 Style: {style_profile}")
            logger.info(f"👥 Audience: {target_audience}")
            logger.info(f"🌐 Language: {language}")
            logger.info(f"💰 Cost-saving mode: {cost_saving_mode}")
            
            # Use orchestrator to manage the complete pipeline
            results = await self.orchestrator.create_video(
                topic=topic,
                length_preference=length_preference,
                style_profile=style_profile,
                target_audience=target_audience,
                language=language,
                knowledge_refs=knowledge_refs,
                cost_saving_mode=cost_saving_mode
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error creating video: {str(e)}")
            raise
    
    def get_session_status(self, session_id: str) -> dict:
        """Get the status of a session"""
        return self.orchestrator.get_session_status(session_id)

async def main_new_architecture(topic: Optional[str] = None, 
                               length_preference: str = "60-90s",
                               style_profile: str = "educational and engaging",
                               target_audience: str = "general",
                               language: str = "English",
                               knowledge_refs: Optional[List[str]] = None,
                               cost_saving_mode: bool = False):
    """
    Main function for new architecture
    
    Args:
        topic: Video topic
        length_preference: Desired length
        style_profile: Style and tone
        target_audience: Target audience
        language: Content language
        knowledge_refs: Reference sources
        cost_saving_mode: Use mock images
    """
    try:
        logger.info("🚀 New Architecture Multi-Agent Video Generator")
        logger.info("=" * 60)
        
        # Get topic if not provided
        if not topic:
            topic = input("Enter video topic: ").strip()
            if not topic:
                logger.error("Topic is required")
                return
        
        # Initialize runner
        runner = NewArchitectureRunner()
        
        # Create video
        results = await runner.create_video(
            topic=topic,
            length_preference=length_preference,
            style_profile=style_profile,
            target_audience=target_audience,
            knowledge_refs=knowledge_refs,
            cost_saving_mode=cost_saving_mode
        )
        
        # Print results
        logger.info("=" * 60)
        logger.info("✅ Video creation completed successfully!")
        logger.info(f"📁 Session ID: {results['session_id']}")
        logger.info(f"📝 Title: {results['full_script'].get('title', 'N/A')}")
        logger.info(f"🎬 Scenes: {len(results['scene_packages'])}")
        logger.info(f"🖼️ Images: {len(results['image_assets'])}")
        logger.info(f"🎤 Voices: {len(results.get('voice_assets', []))}")
        logger.info(f"⏱️ Total time: {results['total_time_seconds']:.2f} seconds")
        
        # Print build report summary
        build_report = results['build_report']
        logger.info("\n📊 Build Report Summary:")
        for stage, info in build_report.get('stages', {}).items():
            status_icon = "✅" if info['status'] == 'success' else "❌"
            logger.info(f"  {status_icon} {stage}: {info['time_ms']}ms")
        
        if build_report.get('errors'):
            logger.warning(f"\n⚠️ {len(build_report['errors'])} errors occurred:")
            for error in build_report['errors']:
                logger.warning(f"  - {error['stage']}: {error['error']}")
        
        return results
        
    except KeyboardInterrupt:
        logger.info("\n👋 Operation cancelled by user")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    def parse_arguments():
        parser = argparse.ArgumentParser(description='New Architecture Multi-Agent Video Generator')
        parser.add_argument('topic', nargs='?', help='Video topic (e.g., "Why are dachshunds short?")')
        parser.add_argument('--length', default='60-90s', help='Video length preference (default: 60-90s)')
        parser.add_argument('--style', default='educational and engaging', help='Style profile (default: educational and engaging)')
        parser.add_argument('--audience', default='general', help='Target audience (default: general)')
        parser.add_argument('--cost', action='store_true', help='Use cost-saving mode (mock images)')
        parser.add_argument('--refs', nargs='*', help='Knowledge references (URLs or citations)')
        parser.add_argument('--test', action='store_true', help='Run test mode with sample topic')
        return parser.parse_args()

    args = parse_arguments()
    
    # Handle test mode
    if args.test:
        test_topic = "Why are dachshunds so short?"
        test_refs = [
            "https://example.com/dachshund-genetics",
            "Parker, H. G. et al. FGF4 retrogene on CFA12 is responsible for chondrodysplasia and intervertebral disc disease in dogs. PNAS (2009)"
        ]
        
        asyncio.run(main_new_architecture(
            topic=test_topic,
            length_preference=args.length,
            style_profile=args.style,
            target_audience=args.audience,
            knowledge_refs=test_refs,
            cost_saving_mode=args.cost
        ))
    else:
        # Normal mode
        asyncio.run(main_new_architecture(
            topic=args.topic,
            length_preference=args.length,
            style_profile=args.style,
            target_audience=args.audience,
            knowledge_refs=args.refs,
            cost_saving_mode=args.cost
        ))
