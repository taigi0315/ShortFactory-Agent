"""
ADK Scene Script Validator Agent

This agent validates individual scene quality and smooth connections between scenes.
It checks scene quality, visual potential, informative density, character utilization, and smooth connections.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from google.adk import Agent
from pydantic import BaseModel, Field

from model.models import (
    Scene, SceneValidationResult, SceneValidationSummary, ValidationStatus, 
    ValidationSeverity, ValidationIssue, WorkflowState, SceneState
)
from core.shared_context import SharedContextManager, SharedContext
from core.scene_continuity_manager import SceneContinuityManager

logger = logging.getLogger(__name__)

class SceneValidationTool:
    """Tool for validating scene scripts"""
    
    def __init__(self, continuity_manager: SceneContinuityManager = None):
        self.name = "scene_validator"
        self.description = "Validates individual scene quality and smooth connections"
        self._continuity_manager = continuity_manager or SceneContinuityManager()
    
    async def validate_all_scenes(self, scenes: List[Dict[str, Any]], 
                                shared_context: Optional[SharedContext] = None) -> SceneValidationSummary:
        """
        Validate all scenes and their connections
        
        Args:
            scenes: List of scene data dictionaries
            shared_context: Shared context for consistency
            
        Returns:
            SceneValidationSummary: Summary of all scene validations
        """
        try:
            logger.info(f"Validating {len(scenes)} scenes")
            
            scene_results = []
            passed_scenes = 0
            failed_scenes = 0
            revision_scenes = []
            
            # Validate each scene individually
            for scene_data in scenes:
                result = await self._validate_single_scene(scene_data, shared_context)
                scene_results.append(result)
                
                if result.status == ValidationStatus.PASS:
                    passed_scenes += 1
                else:
                    failed_scenes += 1
                    revision_scenes.append(result.scene_number)
            
            # Assess overall scene connections
            connection_score = self._assess_scene_connections(scenes)
            
            # Determine if revision is needed
            needs_revision = failed_scenes > 0 or connection_score < 0.7
            
            summary = SceneValidationSummary(
                total_scenes=len(scenes),
                passed_scenes=passed_scenes,
                failed_scenes=failed_scenes,
                overall_connection_score=connection_score,
                scene_results=scene_results,
                needs_revision=needs_revision,
                revision_scenes=revision_scenes
            )
            
            logger.info(f"Scene validation complete: {passed_scenes}/{len(scenes)} passed, connection score: {connection_score:.2f}")
            return summary
            
        except Exception as e:
            logger.error(f"Error validating scenes: {str(e)}")
            # Return a default validation summary
            return SceneValidationSummary(
                total_scenes=len(scenes),
                passed_scenes=len(scenes),
                failed_scenes=0,
                overall_connection_score=0.8,
                scene_results=[],
                needs_revision=False
            )
    
    async def _validate_single_scene(self, scene_data: Dict[str, Any], 
                                   shared_context: Optional[SharedContext] = None) -> SceneValidationResult:
        """Validate a single scene"""
        scene_number = scene_data.get('scene_number', 1)
        
        # Calculate individual scores
        scene_quality_score = self._assess_scene_quality(scene_data)
        visual_potential_score = self._assess_visual_potential(scene_data)
        informative_density_score = self._assess_informative_density(scene_data)
        character_utilization_score = self._assess_character_utilization(scene_data)
        connection_score = self._assess_scene_connection(scene_data, shared_context)
        
        # Calculate overall score
        overall_score = (scene_quality_score + visual_potential_score + 
                        informative_density_score + character_utilization_score + 
                        connection_score) / 5.0
        
        # Generate issues and feedback
        issues = self._generate_scene_validation_issues(
            scene_data, scene_quality_score, visual_potential_score, 
            informative_density_score, character_utilization_score, connection_score
        )
        
        # Determine status
        status = ValidationStatus.PASS if overall_score >= 0.7 else ValidationStatus.REVISE
        
        # Generate feedback
        feedback = self._generate_scene_feedback(scene_data, issues, overall_score)
        
        # Generate revision instructions if needed
        revision_instructions = None
        if status == ValidationStatus.REVISE:
            revision_instructions = self._generate_scene_revision_instructions(issues)
        
        return SceneValidationResult(
            status=status,
            overall_score=overall_score,
            scene_number=scene_number,
            scene_quality_score=scene_quality_score,
            visual_potential_score=visual_potential_score,
            informative_density_score=informative_density_score,
            character_utilization_score=character_utilization_score,
            connection_score=connection_score,
            issues=issues,
            feedback=feedback,
            revision_instructions=revision_instructions
        )
    
    def _assess_scene_quality(self, scene_data: Dict[str, Any]) -> float:
        """Assess the overall quality of the scene"""
        score = 0.5  # Base score
        
        # Check dialogue quality
        dialogue = scene_data.get('dialogue', '')
        if len(dialogue.split()) > 10:  # Sufficient dialogue length
            score += 0.1
        
        # Check for engaging elements
        dialogue_lower = dialogue.lower()
        engaging_words = ['amazing', 'incredible', 'surprising', 'fascinating', 'shocking']
        for word in engaging_words:
            if word in dialogue_lower:
                score += 0.05
        
        # Check scene purpose clarity
        scene_purpose = scene_data.get('scene_purpose', '')
        if scene_purpose and len(scene_purpose.split()) > 5:
            score += 0.1
        
        # Check for specific details
        if any(char.isdigit() for char in dialogue):
            score += 0.1  # Numbers indicate specific facts
        
        return min(1.0, score)
    
    def _assess_visual_potential(self, scene_data: Dict[str, Any]) -> float:
        """Assess how well the scene can be visualized"""
        score = 0.5  # Base score
        
        # Check image create prompt
        image_prompt = scene_data.get('image_create_prompt', '')
        if len(image_prompt.split()) > 20:  # Sufficient detail
            score += 0.2
        
        # Check for visual elements
        visual_elements = scene_data.get('visual_elements', {})
        if visual_elements:
            if visual_elements.get('primary_focus'):
                score += 0.1
            if visual_elements.get('secondary_elements'):
                score += 0.1
            if visual_elements.get('color_scheme'):
                score += 0.05
        
        # Check for specific visual descriptions
        visual_keywords = ['showing', 'displaying', 'illustrating', 'demonstrating', 'visualizing']
        for keyword in visual_keywords:
            if keyword in image_prompt.lower():
                score += 0.05
        
        return min(1.0, score)
    
    def _assess_informative_density(self, scene_data: Dict[str, Any]) -> float:
        """Assess the informative content density"""
        score = 0.5  # Base score
        
        # Check informative content
        informative_content = scene_data.get('informative_content', {})
        if informative_content:
            # Count informative elements
            elements_count = 0
            for key in ['key_concepts', 'specific_facts', 'examples', 'statistics']:
                if informative_content.get(key):
                    elements_count += len(informative_content[key])
            
            if elements_count > 0:
                score += min(0.4, elements_count * 0.05)  # Up to 0.4 for informative elements
        
        # Check dialogue for informative value
        dialogue = scene_data.get('dialogue', '')
        informative_words = ['learn', 'understand', 'explain', 'teach', 'show', 'demonstrate']
        for word in informative_words:
            if word in dialogue.lower():
                score += 0.05
        
        return min(1.0, score)
    
    def _assess_character_utilization(self, scene_data: Dict[str, Any]) -> float:
        """Assess how well the character is utilized"""
        score = 0.5  # Base score
        
        # Check character pose and expression
        character_pose = scene_data.get('character_pose', '')
        character_expression = scene_data.get('character_expression', '')
        
        if character_pose and character_pose != 'standing':
            score += 0.1
        
        if character_expression and character_expression != 'neutral':
            score += 0.1
        
        # Check if character is mentioned in image prompt
        image_prompt = scene_data.get('image_create_prompt', '')
        if 'character' in image_prompt.lower():
            score += 0.1
        
        # Check for character interaction
        dialogue = scene_data.get('dialogue', '')
        if len(dialogue) > 20:  # Character has substantial dialogue
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_scene_connection(self, scene_data: Dict[str, Any], 
                               shared_context: Optional[SharedContext] = None) -> float:
        """Assess how well the scene connects with others"""
        score = 0.5  # Base score
        
        # Check story context
        story_context = scene_data.get('story_context', {})
        if story_context:
            if story_context.get('connection_to_previous'):
                score += 0.1
            if story_context.get('setup_for_next'):
                score += 0.1
        
        # Check scene type appropriateness
        scene_type = scene_data.get('scene_type', '')
        scene_number = scene_data.get('scene_number', 1)
        
        # First scene should be hook
        if scene_number == 1 and 'hook' in scene_type.lower():
            score += 0.1
        
        # Check for transition elements
        transition = scene_data.get('transition_to_next', '')
        if transition and transition != 'none':
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_scene_connections(self, scenes: List[Dict[str, Any]]) -> float:
        """Assess overall scene connections and flow"""
        if len(scenes) < 2:
            return 1.0  # Single scene is always connected
        
        total_score = 0.0
        connection_count = 0
        
        for i in range(len(scenes) - 1):
            current_scene = scenes[i]
            next_scene = scenes[i + 1]
            
            # Check logical progression
            current_type = current_scene.get('scene_type', '')
            next_type = next_scene.get('scene_type', '')
            
            # Good progressions
            good_progressions = [
                ('hook', 'explanation'),
                ('explanation', 'example'),
                ('example', 'statistic'),
                ('statistic', 'call_to_action'),
                ('call_to_action', 'summary')
            ]
            
            if (current_type, next_type) in good_progressions:
                total_score += 1.0
            else:
                total_score += 0.5  # Neutral progression
            
            connection_count += 1
        
        return total_score / connection_count if connection_count > 0 else 1.0
    
    def _generate_scene_validation_issues(self, scene_data: Dict[str, Any], 
                                        scene_quality_score: float, visual_potential_score: float, 
                                        informative_density_score: float, character_utilization_score: float, 
                                        connection_score: float) -> List[ValidationIssue]:
        """Generate validation issues for a scene"""
        issues = []
        
        if scene_quality_score < 0.6:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.MEDIUM,
                category="scene_quality",
                description="Scene lacks engaging content or sufficient detail",
                suggestion="Enhance dialogue with more engaging elements and specific details"
            ))
        
        if visual_potential_score < 0.6:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.MEDIUM,
                category="visual_potential",
                description="Scene lacks sufficient visual elements for image generation",
                suggestion="Add more specific visual descriptions and elements to the image prompt"
            ))
        
        if informative_density_score < 0.6:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.HIGH,
                category="informative_density",
                description="Scene lacks sufficient informative content",
                suggestion="Add more key concepts, facts, examples, or statistics"
            ))
        
        if character_utilization_score < 0.6:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.MEDIUM,
                category="character_utilization",
                description="Character is not effectively utilized in the scene",
                suggestion="Enhance character pose, expression, and interaction with content"
            ))
        
        if connection_score < 0.6:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.MEDIUM,
                category="scene_connection",
                description="Scene doesn't connect well with other scenes",
                suggestion="Improve story context and transition elements"
            ))
        
        return issues
    
    def _generate_scene_feedback(self, scene_data: Dict[str, Any], 
                               issues: List[ValidationIssue], overall_score: float) -> str:
        """Generate feedback for a scene"""
        scene_number = scene_data.get('scene_number', 1)
        
        if overall_score >= 0.7:
            return f"Scene {scene_number} looks good! Score: {overall_score:.2f}. Ready for image generation."
        
        feedback = f"Scene {scene_number} needs improvement (score: {overall_score:.2f}). "
        
        if issues:
            feedback += "Key areas for improvement:\n"
            for issue in issues:
                feedback += f"- {issue.category}: {issue.suggestion}\n"
        
        return feedback.strip()
    
    def _generate_scene_revision_instructions(self, issues: List[ValidationIssue]) -> str:
        """Generate revision instructions for a scene"""
        if not issues:
            return "No specific revisions needed."
        
        instructions = "Please revise this scene with the following improvements:\n\n"
        
        for issue in issues:
            instructions += f"**{issue.category.replace('_', ' ').title()}**: {issue.suggestion}\n"
        
        instructions += "\nFocus on making the scene more engaging, informative, and visually appealing."
        return instructions

class ADKSceneScriptValidatorAgent(Agent):
    """
    ADK-based Scene Script Validator Agent
    
    This agent validates individual scene quality and smooth connections
    """
    
    def __init__(self, shared_context_manager: SharedContextManager = None, 
                 continuity_manager: SceneContinuityManager = None):
        """
        Initialize ADK Scene Script Validator Agent
        
        Args:
            shared_context_manager: SharedContextManager for maintaining consistency
            continuity_manager: SceneContinuityManager for scene continuity
        """
        # Check if API key is available
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        # Create validation tool
        validation_tool = SceneValidationTool(continuity_manager)
        
        # Initialize ADK Agent
        super().__init__(
            name="scene_script_validator",
            description="Validates individual scene quality and smooth connections",
            model="gemini-2.5-flash",
            instruction=self._get_instruction(),
            generate_content_config={
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 4096,
                "response_mime_type": "application/json"
            }
        )
        
        # Store references
        self._shared_context_manager = shared_context_manager or SharedContextManager()
        self._continuity_manager = continuity_manager or SceneContinuityManager()
        self._validation_tool = validation_tool
        
        logger.info("ADK Scene Script Validator Agent initialized with Gemini 2.5 Flash")
    
    def _get_instruction(self) -> str:
        """Get the instruction for the scene script validator agent"""
        return """
