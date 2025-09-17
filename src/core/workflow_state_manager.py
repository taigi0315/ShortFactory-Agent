"""
Workflow State Manager

Manages the state of the video creation workflow, including script validation,
scene generation, and revision tracking.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from model.models import (
    WorkflowState, ScriptState, SceneState, ValidationResult, 
    ScriptValidationResult, SceneValidationSummary
)

logger = logging.getLogger(__name__)

class WorkflowStateManager:
    """
    Manages the overall workflow state and tracks progress through the validation system
    """
    
    def __init__(self, session_id: str):
        """
        Initialize Workflow State Manager
        
        Args:
            session_id: Unique identifier for the session
        """
        self.session_id = session_id
        self._state = WorkflowState(
            session_id=session_id,
            current_stage="script_generation",
            script_state=ScriptState.DRAFT
        )
        logger.info(f"WorkflowStateManager initialized for session: {session_id}")
    
    def get_state(self) -> WorkflowState:
        """Get current workflow state"""
        return self._state
    
    def update_stage(self, stage: str) -> None:
        """Update current workflow stage"""
        self._state.current_stage = stage
        self._state.updated_at = datetime.now()
        logger.info(f"Workflow stage updated to: {stage}")
    
    def update_script_state(self, state: ScriptState) -> None:
        """Update script state"""
        self._state.script_state = state
        self._state.updated_at = datetime.now()
        logger.info(f"Script state updated to: {state.value}")
    
    def update_scene_state(self, scene_number: int, state: SceneState) -> None:
        """Update individual scene state"""
        self._state.scene_states[scene_number] = state
        self._state.updated_at = datetime.now()
        logger.info(f"Scene {scene_number} state updated to: {state.value}")
    
    def add_validation_result(self, validation_result: ValidationResult) -> None:
        """Add validation result to history"""
        self._state.validation_history.append(validation_result)
        self._state.updated_at = datetime.now()
        logger.info(f"Validation result added: {validation_result.status.value}")
    
    def add_revision_record(self, revision_type: str, details: Dict[str, Any]) -> None:
        """Add revision record to history"""
        revision_record = {
            "timestamp": datetime.now().isoformat(),
            "type": revision_type,
            "details": details
        }
        self._state.revision_history.append(revision_record)
        self._state.updated_at = datetime.now()
        logger.info(f"Revision record added: {revision_type}")
    
    def can_revise_script(self) -> bool:
        """Check if script can be revised (not at limit)"""
        script_revisions = len([r for r in self._state.revision_history 
                               if r.get("type") == "script_revision"])
        return script_revisions < 3  # Max 3 revisions
    
    def can_revise_scene(self, scene_number: int) -> bool:
        """Check if specific scene can be revised (not at limit)"""
        scene_revisions = len([r for r in self._state.revision_history 
                              if r.get("type") == "scene_revision" and 
                              r.get("details", {}).get("scene_number") == scene_number])
        return scene_revisions < 3  # Max 3 revisions per scene
    
    def get_revision_count(self, revision_type: str, scene_number: Optional[int] = None) -> int:
        """Get revision count for specific type and scene"""
        if revision_type == "script_revision":
            return len([r for r in self._state.revision_history 
                       if r.get("type") == "script_revision"])
        elif revision_type == "scene_revision" and scene_number is not None:
            return len([r for r in self._state.revision_history 
                       if r.get("type") == "scene_revision" and 
                       r.get("details", {}).get("scene_number") == scene_number])
        return 0
    
    def is_workflow_complete(self) -> bool:
        """Check if workflow is complete (all scenes approved)"""
        if self._state.script_state != ScriptState.APPROVED:
            return False
        
        # Check if all scenes are approved
        for scene_number, scene_state in self._state.scene_states.items():
            if scene_state != SceneState.APPROVED:
                return False
        
        return True
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get comprehensive workflow summary"""
        return {
            "session_id": self._state.session_id,
            "current_stage": self._state.current_stage,
            "script_state": self._state.script_state.value,
            "scene_states": {str(k): v.value for k, v in self._state.scene_states.items()},
            "total_validations": len(self._state.validation_history),
            "total_revisions": len(self._state.revision_history),
            "is_complete": self.is_workflow_complete(),
            "created_at": self._state.created_at.isoformat(),
            "updated_at": self._state.updated_at.isoformat()
        }
    
    def reset_workflow(self) -> None:
        """Reset workflow to initial state"""
        self._state = WorkflowState(
            session_id=self.session_id,
            current_stage="script_generation",
            script_state=ScriptState.DRAFT
        )
        logger.info(f"Workflow reset for session: {self.session_id}")

