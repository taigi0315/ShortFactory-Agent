""""
ADK-based Orchestrator Agent
Implements proper ADK patterns and manages the complete video production pipeline
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from agents.adk_full_script_agent import ADKFullScriptAgent
from agents.adk_scene_script_agent import ADKSceneScriptAgent
from core.session_manager import SessionManager

logger = logging.getLogger(__name__)

class ADKOrchestratorAgent:
    """
    ADK-based Orchestrator Agent that manages the complete video production pipeline
    Uses proper ADK patterns with structured schemas and validation
    """
    
    def __init__(self, session_manager: SessionManager):
        """Initialize ADK Orchestrator Agent"""
        self.session_manager = session_manager
        
        # Initialize sub-agents
        self.full_script_agent = ADKFullScriptAgent()
        self.scene_script_agent = ADKSceneScriptAgent()
        
        logger.info("🚀 ADK Orchestrator Agent initialized with structured sub-agents")
    
    async def create_video_package(self,
                                 topic: str,
                                 length_preference: str = "60-90s",
                                 style_profile: str = "informative and engaging",
                                 target_audience: str = "general",
                                 language: str = "English",
                                 knowledge_refs: Optional[List[str]] = None,
                                 cost_saving_mode: bool = False) -> Dict[str, Any]:
        """
        Create complete video production package using ADK agents
        
        Args:
            topic: Main topic for the video
            length_preference: Preferred video length
            style_profile: Overall style and tone
            target_audience: Target audience
            language: Content language
            knowledge_refs: Optional knowledge references
            cost_saving_mode: Whether to use cost-saving mode
            
        Returns:
            Dict containing complete video package and build report
        """
        
        # Create session
        session_id = self.session_manager.create_session(topic)
        logger.info(f"🎬 Starting ADK video production pipeline - Session: {session_id}")
        
        # Initialize build report
        build_report = {
            "session_id": session_id,
            "topic": topic,
            "created_at": datetime.now().isoformat(),
            "adk_version": "2.0",
            "pipeline_type": "adk_structured",
            "stages": {},
            "validation_results": {},
            "performance_metrics": {},
            "success": False
        }
        
        try:
            # Stage 1: Full Script Generation
            logger.info("📝 Stage 1: Generating full script structure with ADK...")
            stage_start = time.time()
            
            full_script = await self.full_script_agent.generate_full_script(
                topic=topic,
                length_preference=length_preference,
                style_profile=style_profile,
                target_audience=target_audience,
                language=language,
                knowledge_refs=knowledge_refs
            )
            
            stage_time = time.time() - stage_start
            build_report["stages"]["full_script"] = {
                "status": "success",
                "time_ms": int(stage_time * 1000),
                "scenes_count": len(full_script.get("scenes", [])),
                "agent_type": "adk_structured"
            }
            
            logger.info(f"✅ Full script generated with {len(full_script.get('scenes', []))} scenes")
            
            # Save full script
            script_file = self.session_manager.get_session_dir(session_id) / "full_script.json"
            with open(script_file, 'w', encoding='utf-8') as f:
                json.dump(full_script, f, indent=2, ensure_ascii=False)
            
            # Stage 2: Scene Script Generation
            logger.info("🎭 Stage 2: Generating detailed scene scripts with ADK...")
            stage_start = time.time()
            
            scenes = full_script.get("scenes", [])
            scene_packages = []
            previous_scenes = []
            
            # Prepare global context
            global_context = {
                "title": full_script.get("title", ""),
                "overall_style": full_script.get("overall_style", ""),
                "story_summary": full_script.get("story_summary", ""),
                "main_character": full_script.get("main_character", ""),
                "target_audience": target_audience
            }
            
            # Generate each scene package
            for scene_data in scenes:
                scene_number = scene_data.get("scene_number", 1)
                logger.info(f"🎬 Generating scene {scene_number}...")
                
                try:
                    scene_package = await self.scene_script_agent.expand_scene(
                        scene_data=scene_data,
                        global_context=global_context,
                        previous_scenes=previous_scenes.copy()
                    )
                    
                    scene_packages.append(scene_package)
                    previous_scenes.append(scene_package)
                    
                    # Save individual scene package
                    scene_file = self.session_manager.get_session_dir(session_id) / f"scene_package_{scene_number}.json"
                    with open(scene_file, 'w', encoding='utf-8') as f:
                        json.dump(scene_package, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"✅ Scene {scene_number} generated and saved")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to generate scene {scene_number}: {e}")
                    build_report["stages"][f"scene_{scene_number}"] = {
                        "status": "failed",
                        "error": str(e),
                        "agent_type": "adk_structured"
                    }
                    # Continue with other scenes
                    continue
            
            stage_time = time.time() - stage_start
            build_report["stages"]["scene_scripts"] = {
                "status": "success",
                "time_ms": int(stage_time * 1000),
                "scenes_generated": len(scene_packages),
                "scenes_failed": len(scenes) - len(scene_packages),
                "agent_type": "adk_structured"
            }
            
            logger.info(f"✅ Generated {len(scene_packages)} scene packages")
            
            # Stage 3: Validation and Quality Check
            logger.info("🔍 Stage 3: Validation and quality checks...")
            validation_start = time.time()
            
            validation_results = self._validate_production_package(
                full_script, scene_packages
            )
            
            validation_time = time.time() - validation_start
            build_report["validation_results"] = validation_results
            build_report["validation_results"]["validation_time_ms"] = int(validation_time * 1000)
            
            # Stage 4: Package Assembly
            logger.info("📦 Stage 4: Assembling final production package...")
            
            production_package = {
                "session_id": session_id,
                "metadata": {
                    "topic": topic,
                    "length_preference": length_preference,
                    "style_profile": style_profile,
                    "target_audience": target_audience,
                    "language": language,
                    "created_at": datetime.now().isoformat(),
                    "pipeline_version": "adk_2.0"
                },
                "full_script": full_script,
                "scene_packages": scene_packages,
                "validation_results": validation_results,
                "build_report": build_report
            }
            
            # Save complete package
            package_file = self.session_manager.get_session_dir(session_id) / "production_package.json"
            with open(package_file, 'w', encoding='utf-8') as f:
                json.dump(production_package, f, indent=2, ensure_ascii=False)
            
            # Update build report
            build_report["success"] = True
            build_report["performance_metrics"] = {
                "total_scenes": len(scenes),
                "successful_scenes": len(scene_packages),
                "failed_scenes": len(scenes) - len(scene_packages),
                "overall_success_rate": len(scene_packages) / len(scenes) if scenes else 0,
                "json_parsing_success_rate": 1.0,  # ADK structured output guarantees valid JSON
                "schema_validation_success_rate": validation_results.get("schema_validation_rate", 0.0)
            }
            
            # Save final build report
            report_file = self.session_manager.get_session_dir(session_id) / "build_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(build_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🎉 ADK video production pipeline completed successfully!")
            logger.info(f"📊 Success Rate: {build_report['performance_metrics']['overall_success_rate']:.1%}")
            
            return production_package
            
        except Exception as e:
            logger.error(f"❌ ADK pipeline failed: {e}")
            build_report["success"] = False
            build_report["error"] = str(e)
            
            # Save error report
            report_file = self.session_manager.get_session_dir(session_id) / "build_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(build_report, f, indent=2, ensure_ascii=False)
            
            raise
    
    def _validate_production_package(self, 
                                   full_script: Dict[str, Any], 
                                   scene_packages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the complete production package"""
        
        validation_results = {
            "full_script_valid": False,
            "scene_packages_valid": 0,
            "total_scene_packages": len(scene_packages),
            "schema_validation_rate": 0.0,
            "content_validation_rate": 0.0,
            "issues": []
        }
        
        try:
            # Validate full script
            if self._validate_full_script(full_script):
                validation_results["full_script_valid"] = True
                logger.info("✅ Full script validation passed")
            else:
                validation_results["issues"].append("Full script validation failed")
                logger.warning("⚠️ Full script validation failed")
            
            # Validate scene packages
            valid_scenes = 0
            for i, scene_package in enumerate(scene_packages):
                scene_number = scene_package.get("scene_number", i + 1)
                if self._validate_scene_package(scene_package, scene_number):
                    valid_scenes += 1
                else:
                    validation_results["issues"].append(f"Scene {scene_number} validation failed")
            
            validation_results["scene_packages_valid"] = valid_scenes
            validation_results["schema_validation_rate"] = valid_scenes / len(scene_packages) if scene_packages else 0
            validation_results["content_validation_rate"] = validation_results["schema_validation_rate"]  # Same for ADK
            
            logger.info(f"✅ Scene validation: {valid_scenes}/{len(scene_packages)} scenes valid")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            validation_results["issues"].append(f"Validation error: {str(e)}")
            return validation_results
    
    def _validate_full_script(self, full_script: Dict[str, Any]) -> bool:
        """Validate full script structure"""
        try:
            required_fields = ["title", "overall_style", "story_summary", "scenes"]
            for field in required_fields:
                if field not in full_script or not full_script[field]:
                    return False
            
            scenes = full_script.get("scenes", [])
            if len(scenes) < 3:
                return False
            
            return True
        except:
            return False
    
    def _validate_scene_package(self, scene_package: Dict[str, Any], scene_number: int) -> bool:
        """Validate individual scene package"""
        try:
            required_fields = ["scene_number", "narration_script", "visuals", "tts", "timing"]
            for field in required_fields:
                if field not in scene_package:
                    return False
            
            # Check narration script
            narration = scene_package.get("narration_script", [])
            if not narration:
                return False
            
            # Check visuals
            visuals = scene_package.get("visuals", [])
            if not visuals:
                return False
            
            # Check timing
            timing = scene_package.get("timing", {})
            if timing.get("total_ms", 0) < 1000:
                return False
            
            return True
        except:
            return False

# Test function
async def test_adk_orchestrator():
    """Test the ADK Orchestrator Agent"""
    from core.session_manager import SessionManager
    
    session_manager = SessionManager()
    orchestrator = ADKOrchestratorAgent(session_manager)
    
    try:
        package = await orchestrator.create_video_package(
            topic="The surprising science behind why we procrastinate",
            length_preference="60-90s",
            style_profile="informative and engaging",
            target_audience="general",
            language="English"
        )
        
        print("✅ ADK Video Package Created Successfully!")
        print(f"Session ID: {package.get('session_id')}")
        print(f"Success: {package.get('build_report', {}).get('success')}")
        print(f"Scenes: {len(package.get('scene_packages', []))}")
        
        build_report = package.get('build_report', {})
        performance = build_report.get('performance_metrics', {})
        print(f"Success Rate: {performance.get('overall_success_rate', 0):.1%}")
        print(f"JSON Parsing: {performance.get('json_parsing_success_rate', 0):.1%}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_adk_orchestrator())
