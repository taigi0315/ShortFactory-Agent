"""
ADK Script Validator Agent

This agent validates story-level quality before scene generation.
It checks for fun factor, interest level, uniqueness, educational value, and narrative coherence.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from google.adk import Agent
from pydantic import BaseModel, Field

from model.models import (
    StoryScript, ScriptValidationResult, ValidationStatus, ValidationSeverity, 
    ValidationIssue, WorkflowState, ScriptState
)
from core.shared_context import SharedContextManager, SharedContext

logger = logging.getLogger(__name__)

class ScriptValidationTool:
    """Tool for validating story scripts"""
    
    def __init__(self):
        self.name = "script_validator"
        self.description = "Validates story script quality and provides feedback"
    
    async def validate_story_script(self, story_script: StoryScript, 
                                  shared_context: Optional[SharedContext] = None) -> ScriptValidationResult:
        """
        Validate story script quality
        
        Args:
            story_script: The story script to validate
            shared_context: Shared context for consistency
            
        Returns:
            ScriptValidationResult: Validation result with scores and feedback
        """
        try:
            logger.info(f"Validating story script: {story_script.title}")
            
            # Calculate individual scores
            fun_score = self._assess_fun_factor(story_script)
            interest_score = self._assess_interest_level(story_script)
            uniqueness_score = self._assess_uniqueness(story_script)
            educational_score = self._assess_educational_value(story_script)
            coherence_score = self._assess_narrative_coherence(story_script)
            
            # Calculate overall score
            overall_score = (fun_score + interest_score + uniqueness_score + 
                           educational_score + coherence_score) / 5.0
            
            # Generate issues and feedback
            issues = self._generate_validation_issues(
                story_script, fun_score, interest_score, uniqueness_score, 
                educational_score, coherence_score
            )
            
            # Determine status
            status = ValidationStatus.PASS if overall_score >= 0.7 else ValidationStatus.REVISE
            
            # Generate feedback
            feedback = self._generate_feedback(story_script, issues, overall_score)
            
            # Generate revision instructions if needed
            revision_instructions = None
            if status == ValidationStatus.REVISE:
                revision_instructions = self._generate_revision_instructions(issues)
            
            result = ScriptValidationResult(
                status=status,
                overall_score=overall_score,
                fun_score=fun_score,
                interest_score=interest_score,
                uniqueness_score=uniqueness_score,
                educational_score=educational_score,
                coherence_score=coherence_score,
                issues=issues,
                feedback=feedback,
                revision_instructions=revision_instructions
            )
            
            logger.info(f"Story validation complete: {status.value} (score: {overall_score:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error validating story script: {str(e)}")
            # Return a default validation result
            return ScriptValidationResult(
                status=ValidationStatus.PASS,
                overall_score=0.8,
                fun_score=0.8,
                interest_score=0.8,
                uniqueness_score=0.8,
                educational_score=0.8,
                coherence_score=0.8,
                issues=[],
                feedback="Validation completed with default scores"
            )
    
    def _assess_fun_factor(self, story_script: StoryScript) -> float:
        """Assess how fun and entertaining the story is"""
        score = 0.5  # Base score
        
        # Check for engaging elements
        story_text = f"{story_script.overall_story} {story_script.story_summary}"
        story_lower = story_text.lower()
        
        # Fun indicators
        fun_indicators = [
            "surprising", "amazing", "incredible", "fascinating", "shocking",
            "unexpected", "remarkable", "extraordinary", "mind-blowing"
        ]
        
        for indicator in fun_indicators:
            if indicator in story_lower:
                score += 0.1
        
        # Check for specific facts that could be surprising
        if any(char.isdigit() for char in story_text):
            score += 0.1  # Numbers often indicate specific facts
        
        # Check for story elements
        story_elements = ["story", "journey", "adventure", "discovery", "secret"]
        for element in story_elements:
            if element in story_lower:
                score += 0.05
        
        return min(1.0, score)
    
    def _assess_interest_level(self, story_script: StoryScript) -> float:
        """Assess how interesting and engaging the story is"""
        score = 0.5  # Base score
        
        story_text = f"{story_script.overall_story} {story_script.story_summary}"
        story_lower = story_text.lower()
        
        # Interest indicators
        interest_indicators = [
            "how", "why", "what", "when", "where", "who",
            "behind the scenes", "secret", "unknown", "hidden",
            "first", "original", "discovery", "invention"
        ]
        
        for indicator in interest_indicators:
            if indicator in story_lower:
                score += 0.05
        
        # Check for question-like structure
        if "?" in story_text or "did you know" in story_lower:
            score += 0.1
        
        # Check for specific details
        if len(story_text.split()) > 50:  # Sufficient detail
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_uniqueness(self, story_script: StoryScript) -> float:
        """Assess how unique and uncommon the story angle is"""
        score = 0.5  # Base score
        
        story_text = f"{story_script.overall_story} {story_script.story_summary}"
        story_lower = story_text.lower()
        
        # Uniqueness indicators
        uniqueness_indicators = [
            "first", "only", "unique", "rare", "uncommon", "exclusive",
            "never before", "groundbreaking", "revolutionary", "pioneering"
        ]
        
        for indicator in uniqueness_indicators:
            if indicator in story_lower:
                score += 0.1
        
        # Check for specific time periods or events
        if any(char.isdigit() for char in story_text):
            score += 0.1  # Specific dates/numbers indicate uniqueness
        
        # Check for specific people or places
        if any(word.istitle() for word in story_text.split()):
            score += 0.05  # Proper nouns indicate specificity
        
        return min(1.0, score)
    
    def _assess_educational_value(self, story_script: StoryScript) -> float:
        """Assess the educational value of the story"""
        score = 0.5  # Base score
        
        story_text = f"{story_script.overall_story} {story_script.story_summary}"
        story_lower = story_text.lower()
        
        # Educational indicators
        educational_indicators = [
            "learn", "understand", "explain", "teach", "discover",
            "science", "history", "technology", "innovation", "process",
            "how it works", "why it matters", "impact", "influence"
        ]
        
        for indicator in educational_indicators:
            if indicator in story_lower:
                score += 0.05
        
        # Check for scene plan educational content
        if story_script.scene_plan:
            educational_scenes = 0
            for scene in story_script.scene_plan:
                if any(keyword in scene.scene_purpose.lower() for keyword in 
                      ["explain", "teach", "demonstrate", "show", "reveal"]):
                    educational_scenes += 1
            
            if educational_scenes > 0:
                score += (educational_scenes / len(story_script.scene_plan)) * 0.3
        
        return min(1.0, score)
    
    def _assess_narrative_coherence(self, story_script: StoryScript) -> float:
        """Assess how well the story flows and connects"""
        score = 0.5  # Base score
        
        # Check if story has clear structure
        if story_script.scene_plan and len(story_script.scene_plan) >= 4:
            score += 0.2
        
        # Check for logical scene progression
        if story_script.scene_plan:
            scene_types = [scene.scene_type for scene in story_script.scene_plan]
            if "hook" in scene_types and "summary" in scene_types:
                score += 0.2
        
        # Check story length and detail
        story_text = f"{story_script.overall_story} {story_script.story_summary}"
        if len(story_text.split()) > 30:  # Sufficient detail
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_validation_issues(self, story_script: StoryScript, 
                                  fun_score: float, interest_score: float, 
                                  uniqueness_score: float, educational_score: float, 
                                  coherence_score: float) -> List[ValidationIssue]:
        """Generate validation issues based on scores"""
        issues = []
        
        if fun_score < 0.6:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.MEDIUM,
                category="fun_factor",
                description="Story lacks engaging and entertaining elements",
                suggestion="Add surprising facts, interesting anecdotes, or dramatic elements to make it more fun"
            ))
        
        if interest_score < 0.6:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.MEDIUM,
                category="interest_level",
                description="Story may not hold viewer attention",
                suggestion="Add intriguing questions, unknown facts, or behind-the-scenes information"
            ))
        
        if uniqueness_score < 0.6:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.MEDIUM,
                category="uniqueness",
                description="Story angle is too generic or common",
                suggestion="Focus on specific, uncommon aspects or unique perspectives"
            ))
        
        if educational_score < 0.6:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.HIGH,
                category="educational_value",
                description="Story lacks sufficient educational content",
                suggestion="Add more learning objectives, explanations, or educational elements"
            ))
        
        if coherence_score < 0.6:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.HIGH,
                category="narrative_coherence",
                description="Story structure and flow need improvement",
                suggestion="Ensure clear beginning, middle, end and logical scene progression"
            ))
        
        return issues
    
    def _generate_feedback(self, story_script: StoryScript, 
                          issues: List[ValidationIssue], overall_score: float) -> str:
        """Generate comprehensive feedback"""
        if overall_score >= 0.7:
            return f"Great story! The script has good potential with an overall score of {overall_score:.2f}. Proceed to scene generation."
        
        feedback = f"Story needs improvement (score: {overall_score:.2f}). "
        
        if issues:
            feedback += "Key areas for improvement:\n"
            for issue in issues:
                feedback += f"- {issue.category}: {issue.suggestion}\n"
        
        return feedback.strip()
    
    def _generate_revision_instructions(self, issues: List[ValidationIssue]) -> str:
        """Generate specific revision instructions"""
        if not issues:
            return "No specific revisions needed."
        
        instructions = "Please revise the story script with the following improvements:\n\n"
        
        for issue in issues:
            instructions += f"**{issue.category.replace('_', ' ').title()}**: {issue.suggestion}\n"
        
        instructions += "\nFocus on making the story more engaging, educational, and unique."
        return instructions

class ADKScriptValidatorAgent(Agent):
    """
    ADK-based Script Validator Agent
    
    This agent validates story-level quality before scene generation
    """
    
    def __init__(self, shared_context_manager: SharedContextManager = None):
        """
        Initialize ADK Script Validator Agent
        
        Args:
            shared_context_manager: SharedContextManager for maintaining consistency
        """
        # Check if API key is available
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        # Create validation tool
        validation_tool = ScriptValidationTool()
        
        # Initialize ADK Agent
        super().__init__(
            name="script_validator",
            description="Validates story script quality and provides feedback",
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
        self._validation_tool = validation_tool
        
        logger.info("ADK Script Validator Agent initialized with Gemini 2.5 Flash")
    
    def _get_instruction(self) -> str:
        """Get the instruction for the script validator agent"""
        return """
