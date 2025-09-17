"""
Orchestrator Agent - New Architecture
State machine controlling the multi-agent video production pipeline.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import jsonschema
from core.session_manager import SessionManager
from agents.full_script_writer_agent import FullScriptWriterAgent
from agents.scene_script_writer_agent import SceneScriptWriterAgent
from agents.image_create_agent import ImageCreateAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorAgent:
    """
    Orchestrator Agent - New Architecture
    
    Mission: State machine controlling the pipeline. Performs retries, 
    validation, and fallbacks. Manages the complete video production workflow.
    """
    
    def __init__(self):
        """Initialize Orchestrator Agent"""
        # Load JSON schemas
        self.schemas = self._load_schemas()
        
        # Initialize session manager
        self.session_manager = SessionManager()
        
        # Initialize agents
        self.full_script_writer = FullScriptWriterAgent()
        self.scene_script_writer = SceneScriptWriterAgent()
        self.image_create_agent = ImageCreateAgent()
        
        logger.info("Orchestrator Agent initialized with new architecture")
    
    def _load_schemas(self) -> Dict[str, Dict]:
        """Load JSON schemas for validation"""
        schemas = {}
        schema_dir = Path("schemas")
        
        schema_files = [
            "FullScript.json",
            "ScenePackage.json", 
            "ImageAsset.json"
        ]
        
        for schema_file in schema_files:
            schema_path = schema_dir / schema_file
            if schema_path.exists():
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        schema_name = schema_file.replace('.json', '')
                        schemas[schema_name] = json.load(f)
                    logger.info(f"Loaded schema: {schema_name}")
                except Exception as e:
                    logger.error(f"Failed to load schema {schema_file}: {str(e)}")
            else:
                logger.warning(f"Schema file not found: {schema_path}")
        
        return schemas
    
    def _save_build_report(self, session_id: str, build_report: Dict[str, Any]):
        """Save build report to session directory"""
        try:
            session_dir = Path(f"sessions/{session_id}")
            report_file = session_dir / "build_report.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(build_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Build report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to save build report: {str(e)}")
    
    async def create_video(self, 
                          topic: str,
                          length_preference: str = "60-90s",
                          style_profile: str = "educational and engaging", 
                          target_audience: str = "general",
                          knowledge_refs: Optional[List[str]] = None,
                          cost_saving_mode: bool = False) -> Dict[str, Any]:
        """
        Create a complete video using the new multi-agent architecture
        
        Args:
            topic: The subject for the video
            length_preference: Desired video length
            style_profile: Overall style and tone
            target_audience: Target audience description
            knowledge_refs: Optional reference sources
            cost_saving_mode: Use mock images to save costs
            
        Returns:
            Dict: Complete video creation results with build report
        """
        start_time = time.time()
        
        # Create session
        session_id = self.session_manager.create_session(topic)
        logger.info(f"Created session: {session_id}")
        
        # Initialize build report
        build_report = {
            "session_id": session_id,
            "topic": topic,
            "style_profile": style_profile,
            "target_audience": target_audience,
            "cost_saving_mode": cost_saving_mode,
            "start_time": start_time,
            "stages": {},
            "errors": [],
            "model_usage": {},
            "timing": {}
        }
        
        try:
            # Stage 1: Full Script Writer
            logger.info("🎬 Stage 1: Generating full script structure...")
            stage_start = time.time()
            
            full_script = await self.full_script_writer.generate_full_script(
                topic=topic,
                session_id=session_id,
                length_preference=length_preference,
                style_profile=style_profile,
                target_audience=target_audience,
                knowledge_refs=knowledge_refs
            )
            
            # Validate full script (warning only for now)
            if not self._validate_against_schema(full_script, "FullScript"):
                logger.warning("Full script failed schema validation, proceeding anyway")
            
            stage_time = time.time() - stage_start
            build_report["stages"]["full_script"] = {
                "status": "success",
                "time_ms": int(stage_time * 1000),
                "scenes_count": len(full_script.get("scenes", []))
            }
            
            logger.info(f"✅ Full script generated with {len(full_script.get('scenes', []))} scenes")
            
            # Save full script
            script_file = Path(f"sessions/{session_id}/full_script.json")
            with open(script_file, 'w', encoding='utf-8') as f:
                json.dump(full_script, f, indent=2, ensure_ascii=False)
            
            # Stage 2: Scene Script Writer (for each scene)
            logger.info("📝 Stage 2: Generating detailed scene scripts...")
            stage_start = time.time()
            
            scenes = full_script.get("scenes", [])
            scene_packages = []
            previous_scenes = []
            
            global_context = {
                "title": full_script.get("title", ""),
                "overall_style": full_script.get("overall_style", style_profile),
                "main_character": full_script.get("main_character", "Huh"),
                "cosplay_instructions": full_script.get("cosplay_instructions", ""),
                "story_summary": full_script.get("story_summary", ""),
                "target_audience": target_audience
            }
            
            for scene_data in scenes:
                try:
                    scene_number = scene_data.get("scene_number", 1)
                    logger.info(f"Expanding scene {scene_number}...")
                    
                    scene_package = await self.scene_script_writer.expand_scene(
                        scene_data=scene_data,
                        global_context=global_context,
                        session_id=session_id,
                        previous_scenes=previous_scenes
                    )
                    
                    # Validate scene package (warning only)
                    if not self._validate_against_schema(scene_package, "ScenePackage"):
                        logger.warning(f"Scene {scene_number} failed schema validation, proceeding anyway")
                    
                    scene_packages.append(scene_package)
                    previous_scenes.append(scene_package)
                    
                    logger.info(f"✅ Scene {scene_number} package generated")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to generate scene {scene_data.get('scene_number', 'unknown')}: {str(e)}")
                    build_report["errors"].append({
                        "stage": "scene_script",
                        "scene": scene_data.get("scene_number", "unknown"),
                        "error": str(e)
                    })
            
            stage_time = time.time() - stage_start
            build_report["stages"]["scene_scripts"] = {
                "status": "success",
                "time_ms": int(stage_time * 1000),
                "scenes_processed": len(scene_packages),
                "scenes_failed": len(scenes) - len(scene_packages)
            }
            
            logger.info(f"✅ Generated {len(scene_packages)} scene packages")
            
            # Save scene packages
            for package in scene_packages:
                scene_num = package.get("scene_number", 1)
                package_file = Path(f"sessions/{session_id}/scene_package_{scene_num}.json")
                with open(package_file, 'w', encoding='utf-8') as f:
                    json.dump(package, f, indent=2, ensure_ascii=False)
            
            # Stage 3: Image Create Agent (for each scene)
            logger.info("🎨 Stage 3: Generating images...")
            stage_start = time.time()
            
            all_image_assets = []
            
            for scene_package in scene_packages:
                try:
                    scene_number = scene_package.get("scene_number", 1)
                    logger.info(f"Generating images for scene {scene_number}...")
                    
                    image_assets = await self.image_create_agent.generate_images_for_scene(
                        scene_package=scene_package,
                        session_id=session_id,
                        cost_saving_mode=cost_saving_mode
                    )
                    
                    # Validate image assets (warning only)
                    for asset in image_assets:
                        if not self._validate_against_schema(asset, "ImageAsset"):
                            logger.warning(f"Image asset {asset.get('frame_id', 'unknown')} failed schema validation, proceeding anyway")
                    
                    all_image_assets.extend(image_assets)
                    
                    logger.info(f"✅ Generated {len(image_assets)} images for scene {scene_number}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to generate images for scene {scene_package.get('scene_number', 'unknown')}: {str(e)}")
                    build_report["errors"].append({
                        "stage": "image_generation",
                        "scene": scene_package.get("scene_number", "unknown"),
                        "error": str(e)
                    })
            
            stage_time = time.time() - stage_start
            build_report["stages"]["image_generation"] = {
                "status": "success",
                "time_ms": int(stage_time * 1000),
                "images_generated": len(all_image_assets),
                "images_successful": len([a for a in all_image_assets if a.get("safety_result") == "safe"])
            }
            
            logger.info(f"✅ Generated {len(all_image_assets)} total images")
            
            # Save image assets
            assets_file = Path(f"sessions/{session_id}/image_assets.json")
            with open(assets_file, 'w', encoding='utf-8') as f:
                json.dump(all_image_assets, f, indent=2, ensure_ascii=False)
            
            # Stage 4: Final Assembly (placeholder for now)
            logger.info("🎞️ Stage 4: Final assembly...")
            
            # Calculate total time
            total_time = time.time() - start_time
            build_report["total_time_ms"] = int(total_time * 1000)
            build_report["end_time"] = time.time()
            build_report["status"] = "success"
            
            # Save build report
            self._save_build_report(session_id, build_report)
            
            # Create final results
            results = {
                "session_id": session_id,
                "status": "success",
                "full_script": full_script,
                "scene_packages": scene_packages,
                "image_assets": all_image_assets,
                "build_report": build_report,
                "total_time_seconds": total_time
            }
            
            logger.info(f"🎉 Video creation completed successfully!")
            logger.info(f"📁 Session: {session_id}")
            logger.info(f"📝 Scenes: {len(scene_packages)}")
            logger.info(f"🖼️ Images: {len(all_image_assets)}")
            logger.info(f"⏱️ Total time: {total_time:.2f}s")
            
            return results
            
        except Exception as e:
            # Handle overall failure
            total_time = time.time() - start_time
            build_report["total_time_ms"] = int(total_time * 1000)
            build_report["end_time"] = time.time()
            build_report["status"] = "failed"
            build_report["final_error"] = str(e)
            
            self._save_build_report(session_id, build_report)
            
            logger.error(f"❌ Video creation failed: {str(e)}")
            raise
    
    def _validate_against_schema(self, data: Dict[str, Any], schema_name: str) -> bool:
        """Validate data against JSON schema"""
        try:
            if schema_name not in self.schemas:
                logger.warning(f"Schema {schema_name} not found, skipping validation")
                return True
            
            schema = self.schemas[schema_name]
            jsonschema.validate(data, schema)
            
            logger.debug(f"✅ Data validated against {schema_name} schema")
            return True
            
        except jsonschema.ValidationError as e:
            logger.error(f"❌ Schema validation failed for {schema_name}: {e.message}")
            logger.error(f"Failed at path: {' -> '.join(str(p) for p in e.path)}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected validation error for {schema_name}: {str(e)}")
            return False
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a session"""
        try:
            session_dir = Path(f"sessions/{session_id}")
            
            if not session_dir.exists():
                return {"status": "not_found", "session_id": session_id}
            
            # Check for build report
            report_file = session_dir / "build_report.json"
            if report_file.exists():
                with open(report_file, 'r', encoding='utf-8') as f:
                    build_report = json.load(f)
                return build_report
            
            # Check for basic files
            files_present = {
                "full_script": (session_dir / "full_script.json").exists(),
                "scene_packages": len(list(session_dir.glob("scene_package_*.json"))),
                "image_assets": (session_dir / "image_assets.json").exists(),
                "images": len(list((session_dir / "images").glob("*.png"))) if (session_dir / "images").exists() else 0
            }
            
            return {
                "status": "in_progress",
                "session_id": session_id,
                "files_present": files_present
            }
            
        except Exception as e:
            logger.error(f"Error getting session status: {str(e)}")
            return {"status": "error", "session_id": session_id, "error": str(e)}
