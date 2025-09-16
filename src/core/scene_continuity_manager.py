"""
Scene Continuity Manager
Ensures logical flow and visual consistency between scenes
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ContinuityIssue(Enum):
    """Types of continuity issues"""
    VISUAL_INCONSISTENCY = "visual_inconsistency"
    CHARACTER_STATE_MISMATCH = "character_state_mismatch"
    NARRATIVE_GAP = "narrative_gap"
    EDUCATIONAL_REPETITION = "educational_repetition"
    PACE_MISMATCH = "pace_mismatch"
    TRANSITION_ISSUE = "transition_issue"

class ContinuitySeverity(Enum):
    """Severity levels for continuity issues"""
    LOW = "low"  # Minor issue, can be ignored
    MEDIUM = "medium"  # Should be addressed
    HIGH = "high"  # Must be fixed
    CRITICAL = "critical"  # Breaks the flow

@dataclass
class ContinuityIssue:
    """Represents a continuity issue between scenes"""
    issue_type: ContinuityIssue
    severity: ContinuitySeverity
    description: str
    scene_number: int
    suggested_fix: str
    affected_elements: List[str] = field(default_factory=list)

@dataclass
class SceneTransition:
    """Represents a transition between scenes"""
    from_scene: int
    to_scene: int
    transition_type: str
    visual_continuity_score: float  # 0.0 to 1.0
    narrative_continuity_score: float  # 0.0 to 1.0
    character_continuity_score: float  # 0.0 to 1.0
    overall_score: float  # 0.0 to 1.0

class SceneContinuityManager:
    """Manages continuity between scenes"""
    
    def __init__(self):
        self.scene_data: List[Dict[str, Any]] = []
        self.continuity_rules = self._initialize_continuity_rules()
        self.visual_consistency_patterns = self._initialize_visual_patterns()
        logger.info("SceneContinuityManager initialized")
    
    def _initialize_continuity_rules(self) -> Dict[str, Any]:
        """Initialize continuity rules and guidelines"""
        return {
            "character_consistency": {
                "emotion_transitions": {
                    "excited": ["excited", "surprised", "confident"],
                    "curious": ["curious", "excited", "surprised"],
                    "serious": ["serious", "confident", "friendly"],
                    "sad": ["sad", "serious", "friendly"],
                    "confident": ["confident", "excited", "serious"]
                },
                "pose_transitions": {
                    "pointing": ["pointing", "gesturing", "explaining"],
                    "gesturing": ["gesturing", "pointing", "demonstrating"],
                    "explaining": ["explaining", "gesturing", "pointing"],
                    "demonstrating": ["demonstrating", "gesturing", "explaining"]
                }
            },
            "visual_consistency": {
                "color_scheme_consistency": True,
                "lighting_consistency": True,
                "style_consistency": True,
                "background_continuity": True
            },
            "narrative_flow": {
                "max_complexity_jump": 2,  # Max complexity increase between scenes
                "min_educational_progression": 1,  # Min learning progression
                "max_repetition_distance": 3  # Max scenes between similar facts
            }
        }
    
    def _initialize_visual_patterns(self) -> Dict[str, List[str]]:
        """Initialize visual consistency patterns"""
        return {
            "color_schemes": [
                ["#FF6B6B", "#4ECDC4", "#45B7D1"],  # Warm
                ["#96CEB4", "#FFEAA7", "#DDA0DD"],  # Pastel
                ["#2C3E50", "#34495E", "#7F8C8D"],  # Dark
                ["#E74C3C", "#F39C12", "#F1C40F"]   # Vibrant
            ],
            "lighting_styles": [
                "bright_educational", "warm_historical", "cool_modern", "dramatic_focus"
            ],
            "background_types": [
                "minimal_clean", "detailed_informative", "atmospheric_context", "interactive_demo"
            ]
        }
    
    def add_scene(self, scene_data: Dict[str, Any]) -> None:
        """Add a scene to the continuity manager"""
        self.scene_data.append(scene_data)
        logger.debug(f"Added scene {len(self.scene_data)} to continuity manager")
    
    def validate_scene_transition(self, prev_scene: Dict[str, Any], next_scene: Dict[str, Any]) -> List[ContinuityIssue]:
        """
        Validate transition between two scenes
        
        Args:
            prev_scene: Previous scene data
            next_scene: Next scene data
            
        Returns:
            List of continuity issues found
        """
        issues = []
        
        # Check character consistency
        character_issues = self._check_character_consistency(prev_scene, next_scene)
        issues.extend(character_issues)
        
        # Check visual consistency
        visual_issues = self._check_visual_consistency(prev_scene, next_scene)
        issues.extend(visual_issues)
        
        # Check narrative flow
        narrative_issues = self._check_narrative_flow(prev_scene, next_scene)
        issues.extend(narrative_issues)
        
        # Check educational progression
        educational_issues = self._check_educational_progression(prev_scene, next_scene)
        issues.extend(educational_issues)
        
        logger.debug(f"Found {len(issues)} continuity issues between scenes")
        return issues
    
    def _check_character_consistency(self, prev_scene: Dict[str, Any], next_scene: Dict[str, Any]) -> List[ContinuityIssue]:
        """Check character consistency between scenes"""
        issues = []
        
        prev_emotion = prev_scene.get("character_expression", "")
        next_emotion = next_scene.get("character_expression", "")
        prev_pose = prev_scene.get("character_pose", "")
        next_pose = next_scene.get("character_pose", "")
        
        # Check emotion transitions
        emotion_rules = self.continuity_rules["character_consistency"]["emotion_transitions"]
        if prev_emotion in emotion_rules:
            if next_emotion not in emotion_rules[prev_emotion]:
                issues.append(ContinuityIssue(
                    issue_type=ContinuityIssue.CHARACTER_STATE_MISMATCH,
                    severity=ContinuitySeverity.MEDIUM,
                    description=f"Emotion transition from '{prev_emotion}' to '{next_emotion}' may feel jarring",
                    scene_number=next_scene.get("scene_number", 0),
                    suggested_fix=f"Consider transitioning to: {', '.join(emotion_rules[prev_emotion])}",
                    affected_elements=["character_expression"]
                ))
        
        # Check pose transitions
        pose_rules = self.continuity_rules["character_consistency"]["pose_transitions"]
        if prev_pose in pose_rules:
            if next_pose not in pose_rules[prev_pose]:
                issues.append(ContinuityIssue(
                    issue_type=ContinuityIssue.CHARACTER_STATE_MISMATCH,
                    severity=ContinuitySeverity.LOW,
                    description=f"Pose transition from '{prev_pose}' to '{next_pose}' may feel unnatural",
                    scene_number=next_scene.get("scene_number", 0),
                    suggested_fix=f"Consider transitioning to: {', '.join(pose_rules[prev_pose])}",
                    affected_elements=["character_pose"]
                ))
        
        return issues
    
    def _check_visual_consistency(self, prev_scene: Dict[str, Any], next_scene: Dict[str, Any]) -> List[ContinuityIssue]:
        """Check visual consistency between scenes"""
        issues = []
        
        # Check color scheme consistency
        prev_colors = self._extract_color_scheme(prev_scene)
        next_colors = self._extract_color_scheme(next_scene)
        
        if prev_colors and next_colors:
            color_similarity = self._calculate_color_similarity(prev_colors, next_colors)
            if color_similarity < 0.3:  # Low similarity threshold
                issues.append(ContinuityIssue(
                    issue_type=ContinuityIssue.VISUAL_INCONSISTENCY,
                    severity=ContinuitySeverity.MEDIUM,
                    description="Significant color scheme change between scenes",
                    scene_number=next_scene.get("scene_number", 0),
                    suggested_fix="Consider maintaining similar color palette or using gradual transition",
                    affected_elements=["color_scheme", "visual_style"]
                ))
        
        # Check lighting consistency
        prev_lighting = prev_scene.get("visual_elements", {}).get("lighting", "")
        next_lighting = next_scene.get("visual_elements", {}).get("lighting", "")
        
        if prev_lighting and next_lighting and prev_lighting != next_lighting:
            issues.append(ContinuityIssue(
                issue_type=ContinuityIssue.VISUAL_INCONSISTENCY,
                severity=ContinuitySeverity.LOW,
                description=f"Lighting change from '{prev_lighting}' to '{next_lighting}'",
                scene_number=next_scene.get("scene_number", 0),
                suggested_fix="Consider maintaining consistent lighting or using transition effect",
                affected_elements=["lighting"]
            ))
        
        return issues
    
    def _check_narrative_flow(self, prev_scene: Dict[str, Any], next_scene: Dict[str, Any]) -> List[ContinuityIssue]:
        """Check narrative flow between scenes"""
        issues = []
        
        # Check complexity progression
        prev_complexity = self._calculate_scene_complexity(prev_scene)
        next_complexity = self._calculate_scene_complexity(next_scene)
        
        complexity_jump = abs(next_complexity - prev_complexity)
        max_jump = self.continuity_rules["narrative_flow"]["max_complexity_jump"]
        
        if complexity_jump > max_jump:
            issues.append(ContinuityIssue(
                issue_type=ContinuityIssue.PACE_MISMATCH,
                severity=ContinuitySeverity.HIGH,
                description=f"Large complexity jump from {prev_complexity} to {next_complexity}",
                scene_number=next_scene.get("scene_number", 0),
                suggested_fix="Consider gradual complexity progression or intermediate scene",
                affected_elements=["educational_content", "scene_type"]
            ))
        
        # Check transition appropriateness
        prev_type = prev_scene.get("scene_type", "")
        next_type = next_scene.get("scene_type", "")
        transition_type = next_scene.get("transition_to_next", "")
        
        if not self._is_transition_appropriate(prev_type, next_type, transition_type):
            issues.append(ContinuityIssue(
                issue_type=ContinuityIssue.TRANSITION_ISSUE,
                severity=ContinuitySeverity.MEDIUM,
                description=f"Transition '{transition_type}' may not be appropriate from '{prev_type}' to '{next_type}'",
                scene_number=next_scene.get("scene_number", 0),
                suggested_fix="Consider using a different transition type or adjusting scene types",
                affected_elements=["transition_to_next", "scene_type"]
            ))
        
        return issues
    
    def _check_educational_progression(self, prev_scene: Dict[str, Any], next_scene: Dict[str, Any]) -> List[ContinuityIssue]:
        """Check educational progression between scenes"""
        issues = []
        
        # Check for repetition
        prev_facts = self._extract_educational_facts(prev_scene)
        next_facts = self._extract_educational_facts(next_scene)
        
        repetition_score = self._calculate_fact_repetition(prev_facts, next_facts)
        if repetition_score > 0.7:  # High repetition threshold
            issues.append(ContinuityIssue(
                issue_type=ContinuityIssue.EDUCATIONAL_REPETITION,
                severity=ContinuitySeverity.MEDIUM,
                description="High similarity in educational content between scenes",
                scene_number=next_scene.get("scene_number", 0),
                suggested_fix="Consider different educational angle or building upon previous content",
                affected_elements=["educational_content", "key_concepts"]
            ))
        
        return issues
    
    def _extract_color_scheme(self, scene_data: Dict[str, Any]) -> List[str]:
        """Extract color scheme from scene data"""
        visual_elements = scene_data.get("visual_elements", {})
        color_scheme = visual_elements.get("color_scheme", "")
        
        if color_scheme:
            # Simple color extraction - in real implementation, use proper color parsing
            colors = []
            for color in ["red", "blue", "green", "yellow", "purple", "orange"]:
                if color in color_scheme.lower():
                    colors.append(color)
            return colors
        
        return []
    
    def _calculate_color_similarity(self, colors1: List[str], colors2: List[str]) -> float:
        """Calculate similarity between two color schemes"""
        if not colors1 or not colors2:
            return 0.0
        
        intersection = set(colors1) & set(colors2)
        union = set(colors1) | set(colors2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_scene_complexity(self, scene_data: Dict[str, Any]) -> int:
        """Calculate complexity score for a scene"""
        complexity = 0
        
        # Count educational concepts
        educational_content = scene_data.get("educational_content", {})
        for category, items in educational_content.items():
            complexity += len(items)
        
        # Add complexity for scene type
        scene_type = scene_data.get("scene_type", "")
        type_complexity = {
            "hook": 1,
            "explanation": 3,
            "example": 2,
            "statistic": 2,
            "comparison": 4,
            "story_telling": 2,
            "conclusion": 1
        }
        complexity += type_complexity.get(scene_type, 2)
        
        return min(10, complexity)
    
    def _is_transition_appropriate(self, prev_type: str, next_type: str, transition_type: str) -> bool:
        """Check if transition type is appropriate for scene types"""
        appropriate_transitions = {
            ("hook", "explanation"): ["fade", "cut"],
            ("explanation", "example"): ["fade", "slide"],
            ("example", "statistic"): ["fade", "cut"],
            ("statistic", "comparison"): ["fade", "dissolve"],
            ("comparison", "conclusion"): ["fade", "zoom"],
            ("story_telling", "explanation"): ["fade", "cut"]
        }
        
        key = (prev_type, next_type)
        return transition_type in appropriate_transitions.get(key, ["fade", "cut"])
    
    def _extract_educational_facts(self, scene_data: Dict[str, Any]) -> List[str]:
        """Extract educational facts from scene data"""
        facts = []
        educational_content = scene_data.get("educational_content", {})
        
        for category, items in educational_content.items():
            facts.extend(items)
        
        return facts
    
    def _calculate_fact_repetition(self, facts1: List[str], facts2: List[str]) -> float:
        """Calculate repetition score between two fact lists"""
        if not facts1 or not facts2:
            return 0.0
        
        # Simple word-based similarity
        words1 = set(" ".join(facts1).lower().split())
        words2 = set(" ".join(facts2).lower().split())
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_continuity_report(self) -> Dict[str, Any]:
        """Generate a comprehensive continuity report"""
        if len(self.scene_data) < 2:
            return {"message": "Need at least 2 scenes for continuity analysis"}
        
        all_issues = []
        transition_scores = []
        
        # Analyze all scene transitions
        for i in range(len(self.scene_data) - 1):
            prev_scene = self.scene_data[i]
            next_scene = self.scene_data[i + 1]
            
            issues = self.validate_scene_transition(prev_scene, next_scene)
            all_issues.extend(issues)
            
            # Calculate transition score
            transition_score = self._calculate_transition_score(prev_scene, next_scene)
            transition_scores.append(transition_score)
        
        # Categorize issues by severity
        issues_by_severity = {
            "critical": [i for i in all_issues if i.severity == ContinuitySeverity.CRITICAL],
            "high": [i for i in all_issues if i.severity == ContinuitySeverity.HIGH],
            "medium": [i for i in all_issues if i.severity == ContinuitySeverity.MEDIUM],
            "low": [i for i in all_issues if i.severity == ContinuitySeverity.LOW]
        }
        
        # Calculate overall continuity score
        overall_score = sum(transition_scores) / len(transition_scores) if transition_scores else 0.0
        
        return {
            "overall_continuity_score": overall_score,
            "total_issues": len(all_issues),
            "issues_by_severity": {
                severity.value: len(issues) for severity, issues in issues_by_severity.items()
            },
            "critical_issues": [self._issue_to_dict(issue) for issue in issues_by_severity["critical"]],
            "high_priority_issues": [self._issue_to_dict(issue) for issue in issues_by_severity["high"]],
            "transition_scores": transition_scores,
            "recommendations": self._generate_recommendations(issues_by_severity)
        }
    
    def _calculate_transition_score(self, prev_scene: Dict[str, Any], next_scene: Dict[str, Any]) -> float:
        """Calculate overall transition score between scenes"""
        # This is a simplified scoring system
        # In a real implementation, this would be more sophisticated
        
        score = 1.0
        
        # Deduct points for issues
        issues = self.validate_scene_transition(prev_scene, next_scene)
        for issue in issues:
            if issue.severity == ContinuitySeverity.CRITICAL:
                score -= 0.3
            elif issue.severity == ContinuitySeverity.HIGH:
                score -= 0.2
            elif issue.severity == ContinuitySeverity.MEDIUM:
                score -= 0.1
            elif issue.severity == ContinuitySeverity.LOW:
                score -= 0.05
        
        return max(0.0, score)
    
    def _issue_to_dict(self, issue: ContinuityIssue) -> Dict[str, Any]:
        """Convert continuity issue to dictionary"""
        return {
            "type": issue.issue_type.value,
            "severity": issue.severity.value,
            "description": issue.description,
            "scene_number": issue.scene_number,
            "suggested_fix": issue.suggested_fix,
            "affected_elements": issue.affected_elements
        }
    
    def _generate_recommendations(self, issues_by_severity: Dict[str, List[ContinuityIssue]]) -> List[str]:
        """Generate recommendations based on issues found"""
        recommendations = []
        
        if issues_by_severity["critical"]:
            recommendations.append("🚨 CRITICAL: Address critical continuity issues immediately")
        
        if issues_by_severity["high"]:
            recommendations.append("⚠️ HIGH: Fix high-priority continuity issues before production")
        
        if issues_by_severity["medium"]:
            recommendations.append("💡 MEDIUM: Consider addressing medium-priority issues for better flow")
        
        if not any(issues_by_severity.values()):
            recommendations.append("✅ EXCELLENT: No continuity issues found!")
        
        return recommendations

# Test function
def test_scene_continuity_manager():
    """Test the SceneContinuityManager"""
    manager = SceneContinuityManager()
    
    # Test scenes
    scene1 = {
        "scene_number": 1,
        "scene_type": "hook",
        "character_expression": "excited",
        "character_pose": "pointing",
        "visual_elements": {
            "color_scheme": "warm red and blue tones",
            "lighting": "bright educational"
        },
        "educational_content": {
            "key_concepts": ["Coca-Cola origin"],
            "specific_facts": ["Created in 1886"]
        }
    }
    
    scene2 = {
        "scene_number": 2,
        "scene_type": "explanation",
        "character_expression": "curious",
        "character_pose": "gesturing",
        "visual_elements": {
            "color_scheme": "cool blue and green tones",
            "lighting": "warm historical"
        },
        "educational_content": {
            "key_concepts": ["Coca-Cola ingredients"],
            "specific_facts": ["Contains coca leaves"]
        }
    }
    
    # Add scenes
    manager.add_scene(scene1)
    manager.add_scene(scene2)
    
    # Validate transition
    issues = manager.validate_scene_transition(scene1, scene2)
    
    print(f"Found {len(issues)} continuity issues:")
    for issue in issues:
        print(f"- {issue.severity.value}: {issue.description}")
        print(f"  Fix: {issue.suggested_fix}")
    
    # Generate report
    report = manager.get_continuity_report()
    print(f"\nOverall continuity score: {report['overall_continuity_score']:.2f}")

if __name__ == "__main__":
    test_scene_continuity_manager()