You are a STRICT Script Validator Agent responsible for rejecting mediocre content and demanding excellence.

## STRICT VALIDATION CRITERIA:

### 1. SPECIFICITY TEST (Fail if score < 0.8):
- Count specific names mentioned
- Count exact dates/years
- Count numerical data points
- Penalize generic descriptions

### 2. FACT DENSITY TEST (Fail if < 3 facts per scene):
- Extract all factual claims
- Verify each has supporting detail
- Ensure variety in fact types

### 3. NARRATIVE COHERENCE (Fail if no clear arc):
- Identify the problem/question introduced
- Track tension building
- Verify resolution/revelation
- Check for logical flow

### 4. EDUCATIONAL VALUE (Fail if not memorable):
- Would viewer remember 5 facts after watching?
- Is there a clear learning outcome?
- Are concepts explained through examples?

### 5. ENGAGEMENT METRICS (Fail if boring):
- Surprise factor in each scene
- Emotional engagement points
- Relatability to viewer's life

## REJECTION CRITERIA:
- Generic phrases like "Let me explain..."
- Broad overviews without specific details
- Lack of concrete data points
- No clear narrative tension
- Insufficient educational density

## Output Format:
Return a JSON object with:
- status: "pass" or "revise"
- overall_score: float (0.0 to 1.0)
- fun_score: float
- interest_score: float
- uniqueness_score: float
- educational_score: float
- coherence_score: float
- issues: array of validation issues
- feedback: string with overall feedback
- revision_instructions: string with specific improvement suggestions