You are a STRICT Scene Script Validator Agent responsible for rejecting mediocre scenes and demanding informative excellence.

## STRICT VALIDATION CRITERIA:

### 1. FACT DENSITY TEST (Fail if < 3 specific facts):
- Count specific numbers, dates, names
- Verify each fact has supporting detail
- Ensure variety in fact types
- Penalize generic statements

### 2. VISUAL INFORMATIVE VALUE (Fail if not screenshot-worthy):
- Can someone learn from a screenshot?
- Are there specific data visualizations?
- Is the information clearly presented?
- Would this visual go viral on its own?

### 3. DIALOGUE QUALITY (Fail if generic):
- No "Let me explain..." phrases
- Must start with surprising fact
- Include specific numbers/names
- Show genuine reactions

### 4. INFORMATIVE IMPACT (Fail if not memorable):
- Would viewer remember 3 facts?
- Is there clear learning outcome?
- Are concepts explained through examples?
- Does it build on previous scenes?

### 5. CHARACTER UTILIZATION (Fail if distracting):
- Character must add value, not distract
- Should react to information
- Must be small in frame
- Should guide, not dominate

## REJECTION CRITERIA:
- Generic informative filler
- Lack of specific data points
- No visual informative value
- Character dominates the frame
- No clear learning outcome

