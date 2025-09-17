"""
Image Style Selector
Intelligent image style selection based on scene content
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Import from models
from model.models import SceneType, ImageStyle

@dataclass
class StyleSelectionCriteria:
    """Criteria for style selection"""
    scene_type: SceneType
    content_type: str
    educational_goal: str
    engagement_level: int  # 1-10
    visual_complexity: int  # 1-10
    target_audience: str

@dataclass
class StyleSelectionResult:
    """Result of style selection"""
    selected_style: ImageStyle
    confidence_score: float  # 0.0 to 1.0
    reasoning: str
    alternative_styles: List[ImageStyle]
    style_characteristics: Dict[str, Any]

class ImageStyleSelector:
    """Intelligent image style selection based on scene content"""
    
    def __init__(self):
        self.style_mappings = self._initialize_style_mappings()
        self.content_analysis_patterns = self._initialize_content_patterns()
        self.audience_preferences = self._initialize_audience_preferences()
        logger.info("ImageStyleSelector initialized")
    
    def _initialize_style_mappings(self) -> Dict[SceneType, Dict[str, List[ImageStyle]]]:
        """Initialize style mappings for different scene types and content"""
        return {
            SceneType.HOOK: {
                "shocking_fact": [ImageStyle.SPLIT_SCREEN, ImageStyle.CLOSE_UP_REACTION, ImageStyle.INFOGRAPHIC],
                "question": [ImageStyle.CLOSE_UP_REACTION, ImageStyle.SPEECH_BUBBLE, ImageStyle.CINEMATIC],
                "statistic": [ImageStyle.INFOGRAPHIC, ImageStyle.OVERLAY_GRAPHICS, ImageStyle.DIAGRAM_EXPLANATION],
                "story": [ImageStyle.CINEMATIC, ImageStyle.COMIC_PANEL, ImageStyle.FOUR_CUT_CARTOON],
                "controversy": [ImageStyle.SPLIT_SCREEN, ImageStyle.BEFORE_AFTER_COMPARISON, ImageStyle.CINEMATIC]
            },
            SceneType.EXPLANATION: {
                "process": [ImageStyle.STEP_BY_STEP_VISUAL, ImageStyle.DIAGRAM_EXPLANATION, ImageStyle.INFOGRAPHIC],
                "comparison": [ImageStyle.BEFORE_AFTER_COMPARISON, ImageStyle.SPLIT_SCREEN, ImageStyle.DIAGRAM_EXPLANATION],
                "technical": [ImageStyle.DIAGRAM_EXPLANATION, ImageStyle.OVERLAY_GRAPHICS, ImageStyle.INFOGRAPHIC],
                "concept": [ImageStyle.OVERLAY_GRAPHICS, ImageStyle.DIAGRAM_EXPLANATION, ImageStyle.INFOGRAPHIC],
                "data": [ImageStyle.INFOGRAPHIC, ImageStyle.OVERLAY_GRAPHICS, ImageStyle.DIAGRAM_EXPLANATION]
            },
            SceneType.VISUAL_DEMO: {
                "demonstration": [ImageStyle.STEP_BY_STEP_VISUAL, ImageStyle.DIAGRAM_EXPLANATION, ImageStyle.CHARACTER_WITH_BACKGROUND],
                "tutorial": [ImageStyle.STEP_BY_STEP_VISUAL, ImageStyle.DIAGRAM_EXPLANATION, ImageStyle.OVERLAY_GRAPHICS],
                "showcase": [ImageStyle.CINEMATIC, ImageStyle.CHARACTER_WITH_BACKGROUND, ImageStyle.WIDE_ESTABLISHING_SHOT]
            },
            SceneType.COMPARISON: {
                "before_after": [ImageStyle.BEFORE_AFTER_COMPARISON, ImageStyle.SPLIT_SCREEN, ImageStyle.DIAGRAM_EXPLANATION],
                "pros_cons": [ImageStyle.SPLIT_SCREEN, ImageStyle.BEFORE_AFTER_COMPARISON, ImageStyle.INFOGRAPHIC],
                "alternatives": [ImageStyle.SPLIT_SCREEN, ImageStyle.DIAGRAM_EXPLANATION, ImageStyle.OVERLAY_GRAPHICS]
            },
            SceneType.STORY_TELLING: {
                "historical": [ImageStyle.FOUR_CUT_CARTOON, ImageStyle.CINEMATIC, ImageStyle.COMIC_PANEL],
                "dramatic": [ImageStyle.CINEMATIC, ImageStyle.CLOSE_UP_REACTION, ImageStyle.WIDE_ESTABLISHING_SHOT],
                "personal": [ImageStyle.COMIC_PANEL, ImageStyle.CHARACTER_WITH_BACKGROUND, ImageStyle.CLOSE_UP_REACTION],
                "narrative": [ImageStyle.COMIC_PANEL, ImageStyle.FOUR_CUT_CARTOON, ImageStyle.CINEMATIC]
            },
            SceneType.CONCLUSION: {
                "summary": [ImageStyle.INFOGRAPHIC, ImageStyle.OVERLAY_GRAPHICS, ImageStyle.CHARACTER_WITH_BACKGROUND],
                "call_to_action": [ImageStyle.CHARACTER_WITH_BACKGROUND, ImageStyle.SPEECH_BUBBLE, ImageStyle.CLOSE_UP_REACTION],
                "reflection": [ImageStyle.CLOSE_UP_REACTION, ImageStyle.CHARACTER_WITH_BACKGROUND, ImageStyle.CINEMATIC]
            }
        }
    
    def _initialize_content_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for content analysis"""
        return {
            "statistics": ["percent", "%", "million", "billion", "statistics", "data", "numbers", "figures"],
            "process": ["step", "process", "how to", "method", "procedure", "workflow", "sequence"],
            "comparison": ["vs", "versus", "compared to", "difference", "similar", "different", "better", "worse"],
            "story": ["story", "tale", "narrative", "journey", "adventure", "experience", "happened"],
            "technical": ["algorithm", "system", "technology", "mechanism", "function", "operation", "code"],
            "visual": ["show", "demonstrate", "visualize", "display", "illustrate", "depict", "represent"],
            "emotional": ["feel", "emotion", "reaction", "response", "impact", "effect", "influence"],
            "historical": ["history", "past", "origin", "beginning", "started", "founded", "created"],
            "future": ["future", "will", "going to", "predict", "forecast", "trend", "evolution"]
        }
    
    def _initialize_audience_preferences(self) -> Dict[str, Dict[str, Any]]:
        """Initialize audience preferences for different styles"""
        return {
            "beginner": {
                "preferred_styles": [ImageStyle.CHARACTER_WITH_BACKGROUND, ImageStyle.SPEECH_BUBBLE, ImageStyle.COMIC_PANEL],
                "avoid_styles": [ImageStyle.DIAGRAM_EXPLANATION, ImageStyle.OVERLAY_GRAPHICS],
                "complexity_threshold": 5,
                "engagement_priority": 8
            },
            "general": {
                "preferred_styles": [ImageStyle.INFOGRAPHIC, ImageStyle.CHARACTER_WITH_BACKGROUND, ImageStyle.CINEMATIC],
                "avoid_styles": [],
                "complexity_threshold": 7,
                "engagement_priority": 7
            },
            "intermediate": {
                "preferred_styles": [ImageStyle.DIAGRAM_EXPLANATION, ImageStyle.INFOGRAPHIC, ImageStyle.STEP_BY_STEP_VISUAL],
                "avoid_styles": [ImageStyle.COMIC_PANEL, ImageStyle.FOUR_CUT_CARTOON],
                "complexity_threshold": 8,
                "engagement_priority": 6
            },
            "expert": {
                "preferred_styles": [ImageStyle.DIAGRAM_EXPLANATION, ImageStyle.OVERLAY_GRAPHICS, ImageStyle.STEP_BY_STEP_VISUAL],
                "avoid_styles": [ImageStyle.COMIC_PANEL, ImageStyle.SPEECH_BUBBLE],
                "complexity_threshold": 10,
                "engagement_priority": 5
            }
        }
    
    def select_optimal_style(self, scene_data: Dict[str, Any], previous_styles: List[ImageStyle] = None, 
                           target_audience: str = "general") -> StyleSelectionResult:
        """
        Select optimal image style based on scene content analysis
        
        Args:
            scene_data: Scene data including type, content, and educational elements
            previous_styles: List of previously used styles to avoid repetition
            target_audience: Target audience for the content
            
        Returns:
            StyleSelectionResult with selected style and reasoning
        """
        logger.info(f"Selecting optimal style for scene type: {scene_data.get('scene_type', 'unknown')}")
        
        # Analyze scene content
        content_analysis = self._analyze_scene_content(scene_data)
        
        # Get candidate styles based on scene type and content
        candidate_styles = self._get_candidate_styles(scene_data, content_analysis)
        
        # Filter based on audience preferences
        audience_filtered_styles = self._filter_by_audience(candidate_styles, target_audience)
        
        # Avoid recent style repetition
        if previous_styles:
            audience_filtered_styles = self._avoid_style_repetition(audience_filtered_styles, previous_styles)
        
        # Score and rank styles
        scored_styles = self._score_styles(audience_filtered_styles, scene_data, content_analysis, target_audience)
        
        # Select best style
        if not scored_styles:
            # Fallback to default style
            selected_style = ImageStyle.CHARACTER_WITH_BACKGROUND
            confidence_score = 0.3
            reasoning = "No suitable styles found, using default fallback"
        else:
            selected_style, confidence_score = scored_styles[0]
            reasoning = self._generate_reasoning(selected_style, scene_data, content_analysis)
        
        # Get alternative styles
        alternative_styles = [style for style, _ in scored_styles[1:3]] if len(scored_styles) > 1 else []
        
        # Get style characteristics
        style_characteristics = self._get_style_characteristics(selected_style)
        
        result = StyleSelectionResult(
            selected_style=selected_style,
            confidence_score=confidence_score,
            reasoning=reasoning,
            alternative_styles=alternative_styles,
            style_characteristics=style_characteristics
        )
        
        logger.info(f"Selected style: {selected_style.value} (confidence: {confidence_score:.2f})")
        return result
    
    def _analyze_scene_content(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze scene content to determine content type and characteristics"""
        analysis = {
            "content_types": [],
            "educational_elements": [],
            "engagement_factors": [],
            "visual_complexity": 5,  # Default
            "data_density": 0,
            "story_elements": 0
        }
        
        # Analyze dialogue
        dialogue = scene_data.get("dialogue", "").lower()
        for content_type, patterns in self.content_analysis_patterns.items():
            if any(pattern in dialogue for pattern in patterns):
                analysis["content_types"].append(content_type)
        
        # Analyze educational content
        educational_content = scene_data.get("educational_content", {})
        for category, items in educational_content.items():
            analysis["educational_elements"].extend(items)
            if category == "statistics":
                analysis["data_density"] += len(items)
        
        # Analyze visual elements
        visual_elements = scene_data.get("visual_elements", {})
        if visual_elements.get("primary_focus"):
            analysis["visual_complexity"] += 1
        if visual_elements.get("secondary_elements"):
            analysis["visual_complexity"] += len(visual_elements["secondary_elements"])
        
        # Count story elements
        story_keywords = ["story", "tale", "narrative", "journey", "adventure"]
        analysis["story_elements"] = sum(1 for keyword in story_keywords if keyword in dialogue)
        
        return analysis
    
    def _get_candidate_styles(self, scene_data: Dict[str, Any], content_analysis: Dict[str, Any]) -> List[ImageStyle]:
        """Get candidate styles based on scene type and content analysis"""
        scene_type = scene_data.get("scene_type", SceneType.EXPLANATION)
        
        # Get base styles for scene type
        base_styles = []
        if scene_type in self.style_mappings:
            for content_type, styles in self.style_mappings[scene_type].items():
                if content_type in content_analysis["content_types"]:
                    base_styles.extend(styles)
        
        # If no specific content type match, use general styles for scene type
        if not base_styles and scene_type in self.style_mappings:
            all_styles = []
            for styles in self.style_mappings[scene_type].values():
                all_styles.extend(styles)
            base_styles = list(set(all_styles))  # Remove duplicates
        
        # Fallback to general styles
        if not base_styles:
            base_styles = [ImageStyle.CHARACTER_WITH_BACKGROUND, ImageStyle.INFOGRAPHIC, ImageStyle.CINEMATIC]
        
        return base_styles
    
    def _filter_by_audience(self, candidate_styles: List[ImageStyle], target_audience: str) -> List[ImageStyle]:
        """Filter styles based on audience preferences"""
        if target_audience not in self.audience_preferences:
            return candidate_styles
        
        audience_prefs = self.audience_preferences[target_audience]
        preferred_styles = audience_prefs["preferred_styles"]
        avoid_styles = audience_prefs["avoid_styles"]
        
        # Prioritize preferred styles
        filtered_styles = []
        for style in candidate_styles:
            if style in preferred_styles:
                filtered_styles.insert(0, style)  # Add to front
            elif style not in avoid_styles:
                filtered_styles.append(style)
        
        return filtered_styles if filtered_styles else candidate_styles
    
    def _avoid_style_repetition(self, candidate_styles: List[ImageStyle], previous_styles: List[ImageStyle]) -> List[ImageStyle]:
        """Avoid repeating recently used styles"""
        if not previous_styles:
            return candidate_styles
        
        # Get recent styles (last 2-3 scenes)
        recent_styles = previous_styles[-3:] if len(previous_styles) >= 3 else previous_styles
        
        # Filter out recent styles
        filtered_styles = [style for style in candidate_styles if style not in recent_styles]
        
        # If all styles are filtered out, return original list
        return filtered_styles if filtered_styles else candidate_styles
    
    def _score_styles(self, candidate_styles: List[ImageStyle], scene_data: Dict[str, Any], 
                     content_analysis: Dict[str, Any], target_audience: str) -> List[Tuple[ImageStyle, float]]:
        """Score and rank candidate styles"""
        scored_styles = []
        
        for style in candidate_styles:
            score = 0.0
            
            # Base score for style appropriateness
            score += self._get_style_base_score(style, scene_data, content_analysis)
            
            # Audience preference bonus
            score += self._get_audience_bonus(style, target_audience)
            
            # Content type matching bonus
            score += self._get_content_matching_bonus(style, content_analysis)
            
            # Visual complexity matching
            score += self._get_complexity_matching_bonus(style, content_analysis)
            
            # Educational effectiveness bonus
            score += self._get_educational_effectiveness_bonus(style, scene_data)
            
            scored_styles.append((style, score))
        
        # Sort by score (highest first)
        scored_styles.sort(key=lambda x: x[1], reverse=True)
        
        return scored_styles
    
    def _get_style_base_score(self, style: ImageStyle, scene_data: Dict[str, Any], content_analysis: Dict[str, Any]) -> float:
        """Get base score for style appropriateness"""
        base_scores = {
            ImageStyle.INFOGRAPHIC: 0.8,
            ImageStyle.CHARACTER_WITH_BACKGROUND: 0.7,
            ImageStyle.DIAGRAM_EXPLANATION: 0.8,
            ImageStyle.STEP_BY_STEP_VISUAL: 0.7,
            ImageStyle.BEFORE_AFTER_COMPARISON: 0.6,
            ImageStyle.SPLIT_SCREEN: 0.6,
            ImageStyle.OVERLAY_GRAPHICS: 0.7,
            ImageStyle.FOUR_CUT_CARTOON: 0.5,
            ImageStyle.COMIC_PANEL: 0.5,
            ImageStyle.SPEECH_BUBBLE: 0.4,
            ImageStyle.CINEMATIC: 0.6,
            ImageStyle.CLOSE_UP_REACTION: 0.5,
            ImageStyle.WIDE_ESTABLISHING_SHOT: 0.4
        }
        
        return base_scores.get(style, 0.5)
    
    def _get_audience_bonus(self, style: ImageStyle, target_audience: str) -> float:
        """Get bonus score based on audience preferences"""
        if target_audience not in self.audience_preferences:
            return 0.0
        
        audience_prefs = self.audience_preferences[target_audience]
        
        if style in audience_prefs["preferred_styles"]:
            return 0.2
        elif style in audience_prefs["avoid_styles"]:
            return -0.2
        else:
            return 0.0
    
    def _get_content_matching_bonus(self, style: ImageStyle, content_analysis: Dict[str, Any]) -> float:
        """Get bonus score for content type matching"""
        content_types = content_analysis["content_types"]
        
        if "statistics" in content_types and style == ImageStyle.INFOGRAPHIC:
            return 0.3
        elif "process" in content_types and style == ImageStyle.STEP_BY_STEP_VISUAL:
            return 0.3
        elif "comparison" in content_types and style in [ImageStyle.BEFORE_AFTER_COMPARISON, ImageStyle.SPLIT_SCREEN]:
            return 0.3
        elif "story" in content_types and style in [ImageStyle.COMIC_PANEL, ImageStyle.FOUR_CUT_CARTOON]:
            return 0.3
        elif "technical" in content_types and style == ImageStyle.DIAGRAM_EXPLANATION:
            return 0.3
        
        return 0.0
    
    def _get_complexity_matching_bonus(self, style: ImageStyle, content_analysis: Dict[str, Any]) -> float:
        """Get bonus score for visual complexity matching"""
        visual_complexity = content_analysis["visual_complexity"]
        
        # High complexity styles for complex content
        if visual_complexity > 7 and style in [ImageStyle.DIAGRAM_EXPLANATION, ImageStyle.OVERLAY_GRAPHICS]:
            return 0.2
        # Medium complexity styles for medium content
        elif 4 <= visual_complexity <= 7 and style in [ImageStyle.INFOGRAPHIC, ImageStyle.CHARACTER_WITH_BACKGROUND]:
            return 0.2
        # Low complexity styles for simple content
        elif visual_complexity < 4 and style in [ImageStyle.SPEECH_BUBBLE, ImageStyle.CLOSE_UP_REACTION]:
            return 0.2
        
        return 0.0
    
    def _get_educational_effectiveness_bonus(self, style: ImageStyle, scene_data: Dict[str, Any]) -> float:
        """Get bonus score for educational effectiveness"""
        educational_content = scene_data.get("educational_content", {})
        
        if not educational_content:
            return 0.0
        
        # Styles that are particularly good for education
        educational_styles = [ImageStyle.INFOGRAPHIC, ImageStyle.DIAGRAM_EXPLANATION, ImageStyle.STEP_BY_STEP_VISUAL]
        
        if style in educational_styles:
            return 0.2
        
        return 0.0
    
    def _generate_reasoning(self, selected_style: ImageStyle, scene_data: Dict[str, Any], content_analysis: Dict[str, Any]) -> str:
        """Generate reasoning for style selection"""
        scene_type = scene_data.get("scene_type", "unknown")
        content_types = content_analysis["content_types"]
        
        reasoning_parts = []
        
        # Scene type reasoning
        reasoning_parts.append(f"Selected {selected_style.value} for {scene_type} scene")
        
        # Content type reasoning
        if content_types:
            reasoning_parts.append(f"Content analysis detected: {', '.join(content_types)}")
        
        # Specific style reasoning
        if selected_style == ImageStyle.INFOGRAPHIC:
            reasoning_parts.append("Infographic style chosen for data visualization and educational content")
        elif selected_style == ImageStyle.STEP_BY_STEP_VISUAL:
            reasoning_parts.append("Step-by-step style chosen for process demonstration")
        elif selected_style == ImageStyle.DIAGRAM_EXPLANATION:
            reasoning_parts.append("Diagram style chosen for technical explanation")
        elif selected_style == ImageStyle.COMIC_PANEL:
            reasoning_parts.append("Comic panel style chosen for storytelling elements")
        elif selected_style == ImageStyle.CINEMATIC:
            reasoning_parts.append("Cinematic style chosen for dramatic presentation")
        
        return ". ".join(reasoning_parts) + "."
    
    def _get_style_characteristics(self, style: ImageStyle) -> Dict[str, Any]:
        """Get characteristics of the selected style"""
        characteristics = {
            ImageStyle.INFOGRAPHIC: {
                "visual_complexity": "high",
                "educational_effectiveness": "high",
                "engagement_level": "medium",
                "best_for": ["data", "statistics", "comparisons"],
                "layout": "grid-based with clear hierarchy"
            },
            ImageStyle.CHARACTER_WITH_BACKGROUND: {
                "visual_complexity": "medium",
                "educational_effectiveness": "medium",
                "engagement_level": "high",
                "best_for": ["explanations", "introductions", "conclusions"],
                "layout": "character-focused with supporting background"
            },
            ImageStyle.DIAGRAM_EXPLANATION: {
                "visual_complexity": "high",
                "educational_effectiveness": "high",
                "engagement_level": "medium",
                "best_for": ["technical concepts", "processes", "systems"],
                "layout": "structured diagram with labels and arrows"
            },
            ImageStyle.STEP_BY_STEP_VISUAL: {
                "visual_complexity": "medium",
                "educational_effectiveness": "high",
                "engagement_level": "medium",
                "best_for": ["tutorials", "procedures", "workflows"],
                "layout": "sequential steps with clear progression"
            },
            ImageStyle.COMIC_PANEL: {
                "visual_complexity": "low",
                "educational_effectiveness": "medium",
                "engagement_level": "high",
                "best_for": ["stories", "narratives", "scenarios"],
                "layout": "panel-based with speech bubbles"
            },
            ImageStyle.CINEMATIC: {
                "visual_complexity": "high",
                "educational_effectiveness": "medium",
                "engagement_level": "high",
                "best_for": ["dramatic moments", "hooks", "conclusions"],
                "layout": "cinematic composition with depth and atmosphere"
            }
        }
        
        return characteristics.get(style, {
            "visual_complexity": "medium",
            "educational_effectiveness": "medium",
            "engagement_level": "medium",
            "best_for": ["general content"],
            "layout": "standard composition"
        })

# Test function
def test_image_style_selector():
    """Test the ImageStyleSelector"""
    selector = ImageStyleSelector()
    
    # Test scene data
    test_scene = {
        "scene_type": "hook",
        "dialogue": "Did you know that 90% of people don't know this shocking statistic about the company?",
        "educational_content": {
            "statistics": ["90% of people", "shocking statistic"],
            "key_concepts": ["the company", "statistics"]
        },
        "visual_elements": {
            "primary_focus": "statistical data",
            "secondary_elements": ["the company branding", "surprised reactions"]
        }
    }
    
    # Test style selection
    result = selector.select_optimal_style(test_scene, target_audience="general")
    
    print(f"Selected style: {result.selected_style.value}")
    print(f"Confidence score: {result.confidence_score:.2f}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Alternative styles: {[style.value for style in result.alternative_styles]}")
    print(f"Style characteristics: {result.style_characteristics}")

if __name__ == "__main__":
    test_image_style_selector()