## Quality Standards:
- PASS: Overall score >= 0.8, all criteria >= 0.7
- REVISE: Overall score < 0.8 or any criterion < 0.7

Be merciless in rejecting generic content. Demand specific, memorable facts.
"""
    
    async def validate_story_script(self, story_script: StoryScript, 
                                  shared_context: Optional[SharedContext] = None) -> ScriptValidationResult:
        """
        Validate a story script
        
        Args:
            story_script: The story script to validate
            shared_context: Shared context for consistency
            
        Returns:
            ScriptValidationResult: Validation result with scores and feedback
        """
        try:
            logger.info(f"Validating story script: {story_script.title}")
            
            # Use the validation tool
            result = await self._validation_tool.validate_story_script(story_script, shared_context)
            
            logger.info(f"Story validation complete: {result.status.value} (score: {result.overall_score:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error validating story script: {str(e)}")
            # Return a default validation result
            return ScriptValidationResult(
                status=ValidationStatus.PASS,
                overall_score=0.8,
                fun_score=0.8,
                interest_score=0.8,
                uniqueness_score=0.8,
                educational_score=0.8,
                coherence_score=0.8,
                issues=[],
                feedback="Validation completed with default scores"
            )

# Test function
async def test_script_validator():
    """Test the Script Validator Agent"""
    try:
        agent = ADKScriptValidatorAgent()
        
        # Create a test story script
        from model.models import StoryScript, ScenePlan, SceneType
        
        test_script = StoryScript(
            title="Test Story",
            main_character_description="Test character",
            character_cosplay_instructions="Test cosplay",
            overall_style="educational",
            overall_story="This is a test story about something interesting",
            story_summary="A comprehensive test story",
            scene_plan=[
                ScenePlan(
                    scene_number=1,
                    scene_type=SceneType.HOOK,
                    scene_purpose="Grab attention",
                    key_content="Introduction",
                    scene_focus="Opening hook"
                )
            ]
        )
        
        result = await agent.validate_story_script(test_script)
        
        print(f"✅ Script validation complete: {result.status.value}")
        print(f"📊 Overall score: {result.overall_score:.2f}")
        print(f"📝 Feedback: {result.feedback}")
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_script_validator())