class ValidationWorkflowOrchestrator:
    """
    Orchestrates the 2-stage validation workflow
    """
    
    def __init__(self, session_id: str):
        """
        Initialize Validation Workflow Orchestrator
        
        Args:
            session_id: Unique identifier for the session
        """
        self.session_id = session_id
        self._state_manager = WorkflowStateManager(session_id)
        logger.info(f"ValidationWorkflowOrchestrator initialized for session: {session_id}")
    
    async def execute_script_validation_workflow(self, story_script, script_validator, 
                                               script_writer, max_revisions: int = 3) -> ScriptValidationResult:
        """
        Execute script validation workflow with revision loop
        
        Args:
            story_script: The story script to validate
            script_validator: Script validator agent
            script_writer: Script writer agent
            max_revisions: Maximum number of revisions allowed
            
        Returns:
            ScriptValidationResult: Final validation result
        """
        logger.info("Starting script validation workflow")
        
        revision_count = 0
        current_script = story_script
        
        while revision_count <= max_revisions:
            # Update workflow state
            self._state_manager.update_stage("script_validation")
            self._state_manager.update_script_state(ScriptState.UNDER_REVIEW)
            
            # Validate script
            validation_result = await script_validator.validate_story_script(current_script)
            self._state_manager.add_validation_result(validation_result)
            
            if validation_result.status.value == "pass":
                # Script passed validation
                self._state_manager.update_script_state(ScriptState.APPROVED)
                logger.info(f"Script validation passed after {revision_count} revisions")
                return validation_result
            
            elif revision_count < max_revisions:
                # Script needs revision
                self._state_manager.update_script_state(ScriptState.NEEDS_REVISION)
                self._state_manager.add_revision_record("script_revision", {
                    "revision_count": revision_count + 1,
                    "validation_result": validation_result.dict()
                })
                
                logger.info(f"Script validation failed, attempting revision {revision_count + 1}")
                
                # Generate revised script (this would call the script writer with feedback)
                # For now, we'll simulate this
                current_script = await self._simulate_script_revision(current_script, validation_result)
                revision_count += 1
            else:
                # Max revisions reached
                self._state_manager.update_script_state(ScriptState.REVISION_LIMIT_REACHED)
                logger.warning(f"Script validation failed after {max_revisions} revisions")
                return validation_result
        
        return validation_result
    
    async def execute_scene_validation_workflow(self, scenes: List[Dict[str, Any]], 
                                              scene_validator, scene_writer, 
                                              max_revisions: int = 3) -> SceneValidationSummary:
        """
        Execute scene validation workflow with revision loop
        
        Args:
            scenes: List of scene data dictionaries
            scene_validator: Scene validator agent
            scene_writer: Scene writer agent
            max_revisions: Maximum number of revisions allowed per scene
            
        Returns:
            SceneValidationSummary: Final validation summary
        """
        logger.info("Starting scene validation workflow")
        
        current_scenes = scenes.copy()
        revision_count = 0
        max_total_revisions = max_revisions * len(scenes)  # Max revisions per scene * number of scenes
        
        while revision_count < max_total_revisions:
            # Update workflow state
            self._state_manager.update_stage("scene_validation")
            
            # Validate all scenes
            validation_summary = await scene_validator.validate_all_scenes(current_scenes)
            self._state_manager.add_validation_result(validation_summary)
            
            if not validation_summary.needs_revision:
                # All scenes passed validation
                for scene_number in range(1, len(current_scenes) + 1):
                    self._state_manager.update_scene_state(scene_number, SceneState.APPROVED)
                logger.info(f"Scene validation passed after {revision_count} revisions")
                return validation_summary
            
            # Revise failed scenes
            revised_scenes = []
            scenes_revised = 0
            
            for scene_number in validation_summary.revision_scenes:
                if self._state_manager.can_revise_scene(scene_number):
                    # Find the scene data
                    scene_data = next((s for s in current_scenes if s.get('scene_number') == scene_number), None)
                    if scene_data:
                        # Generate revised scene (this would call the scene writer with feedback)
                        revised_scene = await self._simulate_scene_revision(scene_number, scene_data, validation_summary)
                        revised_scenes.append(revised_scene)
                        scenes_revised += 1
                        
                        self._state_manager.add_revision_record("scene_revision", {
                            "scene_number": scene_number,
                            "revision_count": self._state_manager.get_revision_count("scene_revision", scene_number) + 1
                        })
                else:
                    # Scene has reached revision limit
                    self._state_manager.update_scene_state(scene_number, SceneState.REVISION_LIMIT_REACHED)
                    logger.warning(f"Scene {scene_number} reached revision limit")
            
            if scenes_revised == 0:
                # No more scenes can be revised
                logger.warning("No more scenes can be revised")
                break
            
            # Update current scenes with revised ones
            for revised_scene in revised_scenes:
                scene_number = revised_scene.get('scene_number')
                current_scenes = [s if s.get('scene_number') != scene_number else revised_scene 
                                for s in current_scenes]
            
            revision_count += scenes_revised
            logger.info(f"Revised {scenes_revised} scenes, total revisions: {revision_count}")
        
        return validation_summary
    
    async def _simulate_script_revision(self, current_script, validation_result: ScriptValidationResult):
        """Simulate script revision (placeholder for actual implementation)"""
        logger.info("Simulating script revision based on validation feedback")
        # In real implementation, this would call the script writer with feedback
        return current_script
    
    async def _simulate_scene_revision(self, scene_number: int, scene_data: Dict[str, Any], 
                                     validation_summary: SceneValidationSummary):
        """Simulate scene revision (placeholder for actual implementation)"""
        logger.info(f"Simulating scene {scene_number} revision based on validation feedback")
        # In real implementation, this would call the scene writer with feedback
        return scene_data
    
    def get_workflow_state(self) -> WorkflowState:
        """Get current workflow state"""
        return self._state_manager.get_state()
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get workflow summary"""
        return self._state_manager.get_workflow_summary()

# Test function
async def test_workflow_state_manager():
    """Test the Workflow State Manager"""
    try:
        orchestrator = ValidationWorkflowOrchestrator("test_session_123")
        
        # Test workflow summary
        summary = orchestrator.get_workflow_summary()
        print(f"✅ Workflow State Manager initialized")
        print(f"📊 Session ID: {summary['session_id']}")
        print(f"🎯 Current Stage: {summary['current_stage']}")
        print(f"📝 Script State: {summary['script_state']}")
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_workflow_state_manager())
