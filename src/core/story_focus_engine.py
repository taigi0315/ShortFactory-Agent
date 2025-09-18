"""
Story Focus Engine
Ensures stories are specific and engaging with focus patterns
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import random

logger = logging.getLogger(__name__)

class FocusPattern(Enum):
    """Story focus patterns for specific, engaging narratives"""
    ORIGIN_STORY = "origin_story"
    TURNING_POINT = "turning_point"
    SPECIFIC_INNOVATION = "specific_innovation"
    BEHIND_SCENES = "behind_scenes"
    MISCONCEPTION = "misconception"
    SPECIFIC_PERSON = "specific_person"
    SPECIFIC_EVENT = "specific_event"
    SECRET_REVEAL = "secret_reveal"
    CONTROVERSY = "controversy"
    UNEXPECTED_CONNECTION = "unexpected_connection"

@dataclass
class FocusPatternTemplate:
    """Template for story focus patterns"""
    pattern: FocusPattern
    template: str
    engagement_score: int  # 1-10
    specificity_score: int  # 1-10
    informative_value: int  # 1-10
    target_keywords: List[str]

@dataclass
class StoryFocusResult:
    """Result of story focus refinement"""
    original_story: str
    focused_story: str
    applied_pattern: FocusPattern
    focus_score: float  # 0.0 to 1.0
    engagement_improvement: float  # 0.0 to 1.0
    specificity_improvement: float  # 0.0 to 1.0
    suggested_angles: List[str]

class StoryFocusEngine:
    """Engine to ensure stories are specific and engaging"""
    
    def __init__(self):
        self.focus_patterns = self._initialize_focus_patterns()
        self.broadness_indicators = self._initialize_broadness_indicators()
        self.specificity_boosters = self._initialize_specificity_boosters()
        logger.info("StoryFocusEngine initialized")
    
    def _initialize_focus_patterns(self) -> Dict[FocusPattern, FocusPatternTemplate]:
        """Initialize focus patterns with templates and scores"""
        return {
            FocusPattern.ORIGIN_STORY: FocusPatternTemplate(
                pattern=FocusPattern.ORIGIN_STORY,
                template="The untold story of how {subject} was accidentally discovered by {person} in {year}",
                engagement_score=9,
                specificity_score=8,
                informative_value=8,
                target_keywords=["discovered", "invented", "created", "founded", "started"]
            ),
            FocusPattern.TURNING_POINT: FocusPatternTemplate(
                pattern=FocusPattern.TURNING_POINT,
                template="The {timeframe} that changed {subject} forever and why it almost failed",
                engagement_score=8,
                specificity_score=7,
                informative_value=7,
                target_keywords=["changed", "turning point", "breakthrough", "revolution", "transformation"]
            ),
            FocusPattern.SPECIFIC_INNOVATION: FocusPatternTemplate(
                pattern=FocusPattern.SPECIFIC_INNOVATION,
                template="The one {innovation_type} that made {subject} possible and how it works",
                engagement_score=7,
                specificity_score=9,
                informative_value=9,
                target_keywords=["innovation", "technology", "method", "technique", "breakthrough"]
            ),
            FocusPattern.BEHIND_SCENES: FocusPatternTemplate(
                pattern=FocusPattern.BEHIND_SCENES,
                template="What really happens inside {subject} that nobody talks about",
                engagement_score=9,
                specificity_score=6,
                informative_value=6,
                target_keywords=["behind", "inside", "secret", "hidden", "unknown"]
            ),
            FocusPattern.MISCONCEPTION: FocusPatternTemplate(
                pattern=FocusPattern.MISCONCEPTION,
                template="Why everything you know about {subject} is wrong and the real truth",
                engagement_score=10,
                specificity_score=7,
                informative_value=8,
                target_keywords=["wrong", "myth", "misconception", "truth", "reality"]
            ),
            FocusPattern.SPECIFIC_PERSON: FocusPatternTemplate(
                pattern=FocusPattern.SPECIFIC_PERSON,
                template="The unknown genius who actually created {subject} and their incredible story",
                engagement_score=8,
                specificity_score=8,
                informative_value=7,
                target_keywords=["person", "genius", "creator", "inventor", "founder"]
            ),
            FocusPattern.SPECIFIC_EVENT: FocusPatternTemplate(
                pattern=FocusPattern.SPECIFIC_EVENT,
                template="The day {subject} almost failed completely and how it was saved",
                engagement_score=9,
                specificity_score=8,
                informative_value=6,
                target_keywords=["failed", "crisis", "disaster", "saved", "recovery"]
            ),
            FocusPattern.SECRET_REVEAL: FocusPatternTemplate(
                pattern=FocusPattern.SECRET_REVEAL,
                template="The secret {aspect} of {subject} that {company/person} doesn't want you to know",
                engagement_score=10,
                specificity_score=6,
                informative_value=7,
                target_keywords=["secret", "hidden", "confidential", "classified", "revealed"]
            ),
            FocusPattern.CONTROVERSY: FocusPatternTemplate(
                pattern=FocusPattern.CONTROVERSY,
                template="The controversial {aspect} of {subject} that divided {community/industry}",
                engagement_score=9,
                specificity_score=7,
                informative_value=8,
                target_keywords=["controversial", "debate", "divided", "conflict", "disagreement"]
            ),
            FocusPattern.UNEXPECTED_CONNECTION: FocusPatternTemplate(
                pattern=FocusPattern.UNEXPECTED_CONNECTION,
                template="How {subject} is secretly connected to {unexpected_thing} and why it matters",
                engagement_score=8,
                specificity_score=7,
                informative_value=7,
                target_keywords=["connected", "linked", "related", "influence", "impact"]
            )
        }
    
    def _initialize_broadness_indicators(self) -> List[str]:
        """Initialize indicators that suggest a story is too broad"""
        return [
            "overview", "introduction", "basics", "fundamentals", "general",
            "everything about", "all about", "complete guide", "comprehensive",
            "history of", "evolution of", "development of", "growth of",
            "understanding", "learning about", "exploring", "discovering"
        ]
    
    def _initialize_specificity_boosters(self) -> Dict[str, List[str]]:
        """Initialize words that boost specificity"""
        return {
            "time": ["specific", "exact", "precise", "particular", "certain"],
            "place": ["location", "exact", "specific", "particular", "precise"],
            "person": ["specific", "particular", "exact", "individual", "named"],
            "event": ["specific", "particular", "exact", "precise", "certain"],
            "number": ["exact", "precise", "specific", "particular", "certain"],
            "detail": ["specific", "particular", "exact", "precise", "detailed"]
        }
    
    def refine_story_focus(self, broad_subject: str, initial_story: str, target_audience: str = "general") -> StoryFocusResult:
        """
        Refine story to be more specific and engaging
        
        Args:
            broad_subject: The original broad subject
            initial_story: The initial story attempt
            target_audience: Target audience for the story
            
        Returns:
            StoryFocusResult with refined story and analysis
        """
        logger.info(f"Refining story focus for subject: {broad_subject}")
        
        # Analyze current story broadness
        broadness_score = self._calculate_broadness_score(initial_story)
        specificity_score = self._calculate_specificity_score(initial_story)
        engagement_score = self._calculate_engagement_score(initial_story)
        
        # If story is already specific enough, return as is
        if broadness_score < 0.3 and specificity_score > 0.7:
            logger.info("Story is already well-focused")
            return StoryFocusResult(
                original_story=initial_story,
                focused_story=initial_story,
                applied_pattern=FocusPattern.ORIGIN_STORY,  # Default
                focus_score=0.8,
                engagement_improvement=0.0,
                specificity_improvement=0.0,
                suggested_angles=[]
            )
        
        # Find best focus pattern
        best_pattern = self._select_best_focus_pattern(broad_subject, initial_story, target_audience)
        
        # Apply focus pattern
        focused_story = self._apply_focus_pattern(broad_subject, initial_story, best_pattern)
        
        # Calculate improvements
        new_specificity_score = self._calculate_specificity_score(focused_story)
        new_engagement_score = self._calculate_engagement_score(focused_story)
        
        specificity_improvement = new_specificity_score - specificity_score
        engagement_improvement = new_engagement_score - engagement_score
        
        # Generate alternative angles
        suggested_angles = self._generate_alternative_angles(broad_subject, best_pattern)
        
        result = StoryFocusResult(
            original_story=initial_story,
            focused_story=focused_story,
            applied_pattern=best_pattern,
            focus_score=(new_specificity_score + new_engagement_score) / 2,
            engagement_improvement=engagement_improvement,
            specificity_improvement=specificity_improvement,
            suggested_angles=suggested_angles
        )
        
        logger.info(f"Story focus refined: {best_pattern.value} pattern applied")
        return result
    
    def _calculate_broadness_score(self, story: str) -> float:
        """Calculate how broad a story is (0.0 = very specific, 1.0 = very broad)"""
        story_lower = story.lower()
        broadness_count = sum(1 for indicator in self.broadness_indicators if indicator in story_lower)
        
        # Normalize by story length
        word_count = len(story.split())
        broadness_score = min(1.0, broadness_count / max(1, word_count / 10))
        
        return broadness_score
    
    def _calculate_specificity_score(self, story: str) -> float:
        """Calculate how specific a story is (0.0 = very broad, 1.0 = very specific)"""
        story_lower = story.lower()
        specificity_count = 0
        
        # Count specificity indicators
        for category, boosters in self.specificity_boosters.items():
            specificity_count += sum(1 for booster in boosters if booster in story_lower)
        
        # Count specific elements (numbers, names, dates, places)
        import re
        numbers = len(re.findall(r'\d+', story))
        capitalized_words = len(re.findall(r'\b[A-Z][a-z]+\b', story))
        
        specificity_count += numbers + capitalized_words
        
        # Normalize by story length
        word_count = len(story.split())
        specificity_score = min(1.0, specificity_count / max(1, word_count / 5))
        
        return specificity_score
    
    def _calculate_engagement_score(self, story: str) -> float:
        """Calculate engagement potential of a story (0.0 = boring, 1.0 = very engaging)"""
        story_lower = story.lower()
        engagement_count = 0
        
        # Count engagement words
        engagement_words = [
            "secret", "hidden", "unknown", "surprising", "shocking", "incredible",
            "amazing", "unbelievable", "controversial", "scandal", "crisis",
            "breakthrough", "revolutionary", "game-changing", "life-changing",
            "dramatic", "intense", "explosive", "revealing", "exclusive"
        ]
        
        engagement_count = sum(1 for word in engagement_words if word in story_lower)
        
        # Count question words (indicating curiosity)
        question_words = ["how", "why", "what", "when", "where", "who"]
        engagement_count += sum(1 for word in question_words if word in story_lower)
        
        # Normalize by story length
        word_count = len(story.split())
        engagement_score = min(1.0, engagement_count / max(1, word_count / 8))
        
        return engagement_score
    
    def _select_best_focus_pattern(self, subject: str, story: str, target_audience: str) -> FocusPattern:
        """Select the best focus pattern for the subject and story"""
        subject_lower = subject.lower()
        story_lower = story.lower()
        
        # Score each pattern based on subject and story content
        pattern_scores = {}
        
        for pattern, template in self.focus_patterns.items():
            score = 0
            
            # Check if subject matches pattern keywords
            for keyword in template.target_keywords:
                if keyword in subject_lower or keyword in story_lower:
                    score += 2
            
            # Add base scores
            score += template.engagement_score
            score += template.specificity_score
            score += template.informative_value
            
            # Adjust for target audience
            if target_audience == "beginner":
                score += template.informative_value  # Prioritize informative value
            elif target_audience == "expert":
                score += template.specificity_score  # Prioritize specificity
            
            pattern_scores[pattern] = score
        
        # Select pattern with highest score
        best_pattern = max(pattern_scores, key=pattern_scores.get)
        
        # Add some randomness to avoid always picking the same pattern
        top_patterns = sorted(pattern_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        if len(top_patterns) > 1 and top_patterns[0][1] - top_patterns[1][1] < 5:
            # If scores are close, randomly select from top 3
            best_pattern = random.choice(top_patterns)[0]
        
        return best_pattern
    
    def _apply_focus_pattern(self, subject: str, initial_story: str, pattern: FocusPattern) -> str:
        """Apply focus pattern to create a more specific story"""
        template = self.focus_patterns[pattern]
        
        # Extract key elements from subject and initial story
        key_elements = self._extract_key_elements(subject, initial_story)
        
        # Apply template with extracted elements
        focused_story = template.template.format(
            subject=subject,
            **key_elements
        )
        
        # Enhance with specific details if available
        if key_elements.get("person"):
            focused_story += f" Meet {key_elements['person']}, the {self._get_person_descriptor(key_elements['person'])}."
        
        if key_elements.get("year"):
            focused_story += f" This happened in {key_elements['year']}, a time when {self._get_historical_context(key_elements['year'])}."
        
        if key_elements.get("place"):
            focused_story += f" The setting? {key_elements['place']}, where {self._get_place_context(key_elements['place'])}."
        
        return focused_story
    
    def _extract_key_elements(self, subject: str, story: str) -> Dict[str, str]:
        """Extract key elements from subject and story for pattern application"""
        elements = {}
        
        # Extract person names (capitalized words that might be names)
        import re
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', story)
        if capitalized_words:
            elements["person"] = capitalized_words[0]  # Take first capitalized word as person
        
        # Extract years (4-digit numbers)
        years = re.findall(r'\b(19|20)\d{2}\b', story)
        if years:
            elements["year"] = years[0]
        
        # Extract places (common place indicators)
        place_indicators = ["in", "at", "from", "to"]
        words = story.split()
        for i, word in enumerate(words):
            if word.lower() in place_indicators and i + 1 < len(words):
                elements["place"] = words[i + 1]
                break
        
        # Extract innovation types
        innovation_types = ["technology", "method", "technique", "system", "approach", "solution"]
        for innovation in innovation_types:
            if innovation in story.lower():
                elements["innovation_type"] = innovation
                break
        
        # Extract timeframes
        timeframes = ["moment", "day", "week", "month", "year", "decade", "century"]
        for timeframe in timeframes:
            if timeframe in story.lower():
                elements["timeframe"] = timeframe
                break
        
        # Extract aspects
        aspects = ["secret", "hidden", "controversial", "unknown", "behind-the-scenes"]
        for aspect in aspects:
            if aspect in story.lower():
                elements["aspect"] = aspect
                break
        
        return elements
    
    def _get_person_descriptor(self, person: str) -> str:
        """Get a descriptor for a person"""
        descriptors = [
            "brilliant mind", "innovative thinker", "visionary", "pioneer",
            "genius", "trailblazer", "revolutionary", "game-changer"
        ]
        return random.choice(descriptors)
    
    def _get_historical_context(self, year: str) -> str:
        """Get historical context for a year"""
        year_int = int(year)
        if year_int < 1900:
            return "the world was very different"
        elif year_int < 1950:
            return "technology was just beginning to change everything"
        elif year_int < 2000:
            return "the digital revolution was taking shape"
        else:
            return "the internet age was transforming society"
    
    def _get_place_context(self, place: str) -> str:
        """Get context for a place"""
        contexts = {
            "silicon valley": "innovation happens",
            "new york": "big dreams come true",
            "california": "the future is built",
            "london": "history meets innovation",
            "tokyo": "tradition meets technology"
        }
        return contexts.get(place.lower(), "important things happen")
    
    def _generate_alternative_angles(self, subject: str, applied_pattern: FocusPattern) -> List[str]:
        """Generate alternative story angles for the same subject"""
        alternatives = []
        
        # Get other patterns that could work for this subject
        for pattern, template in self.focus_patterns.items():
            if pattern != applied_pattern:
                # Check if pattern could work for this subject
                if any(keyword in subject.lower() for keyword in template.target_keywords):
                    alternative_story = template.template.format(subject=subject)
                    alternatives.append(alternative_story)
        
        # Limit to top 3 alternatives
        return alternatives[:3]
    
    def analyze_story_potential(self, subject: str, story: str) -> Dict[str, Any]:
        """Analyze the potential of a story for video creation"""
        broadness_score = self._calculate_broadness_score(story)
        specificity_score = self._calculate_specificity_score(story)
        engagement_score = self._calculate_engagement_score(story)
        
        # Calculate overall potential
        overall_potential = (specificity_score + engagement_score - broadness_score) / 2
        
        # Determine recommendations
        recommendations = []
        if broadness_score > 0.5:
            recommendations.append("Story is too broad - needs more specific focus")
        if specificity_score < 0.4:
            recommendations.append("Story lacks specific details - add names, dates, places")
        if engagement_score < 0.3:
            recommendations.append("Story needs more engaging elements - add surprises, secrets, drama")
        
        return {
            "overall_potential": overall_potential,
            "broadness_score": broadness_score,
            "specificity_score": specificity_score,
            "engagement_score": engagement_score,
            "recommendations": recommendations,
            "needs_refinement": overall_potential < 0.6
        }

# Test function
def test_story_focus_engine():
    """Test the StoryFocusEngine"""
    engine = StoryFocusEngine()
    
    # Test cases
    test_cases = [
        ("the company", "The history of the company and how it became popular"),
        ("Tesla", "How Tesla is changing the automotive industry"),
        ("Netflix", "The story of Netflix and streaming services"),
        ("BTS", "How BTS became popular in the music industry")
    ]
    
    for subject, initial_story in test_cases:
        print(f"\n🔍 Testing: {subject}")
        print(f"📖 Initial story: {initial_story}")
        
        result = engine.refine_story_focus(subject, initial_story)
        
        print(f"✅ Focused story: {result.focused_story}")
        print(f"🎯 Applied pattern: {result.applied_pattern.value}")
        print(f"📊 Focus score: {result.focus_score:.2f}")
        print(f"📈 Improvements: Specificity +{result.specificity_improvement:.2f}, Engagement +{result.engagement_improvement:.2f}")
        
        if result.suggested_angles:
            print(f"💡 Alternative angles:")
            for i, angle in enumerate(result.suggested_angles, 1):
                print(f"   {i}. {angle}")

if __name__ == "__main__":
    test_story_focus_engine()
