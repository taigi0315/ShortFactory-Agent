"""
Shared Context Object for Agent Communication
Maintains consistency across agents and scenes
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class VisualStyle(Enum):
    """Visual style consistency markers"""
    MODERN = "modern"
    VINTAGE = "vintage"
    MINIMALIST = "minimalist"
    DETAILED = "detailed"
    CARTOON = "cartoon"
    REALISTIC = "realistic"

class NarrativeMomentum(Enum):
    """Narrative arc progression tracking"""
    BUILDING = "building"
    PEAK = "peak"
    RESOLVING = "resolving"
    MAINTAINING = "maintaining"

@dataclass
class CharacterState:
    """Character consistency details across scenes"""
    current_emotion: str
    current_pose: str
    knowledge_level: str  # "beginner", "intermediate", "expert"
    energy_level: int  # 1-10 scale
    last_interaction: Optional[str] = None
    established_traits: Set[str] = field(default_factory=set)

@dataclass
class VisualElement:
    """Visual elements introduced in scenes"""
    element_type: str  # "chart", "diagram", "infographic", "timeline"
    content: str
    scene_number: int
    color_scheme: Optional[str] = None
    position: Optional[str] = None

@dataclass
class InformativeFact:
    """Facts/statistics used to avoid repetition"""
    fact: str
    scene_number: int
    category: str  # "statistic", "example", "concept", "definition"
    complexity_level: int  # 1-5 scale

@dataclass
class SharedContext:
    """
    Shared context object that maintains consistency across agents and scenes
    """
    # Character consistency
    character_state: CharacterState
    
    # Visual style continuity
    visual_style: VisualStyle
    color_palette: List[str]
    
    # Narrative arc progression
    narrative_momentum: NarrativeMomentum
    story_arc_position: float  # 0.0 to 1.0 (beginning to end)
    
    # Technical constraints
    target_audience: str
    video_duration_target: int  # seconds
    scene_count: int
    
    # Optional fields with defaults
    established_visual_elements: List[VisualElement] = field(default_factory=list)
    established_facts: List[InformativeFact] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    complexity_progression: List[int] = field(default_factory=list)
    previous_scene_summary: Optional[str] = None
    next_scene_hints: List[str] = field(default_factory=list)
    
    def add_visual_element(self, element: VisualElement) -> None:
        """Add a visual element to maintain consistency"""
        self.established_visual_elements.append(element)
        logger.debug(f"Added visual element: {element.element_type} in scene {element.scene_number}")
    
    def add_informative_fact(self, fact: InformativeFact) -> None:
        """Add an informative fact to avoid repetition"""
        self.established_facts.append(fact)
        logger.debug(f"Added informative fact: {fact.category} in scene {fact.scene_number}")
    
    def update_character_state(self, emotion: str, pose: str, knowledge_level: str = None, energy_level: int = None) -> None:
        """Update character state for consistency"""
        self.character_state.current_emotion = emotion
        self.character_state.current_pose = pose
        if knowledge_level:
            self.character_state.knowledge_level = knowledge_level
        if energy_level:
            self.character_state.energy_level = energy_level
        logger.debug(f"Updated character state: {emotion}, {pose}")
    
    def check_fact_repetition(self, new_fact: str, category: str) -> bool:
        """Check if a fact has been used recently to avoid repetition"""
        recent_scenes = max(1, len(self.established_facts) - 3)  # Check last 3 scenes
        for fact in self.established_facts[-recent_scenes:]:
            if fact.category == category and fact.fact.lower() in new_fact.lower():
                return True
        return False
    
    def get_visual_consistency_guidelines(self) -> Dict[str, Any]:
        """Get visual consistency guidelines for scene generation"""
        return {
            "style": self.visual_style.value,
            "color_palette": self.color_palette,
            "established_elements": [elem.element_type for elem in self.established_visual_elements[-3:]],
            "character_state": {
                "emotion": self.character_state.current_emotion,
                "pose": self.character_state.current_pose,
                "energy_level": self.character_state.energy_level
            }
        }
    
    def get_informative_continuity_guidelines(self) -> Dict[str, Any]:
        """Get informative continuity guidelines for scene generation"""
        return {
            "learning_objectives": self.learning_objectives,
            "complexity_progression": self.complexity_progression,
            "recent_facts": [fact.fact for fact in self.established_facts[-2:]],
            "target_audience": self.target_audience
        }
    
    def update_narrative_momentum(self, scene_number: int, total_scenes: int) -> None:
        """Update narrative momentum based on scene position"""
        self.story_arc_position = scene_number / total_scenes
        
        if self.story_arc_position < 0.3:
            self.narrative_momentum = NarrativeMomentum.BUILDING
        elif self.story_arc_position < 0.7:
            self.narrative_momentum = NarrativeMomentum.PEAK
        else:
            self.narrative_momentum = NarrativeMomentum.RESOLVING
        
        logger.debug(f"Updated narrative momentum: {self.narrative_momentum.value} at position {self.story_arc_position:.2f}")
    
    def get_scene_context_for_writer(self, scene_number: int, scene_type: str) -> Dict[str, Any]:
        """Get comprehensive context for scene writer"""
        return {
            "scene_number": scene_number,
            "scene_type": scene_type,
            "character_consistency": {
                "current_emotion": self.character_state.current_emotion,
                "current_pose": self.character_state.current_pose,
                "knowledge_level": self.character_state.knowledge_level,
                "energy_level": self.character_state.energy_level,
                "established_traits": list(self.character_state.established_traits)
            },
            "visual_consistency": self.get_visual_consistency_guidelines(),
            "informative_continuity": self.get_informative_continuity_guidelines(),
            "narrative_context": {
                "momentum": self.narrative_momentum.value,
                "arc_position": self.story_arc_position,
                "previous_scene": self.previous_scene_summary,
                "next_scene_hints": self.next_scene_hints
            },
            "technical_constraints": {
                "target_audience": self.target_audience,
                "video_duration_target": self.video_duration_target,
                "scene_count": self.scene_count
            }
        }

class SharedContextManager:
    """Manager for shared context across agents"""
    
    def __init__(self):
        self.context: Optional[SharedContext] = None
        logger.info("SharedContextManager initialized")
    
    def create_context(self, 
                      character_emotion: str = "excited",
                      character_pose: str = "pointing",
                      visual_style: VisualStyle = VisualStyle.MODERN,
                      color_palette: List[str] = None,
                      target_audience: str = "general",
                      video_duration: int = 60,
                      scene_count: int = 6) -> SharedContext:
        """Create a new shared context"""
        
        if color_palette is None:
            color_palette = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
        
        character_state = CharacterState(
            current_emotion=character_emotion,
            current_pose=character_pose,
            knowledge_level="beginner",
            energy_level=8
        )
        
        self.context = SharedContext(
            character_state=character_state,
            visual_style=visual_style,
            color_palette=color_palette,
            narrative_momentum=NarrativeMomentum.BUILDING,
            story_arc_position=0.0,
            target_audience=target_audience,
            video_duration_target=video_duration,
            scene_count=scene_count
        )
        
        logger.info(f"Created shared context with {visual_style.value} style and {target_audience} audience")
        return self.context
    
    def get_context(self) -> Optional[SharedContext]:
        """Get current shared context"""
        return self.context
    
    def update_context_after_scene(self, scene_number: int, scene_data: Dict[str, Any]) -> None:
        """Update context after a scene is generated"""
        if not self.context:
            logger.warning("No shared context available for update")
            return
        
        # Update character state
        if "character_expression" in scene_data and "character_pose" in scene_data:
            self.context.update_character_state(
                emotion=scene_data["character_expression"],
                pose=scene_data["character_pose"]
            )
        
        # Add visual elements
        if "image_create_prompt" in scene_data:
            visual_element = VisualElement(
                element_type="scene_content",
                content=scene_data["image_create_prompt"],
                scene_number=scene_number
            )
            self.context.add_visual_element(visual_element)
        
        # Add informative facts
        if "informative_content" in scene_data:
            for category, facts in scene_data["informative_content"].items():
                for fact in facts:
                    informative_fact = InformativeFact(
                        fact=fact,
                        scene_number=scene_number,
                        category=category,
                        complexity_level=3  # Default complexity
                    )
                    self.context.add_informative_fact(informative_fact)
        
        # Update narrative momentum
        self.context.update_narrative_momentum(scene_number, self.context.scene_count)
        
        # Update previous scene summary
        if "dialogue" in scene_data:
            self.context.previous_scene_summary = scene_data["dialogue"]
        
        logger.info(f"Updated shared context after scene {scene_number}")
    
    def reset_context(self) -> None:
        """Reset shared context"""
        self.context = None
        logger.info("Shared context reset")
