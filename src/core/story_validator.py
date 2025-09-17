"""
Story Validation and Complexity Scoring System
Validates story scoping and provides complexity analysis
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ComplexityLevel(Enum):
    """Story complexity levels"""
    SIMPLE = "simple"  # 1-2 concepts, basic facts
    MODERATE = "moderate"  # 3-4 concepts, some depth
    COMPLEX = "complex"  # 5+ concepts, deep analysis
    EXPERT = "expert"  # Advanced concepts, multiple perspectives

class StoryFeasibility(Enum):
    """Story feasibility assessment"""
    HIGHLY_FEASIBLE = "highly_feasible"  # Easy to cover in 6-8 scenes
    FEASIBLE = "feasible"  # Can be covered with good planning
    CHALLENGING = "challenging"  # Needs careful scene selection
    NOT_FEASIBLE = "not_feasible"  # Too complex for short video

@dataclass
class HookTemplate:
    """Hook template for different topic categories"""
    category: str
    hook_type: str
    template: str
    effectiveness_score: int  # 1-10

@dataclass
class StoryValidationResult:
    """Result of story validation"""
    is_valid: bool
    complexity_level: ComplexityLevel
    feasibility: StoryFeasibility
    complexity_score: int  # 1-10
    scene_count_estimate: int
    suggested_simplifications: List[str]
    recommended_hooks: List[HookTemplate]
    validation_notes: List[str]

class StoryValidator:
    """Validates story scoping and provides complexity analysis"""
    
    def __init__(self):
        self.hook_library = self._initialize_hook_library()
        self.complexity_indicators = self._initialize_complexity_indicators()
        logger.info("StoryValidator initialized")
    
    def _initialize_hook_library(self) -> Dict[str, List[HookTemplate]]:
        """Initialize hook library by topic categories"""
        return {
            "business": [
                HookTemplate("business", "shocking_fact", "Did you know that {company} started with just ${amount} and now makes ${revenue} annually?", 9),
                HookTemplate("business", "statistic", "Every {timeframe}, {company} {impressive_action} - here's how they did it", 8),
                HookTemplate("business", "story", "In {year}, {person} had an idea that would change {industry} forever", 7)
            ],
            "technology": [
                HookTemplate("technology", "shocking_fact", "The technology you use every day was invented by accident in {year}", 9),
                HookTemplate("technology", "question", "What if I told you that {technology} works completely differently than you think?", 8),
                HookTemplate("technology", "statistic", "{technology} processes {amount} of data every second - here's how", 7)
            ],
            "science": [
                HookTemplate("science", "shocking_fact", "Scientists just discovered that {scientific_fact} - and it changes everything", 9),
                HookTemplate("science", "myth_busting", "Everything you know about {topic} is wrong - here's the truth", 8),
                HookTemplate("science", "statistic", "In the time it takes to {common_action}, {scientific_process} happens {number} times", 7)
            ],
            "history": [
                HookTemplate("history", "shocking_fact", "The real story of {historical_event} is nothing like what you learned in school", 9),
                HookTemplate("history", "story", "In {year}, {person} made a decision that would shape the world for centuries", 8),
                HookTemplate("history", "timeline", "From {start_year} to {end_year}, {topic} went through an incredible transformation", 7)
            ],
            "culture": [
                HookTemplate("culture", "shocking_fact", "The {cultural_phenomenon} you love actually started as {original_purpose}", 9),
                HookTemplate("culture", "story", "How {cultural_icon} went from {humble_beginning} to {global_success}", 8),
                HookTemplate("culture", "comparison", "While you see {surface_thing}, the real {cultural_phenomenon} is {deeper_meaning}", 7)
            ]
        }
    
    def _initialize_complexity_indicators(self) -> Dict[str, int]:
        """Initialize complexity indicators and their weights"""
        return {
            # High complexity indicators (weight: 3)
            "multiple_perspectives": 3,
            "technical_jargon": 3,
            "historical_context": 3,
            "scientific_principles": 3,
            "economic_factors": 3,
            
            # Medium complexity indicators (weight: 2)
            "timeline_span": 2,
            "multiple_characters": 2,
            "cause_and_effect": 2,
            "comparison_analysis": 2,
            "statistical_data": 2,
            
            # Low complexity indicators (weight: 1)
            "simple_facts": 1,
            "single_concept": 1,
            "visual_demonstration": 1,
            "personal_story": 1,
            "current_events": 1
        }
    
    def validate_story(self, subject: str, story: str, target_audience: str = "general") -> StoryValidationResult:
        """
        Validate story scoping and provide complexity analysis
        
        Args:
            subject: Original subject/topic
            story: The narrowed story
            target_audience: Target audience level
            
        Returns:
            StoryValidationResult with validation details
        """
        logger.info(f"Validating story: {story}")
        
        # Analyze complexity
        complexity_score = self._calculate_complexity_score(story, target_audience)
        complexity_level = self._determine_complexity_level(complexity_score)
        
        # Assess feasibility
        feasibility = self._assess_feasibility(complexity_score, story)
        
        # Estimate scene count
        scene_count_estimate = self._estimate_scene_count(complexity_score, story)
        
        # Generate suggestions
        simplifications = self._suggest_simplifications(story, complexity_score)
        recommended_hooks = self._recommend_hooks(subject, story)
        
        # Validation notes
        validation_notes = self._generate_validation_notes(story, complexity_score, feasibility)
        
        # Determine if story is valid
        is_valid = feasibility in [StoryFeasibility.HIGHLY_FEASIBLE, StoryFeasibility.FEASIBLE]
        
        result = StoryValidationResult(
            is_valid=is_valid,
            complexity_level=complexity_level,
            feasibility=feasibility,
            complexity_score=complexity_score,
            scene_count_estimate=scene_count_estimate,
            suggested_simplifications=simplifications,
            recommended_hooks=recommended_hooks,
            validation_notes=validation_notes
        )
        
        logger.info(f"Story validation complete: {complexity_level.value} complexity, {feasibility.value} feasibility")
        return result
    
    def _calculate_complexity_score(self, story: str, target_audience: str) -> int:
        """Calculate complexity score based on story content"""
        score = 0
        story_lower = story.lower()
        
        # Check for complexity indicators
        for indicator, weight in self.complexity_indicators.items():
            if self._check_indicator_presence(story_lower, indicator):
                score += weight
        
        # Adjust for target audience
        audience_multiplier = {
            "beginner": 1.5,
            "general": 1.0,
            "intermediate": 0.8,
            "expert": 0.6
        }.get(target_audience, 1.0)
        
        final_score = min(10, int(score * audience_multiplier))
        return max(1, final_score)
    
    def _check_indicator_presence(self, story: str, indicator: str) -> bool:
        """Check if a complexity indicator is present in the story"""
        indicator_patterns = {
            "multiple_perspectives": ["different", "various", "multiple", "several", "diverse"],
            "technical_jargon": ["algorithm", "methodology", "framework", "paradigm", "infrastructure"],
            "historical_context": ["century", "decade", "era", "period", "timeline", "evolution"],
            "scientific_principles": ["theory", "hypothesis", "research", "study", "experiment"],
            "economic_factors": ["market", "economy", "financial", "revenue", "profit", "investment"],
            "timeline_span": ["from", "to", "between", "over", "throughout", "during"],
            "multiple_characters": ["and", "with", "together", "collaboration", "partnership"],
            "cause_and_effect": ["because", "due to", "resulted in", "led to", "caused"],
            "comparison_analysis": ["compared to", "versus", "unlike", "similar to", "different from"],
            "statistical_data": ["percent", "%", "million", "billion", "statistics", "data"],
            "simple_facts": ["is", "are", "was", "were", "basic", "simple"],
            "single_concept": ["one", "single", "main", "primary", "key"],
            "visual_demonstration": ["show", "demonstrate", "visual", "see", "watch"],
            "personal_story": ["I", "my", "personal", "experience", "story"],
            "current_events": ["today", "now", "current", "recent", "latest"]
        }
        
        patterns = indicator_patterns.get(indicator, [])
        return any(pattern in story for pattern in patterns)
    
    def _determine_complexity_level(self, score: int) -> ComplexityLevel:
        """Determine complexity level based on score"""
        if score <= 3:
            return ComplexityLevel.SIMPLE
        elif score <= 6:
            return ComplexityLevel.MODERATE
        elif score <= 8:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.EXPERT
    
    def _assess_feasibility(self, complexity_score: int, story: str) -> StoryFeasibility:
        """Assess if story is feasible for 6-8 scene video"""
        # Check story length and complexity
        word_count = len(story.split())
        
        if complexity_score <= 4 and word_count <= 50:
            return StoryFeasibility.HIGHLY_FEASIBLE
        elif complexity_score <= 6 and word_count <= 100:
            return StoryFeasibility.FEASIBLE
        elif complexity_score <= 8 and word_count <= 150:
            return StoryFeasibility.CHALLENGING
        else:
            return StoryFeasibility.NOT_FEASIBLE
    
    def _estimate_scene_count(self, complexity_score: int, story: str) -> int:
        """Estimate required scene count based on complexity"""
        base_scenes = 6
        complexity_adjustment = (complexity_score - 5) * 0.5
        word_count_adjustment = len(story.split()) / 20
        
        estimated = base_scenes + complexity_adjustment + word_count_adjustment
        return min(10, max(4, int(estimated)))
    
    def _suggest_simplifications(self, story: str, complexity_score: int) -> List[str]:
        """Suggest simplifications for complex stories"""
        suggestions = []
        
        if complexity_score > 7:
            suggestions.append("Focus on a single aspect or time period")
            suggestions.append("Reduce the number of characters or concepts")
            suggestions.append("Simplify technical language for general audience")
        
        if complexity_score > 5:
            suggestions.append("Choose one main perspective instead of multiple viewpoints")
            suggestions.append("Focus on key facts rather than comprehensive coverage")
        
        if "timeline" in story.lower() or "evolution" in story.lower():
            suggestions.append("Pick 2-3 key moments instead of covering entire timeline")
        
        if "multiple" in story.lower() or "various" in story.lower():
            suggestions.append("Focus on one primary example instead of multiple cases")
        
        return suggestions
    
    def _recommend_hooks(self, subject: str, story: str) -> List[HookTemplate]:
        """Recommend hooks based on subject and story"""
        # Determine topic category
        category = self._categorize_topic(subject, story)
        
        # Get hooks for category
        category_hooks = self.hook_library.get(category, self.hook_library["business"])
        
        # Return top 3 hooks
        return sorted(category_hooks, key=lambda x: x.effectiveness_score, reverse=True)[:3]
    
    def _categorize_topic(self, subject: str, story: str) -> str:
        """Categorize topic for hook selection"""
        text = f"{subject} {story}".lower()
        
        if any(word in text for word in ["business", "company", "startup", "entrepreneur", "market"]):
            return "business"
        elif any(word in text for word in ["technology", "tech", "software", "ai", "digital"]):
            return "technology"
        elif any(word in text for word in ["science", "research", "study", "experiment", "theory"]):
            return "science"
        elif any(word in text for word in ["history", "historical", "century", "era", "timeline"]):
            return "history"
        elif any(word in text for word in ["culture", "music", "art", "entertainment", "social"]):
            return "culture"
        else:
            return "business"  # Default category
    
    def _generate_validation_notes(self, story: str, complexity_score: int, feasibility: StoryFeasibility) -> List[str]:
        """Generate validation notes and recommendations"""
        notes = []
        
        if feasibility == StoryFeasibility.HIGHLY_FEASIBLE:
            notes.append("✅ Story is well-scoped and perfect for short video format")
            notes.append("✅ Complexity level is appropriate for target audience")
        elif feasibility == StoryFeasibility.FEASIBLE:
            notes.append("✅ Story is feasible with good scene planning")
            notes.append("⚠️ Consider simplifying some aspects for better flow")
        elif feasibility == StoryFeasibility.CHALLENGING:
            notes.append("⚠️ Story is challenging but manageable with careful planning")
            notes.append("⚠️ Consider reducing scope or focusing on key aspects")
        else:
            notes.append("❌ Story is too complex for 6-8 scene format")
            notes.append("❌ Strongly recommend simplifying or choosing different angle")
        
        if complexity_score > 6:
            notes.append("💡 Consider using more visual demonstrations")
            notes.append("💡 Break down complex concepts into simpler parts")
        
        return notes

# Test function
def test_story_validator():
    """Test the StoryValidator"""
    validator = StoryValidator()
    
    # Test cases
    test_cases = [
        ("Elon Musk", "How Elon Musk bought a house in Austin and moved Tesla headquarters there"),
        ("Machine Learning", "How Netflix uses machine learning to recommend movies you'll love"),
        ("Climate Change", "How a small island nation is fighting rising sea levels with innovative solutions"),
        ("music industry", "How BTS broke into the American market and changed music industry forever")
    ]
    
    for subject, story in test_cases:
        print(f"\n🔍 Validating: {subject}")
        print(f"📖 Story: {story}")
        
        result = validator.validate_story(subject, story)
        
        print(f"✅ Valid: {result.is_valid}")
        print(f"📊 Complexity: {result.complexity_level.value} (Score: {result.complexity_score})")
        print(f"🎯 Feasibility: {result.feasibility.value}")
        print(f"🎬 Estimated scenes: {result.scene_count_estimate}")
        print(f"💡 Suggestions: {result.suggested_simplifications}")
        print(f"🎣 Recommended hooks: {[hook.template for hook in result.recommended_hooks]}")

if __name__ == "__main__":
    test_story_validator()
