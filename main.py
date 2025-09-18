"""
Main Application - ADK-based Architecture
Uses the efficient ADK-based agent system with structured schemas.
"""

import os
import asyncio
import logging
import json
from typing import Optional, List
from pathlib import Path
from dotenv import load_dotenv
from agents.adk_orchestrator_agent import ADKOrchestratorAgent
from core.session_manager import SessionManager

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShortFactoryRunner:
    """
    ShortFactory Runner - ADK-based Architecture
    
    Uses the efficient ADK-based multi-agent system:
    - ADK Full Script Agent: High-level story structure with schemas
    - ADK Scene Script Agent: Detailed scene packages with validation
    - Existing Image/Voice/Video Agents: Production-ready assets
    - ADK Orchestrator: Structured pipeline management
    """
    
    def __init__(self):
        """Initialize ShortFactory Runner"""
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        # Initialize session manager and ADK orchestrator
        self.session_manager = SessionManager()
        self.orchestrator = ADKOrchestratorAgent(self.session_manager)
        
        logger.info("ShortFactory Runner initialized with ADK architecture")
    
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
            
            # Use ADK orchestrator to manage the complete pipeline
            results = await self.orchestrator.create_video_package(
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

async def main_shortfactory(topic: Optional[str] = None, 
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
        runner = ShortFactoryRunner()
        
        # Create video
        results = await runner.create_video(
            topic=topic,
            length_preference=length_preference,
            style_profile=style_profile,
            target_audience=target_audience,
            knowledge_refs=knowledge_refs,
            cost_saving_mode=cost_saving_mode
        )
        
        # Print results (ADK format)
        logger.info("=" * 60)
        logger.info("✅ Video creation completed successfully!")
        logger.info(f"📁 Session ID: {results['session_id']}")
        
        # ADK 결과 구조에 맞게 수정
        if 'full_script' in results:
            logger.info(f"📝 Title: {results['full_script'].get('title', 'N/A')}")
        
        if 'scene_packages' in results:
            logger.info(f"🎬 Scenes: {len(results['scene_packages'])}")
        
        # ADK는 아직 이미지/음성 생성을 하지 않으므로 조건부 출력
        if 'image_assets' in results:
            logger.info(f"🖼️ Images: {len(results['image_assets'])}")
        if 'voice_assets' in results:
            logger.info(f"🎤 Voices: {len(results['voice_assets'])}")
        
        if results.get('video_path'):
            video_name = Path(results['video_path']).name
            logger.info(f"🎬 Video: {video_name}")
        
        if 'total_time_seconds' in results:
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
        
        asyncio.run(main_shortfactory(
            topic=test_topic,
            length_preference=args.length,
            style_profile=args.style,
            target_audience=args.audience,
            knowledge_refs=test_refs,
            cost_saving_mode=args.cost
        ))
    else:
        # Normal mode
        asyncio.run(main_shortfactory(
            topic=args.topic,
            length_preference=args.length,
            style_profile=args.style,
            target_audience=args.audience,
            knowledge_refs=args.refs,
            cost_saving_mode=args.cost
        ))