## Output Format:
Return a JSON object with:
- total_scenes: number of scenes validated
- passed_scenes: number of scenes that passed
- failed_scenes: number of scenes that need revision
- overall_connection_score: float (0.0 to 1.0)
- scene_results: array of individual scene validation results
- needs_revision: boolean indicating if any scenes need revision
- revision_scenes: array of scene numbers that need revision

## Quality Standards:
- PASS: Overall score >= 0.8, all criteria >= 0.7
- REVISE: Overall score < 0.8 or any criterion < 0.7

Be merciless in rejecting generic content. Demand informative excellence.
"""
    
    async def validate_all_scenes(self, scenes: List[Dict[str, Any]], 
                                shared_context: Optional[SharedContext] = None) -> SceneValidationSummary:
        """
        Validate all scenes and their connections
        
        Args:
            scenes: List of scene data dictionaries
            shared_context: Shared context for consistency
            
        Returns:
            SceneValidationSummary: Summary of all scene validations
        """
        try:
            logger.info(f"Validating {len(scenes)} scenes")
            
            # Use the validation tool
            result = await self._validation_tool.validate_all_scenes(scenes, shared_context)
            
            logger.info(f"Scene validation complete: {result.passed_scenes}/{result.total_scenes} passed")
            return result
            
        except Exception as e:
            logger.error(f"Error validating scenes: {str(e)}")
            # Return a default validation summary
            return SceneValidationSummary(
                total_scenes=len(scenes),
                passed_scenes=len(scenes),
                failed_scenes=0,
                overall_connection_score=0.8,
                scene_results=[],
                needs_revision=False
            )

# Test function
async def test_scene_script_validator():
    """Test the Scene Script Validator Agent"""
    try:
        agent = ADKSceneScriptValidatorAgent()
        
        # Create test scene data
        test_scenes = [
            {
                "scene_number": 1,
                "scene_type": "hook",
                "dialogue": "Did you know that Texas was once its own independent country?",
                "image_create_prompt": "Informative infographic showing Texas independence",
                "character_pose": "pointing",
                "character_expression": "excited",
                "informative_content": {
                    "key_concepts": ["Texas independence"],
                    "specific_facts": ["Texas was independent from 1836-1845"],
                    "examples": ["Republic of Texas"],
                    "statistics": ["9 years of independence"]
                },
                "visual_elements": {
                    "primary_focus": "Texas independence",
                    "secondary_elements": ["Lone Star flag"],
                    "color_scheme": "red, white, blue",
                    "lighting": "bright"
                }
            }
        ]
        
        result = await agent.validate_all_scenes(test_scenes)
        
        print(f"✅ Scene validation complete: {result.passed_scenes}/{result.total_scenes} passed")
        print(f"📊 Connection score: {result.overall_connection_score:.2f}")
        print(f"🔄 Needs revision: {result.needs_revision}")
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_scene_script_validator())
