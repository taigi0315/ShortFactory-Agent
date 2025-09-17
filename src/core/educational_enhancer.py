"""
Educational Depth Enhancement
Enhances educational prompts with specific elements, data points, and visual metaphors
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)

class EducationalElementType(Enum):
    """Types of educational elements"""
    DATA_POINT = "data_point"
    KEY_CONCEPT = "key_concept"
    VISUAL_METAPHOR = "visual_metaphor"
    INFORMATION_HIERARCHY = "information_hierarchy"
    LEARNING_OBJECTIVE = "learning_objective"
    ASSESSMENT_CRITERIA = "assessment_criteria"

@dataclass
class EducationalElement:
    """Represents an educational element"""
    element_type: EducationalElementType
    content: str
    importance_level: int  # 1-5 scale
    visual_complexity: int  # 1-5 scale
    target_audience: str
    learning_objective: str

@dataclass
class EnhancedEducationalContent:
    """Enhanced educational content with depth and specificity"""
    original_content: str
    enhanced_elements: List[EducationalElement]
    data_points: List[str]
    key_concepts: List[str]
    visual_metaphors: List[str]
    information_hierarchy: Dict[str, List[str]]
    learning_objectives: List[str]
    assessment_criteria: List[str]
    complexity_score: float  # 0.0 to 1.0
    educational_density: float  # 0.0 to 1.0

class EducationalEnhancer:
    """Enhances educational content with depth and specificity"""
    
    def __init__(self):
        self.data_extraction_patterns = self._initialize_data_patterns()
        self.concept_extraction_patterns = self._initialize_concept_patterns()
        self.metaphor_templates = self._initialize_metaphor_templates()
        self.hierarchy_templates = self._initialize_hierarchy_templates()
        logger.info("EducationalEnhancer initialized")
    
    def _initialize_data_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for extracting data points"""
        return {
            "numbers": [r'\d+', r'\d+\.\d+', r'\d+%', r'\d+/\d+'],
            "percentages": [r'\d+%', r'\d+\.\d+%'],
            "currency": [r'\$\d+', r'\$\d+\.\d+', r'\d+ dollars', r'\d+ USD'],
            "dates": [r'\d{4}', r'\d{1,2}/\d{1,2}/\d{4}', r'\d{1,2}-\d{1,2}-\d{4}'],
            "quantities": [r'\d+ million', r'\d+ billion', r'\d+ thousand', r'\d+ units'],
            "ratios": [r'\d+:\d+', r'\d+ to \d+', r'\d+ out of \d+'],
            "statistics": [r'\d+% of', r'\d+ times', r'\d+x', r'\d+ times more']
        }
    
    def _initialize_concept_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for extracting key concepts"""
        return {
            "processes": ["process", "method", "technique", "approach", "system", "workflow"],
            "principles": ["principle", "theory", "concept", "idea", "notion", "framework"],
            "technologies": ["technology", "innovation", "invention", "development", "advancement"],
            "strategies": ["strategy", "plan", "approach", "method", "tactic", "technique"],
            "phenomena": ["phenomenon", "trend", "pattern", "behavior", "characteristic", "feature"]
        }
    
    def _initialize_metaphor_templates(self) -> Dict[str, List[str]]:
        """Initialize templates for visual metaphors"""
        return {
            "growth": [
                "like a growing tree with branches representing different aspects",
                "as a rising mountain showing progression and achievement",
                "like a blooming flower with petals representing different elements"
            ],
            "connection": [
                "as a web of interconnected nodes showing relationships",
                "like a network of roads connecting different destinations",
                "as a puzzle where pieces fit together to form the complete picture"
            ],
            "transformation": [
                "like a caterpillar becoming a butterfly showing change",
                "as a seed growing into a plant representing development",
                "like a phoenix rising from ashes symbolizing renewal"
            ],
            "comparison": [
                "as a scale balancing different options",
                "like a race between competitors showing differences",
                "as a bridge connecting two different worlds"
            ],
            "process": [
                "like a factory assembly line showing step-by-step production",
                "as a recipe with ingredients and cooking steps",
                "like a journey with milestones and destinations"
            ]
        }
    
    def _initialize_hierarchy_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize templates for information hierarchy"""
        return {
            "pyramid": {
                "top": ["main concept", "primary goal", "core idea"],
                "middle": ["supporting concepts", "key principles", "important factors"],
                "bottom": ["foundational elements", "basic components", "essential details"]
            },
            "flow": {
                "start": ["beginning", "origin", "starting point"],
                "middle": ["development", "process", "transformation"],
                "end": ["result", "outcome", "conclusion"]
            },
            "tree": {
                "root": ["foundation", "base", "core"],
                "trunk": ["main structure", "primary support", "central element"],
                "branches": ["sub-categories", "related concepts", "extensions"],
                "leaves": ["specific details", "examples", "applications"]
            }
        }
    
    def enhance_educational_content(self, scene_data: Dict[str, Any], target_audience: str = "general") -> EnhancedEducationalContent:
        """
        Enhance educational content with depth and specificity
        
        Args:
            scene_data: Scene data containing educational content
            target_audience: Target audience for the content
            
        Returns:
            EnhancedEducationalContent with enhanced elements
        """
        logger.info(f"Enhancing educational content for audience: {target_audience}")
        
        # Extract original content
        original_content = self._extract_original_content(scene_data)
        
        # Extract and enhance different types of educational elements
        data_points = self._extract_data_points(original_content)
        key_concepts = self._extract_key_concepts(original_content)
        visual_metaphors = self._generate_visual_metaphors(original_content, key_concepts)
        information_hierarchy = self._create_information_hierarchy(original_content, key_concepts)
        learning_objectives = self._generate_learning_objectives(original_content, target_audience)
        assessment_criteria = self._generate_assessment_criteria(original_content, target_audience)
        
        # Create enhanced elements
        enhanced_elements = self._create_enhanced_elements(
            data_points, key_concepts, visual_metaphors, 
            information_hierarchy, learning_objectives, assessment_criteria,
            target_audience
        )
        
        # Calculate complexity and density scores
        complexity_score = self._calculate_complexity_score(enhanced_elements, target_audience)
        educational_density = self._calculate_educational_density(enhanced_elements)
        
        result = EnhancedEducationalContent(
            original_content=original_content,
            enhanced_elements=enhanced_elements,
            data_points=data_points,
            key_concepts=key_concepts,
            visual_metaphors=visual_metaphors,
            information_hierarchy=information_hierarchy,
            learning_objectives=learning_objectives,
            assessment_criteria=assessment_criteria,
            complexity_score=complexity_score,
            educational_density=educational_density
        )
        
        logger.info(f"Educational content enhanced: {len(enhanced_elements)} elements, density: {educational_density:.2f}")
        return result
    
    def _extract_original_content(self, scene_data: Dict[str, Any]) -> str:
        """Extract original content from scene data"""
        content_parts = []
        
        # Add dialogue
        if scene_data.get("dialogue"):
            content_parts.append(scene_data["dialogue"])
        
        # Add educational content
        educational_content = scene_data.get("educational_content", {})
        for category, items in educational_content.items():
            if isinstance(items, list):
                content_parts.extend(items)
            else:
                content_parts.append(str(items))
        
        # Add image create prompt
        if scene_data.get("image_create_prompt"):
            content_parts.append(scene_data["image_create_prompt"])
        
        return " ".join(content_parts)
    
    def _extract_data_points(self, content: str) -> List[str]:
        """Extract data points from content"""
        data_points = []
        
        for pattern_type, patterns in self.data_extraction_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if pattern_type == "numbers" and len(match) > 1:  # Avoid single digits
                        data_points.append(f"{match} ({pattern_type})")
                    elif pattern_type != "numbers":
                        data_points.append(f"{match} ({pattern_type})")
        
        # Remove duplicates and return
        return list(set(data_points))
    
    def _extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts from content"""
        key_concepts = []
        content_lower = content.lower()
        
        for concept_type, patterns in self.concept_extraction_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    # Extract the concept and its context
                    concept_context = self._extract_concept_context(content, pattern)
                    if concept_context:
                        key_concepts.append(f"{concept_context} ({concept_type})")
        
        return list(set(key_concepts))
    
    def _extract_concept_context(self, content: str, pattern: str) -> str:
        """Extract context around a concept pattern"""
        import re
        
        # Find the pattern and extract surrounding context
        pattern_index = content.lower().find(pattern)
        if pattern_index != -1:
            # Extract 50 characters before and after the pattern
            start = max(0, pattern_index - 50)
            end = min(len(content), pattern_index + len(pattern) + 50)
            context = content[start:end].strip()
            
            # Clean up the context
            context = re.sub(r'\s+', ' ', context)
            return context
        
        return ""
    
    def _generate_visual_metaphors(self, content: str, key_concepts: List[str]) -> List[str]:
        """Generate visual metaphors based on content and concepts"""
        metaphors = []
        content_lower = content.lower()
        
        # Determine metaphor type based on content
        metaphor_type = self._determine_metaphor_type(content_lower, key_concepts)
        
        if metaphor_type in self.metaphor_templates:
            metaphors.extend(self.metaphor_templates[metaphor_type])
        
        # Generate custom metaphors based on key concepts
        for concept in key_concepts:
            custom_metaphor = self._generate_custom_metaphor(concept, content_lower)
            if custom_metaphor:
                metaphors.append(custom_metaphor)
        
        return list(set(metaphors))
    
    def _determine_metaphor_type(self, content: str, key_concepts: List[str]) -> str:
        """Determine the most appropriate metaphor type"""
        metaphor_indicators = {
            "growth": ["grow", "increase", "expand", "develop", "progress", "rise"],
            "connection": ["connect", "link", "relate", "associate", "network", "web"],
            "transformation": ["change", "transform", "convert", "evolve", "shift", "turn"],
            "comparison": ["compare", "versus", "vs", "different", "similar", "contrast"],
            "process": ["process", "step", "method", "procedure", "workflow", "sequence"]
        }
        
        scores = {}
        for metaphor_type, indicators in metaphor_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content)
            scores[metaphor_type] = score
        
        # Return the metaphor type with highest score
        return max(scores, key=scores.get) if scores else "process"
    
    def _generate_custom_metaphor(self, concept: str, content: str) -> str:
        """Generate a custom metaphor for a specific concept"""
        concept_lower = concept.lower()
        
        # Simple metaphor generation based on concept type
        if "process" in concept_lower:
            return f"like a {concept} assembly line with clear steps and checkpoints"
        elif "system" in concept_lower:
            return f"as a {concept} ecosystem where all parts work together"
        elif "strategy" in concept_lower:
            return f"like a {concept} game plan with moves and counter-moves"
        elif "technology" in concept_lower:
            return f"as a {concept} toolkit with different tools for different tasks"
        
        return ""
    
    def _create_information_hierarchy(self, content: str, key_concepts: List[str]) -> Dict[str, List[str]]:
        """Create information hierarchy from content and concepts"""
        hierarchy = {
            "primary": [],
            "secondary": [],
            "tertiary": []
        }
        
        # Determine hierarchy type
        hierarchy_type = self._determine_hierarchy_type(content, key_concepts)
        
        if hierarchy_type in self.hierarchy_templates:
            template = self.hierarchy_templates[hierarchy_type]
            
            # Assign concepts to hierarchy levels
            for i, concept in enumerate(key_concepts):
                if i == 0:
                    hierarchy["primary"].append(concept)
                elif i < 3:
                    hierarchy["secondary"].append(concept)
                else:
                    hierarchy["tertiary"].append(concept)
        
        return hierarchy
    
    def _determine_hierarchy_type(self, content: str, key_concepts: List[str]) -> str:
        """Determine the most appropriate hierarchy type"""
        hierarchy_indicators = {
            "pyramid": ["main", "primary", "core", "fundamental", "basic"],
            "flow": ["process", "step", "sequence", "order", "progression"],
            "tree": ["category", "type", "kind", "classification", "branch"]
        }
        
        scores = {}
        for hierarchy_type, indicators in hierarchy_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content.lower())
            scores[hierarchy_type] = score
        
        return max(scores, key=scores.get) if scores else "pyramid"
    
    def _generate_learning_objectives(self, content: str, target_audience: str) -> List[str]:
        """Generate learning objectives based on content and audience"""
        objectives = []
        
        # Base objectives for different audience levels
        base_objectives = {
            "beginner": [
                "Understand the basic concept",
                "Identify key components",
                "Recognize main characteristics"
            ],
            "general": [
                "Explain the concept clearly",
                "Apply knowledge to examples",
                "Analyze different aspects"
            ],
            "intermediate": [
                "Evaluate effectiveness",
                "Compare different approaches",
                "Synthesize information"
            ],
            "expert": [
                "Critique methodologies",
                "Design improvements",
                "Create new applications"
            ]
        }
        
        # Get base objectives for target audience
        if target_audience in base_objectives:
            objectives.extend(base_objectives[target_audience])
        
        # Generate content-specific objectives
        content_objectives = self._generate_content_specific_objectives(content)
        objectives.extend(content_objectives)
        
        return list(set(objectives))
    
    def _generate_content_specific_objectives(self, content: str) -> List[str]:
        """Generate objectives specific to the content"""
        objectives = []
        content_lower = content.lower()
        
        if "statistics" in content_lower or "data" in content_lower:
            objectives.append("Interpret statistical information accurately")
        
        if "process" in content_lower or "method" in content_lower:
            objectives.append("Follow the process step-by-step")
        
        if "compare" in content_lower or "versus" in content_lower:
            objectives.append("Compare and contrast different options")
        
        if "history" in content_lower or "timeline" in content_lower:
            objectives.append("Understand historical context and progression")
        
        return objectives
    
    def _generate_assessment_criteria(self, content: str, target_audience: str) -> List[str]:
        """Generate assessment criteria based on content and audience"""
        criteria = []
        
        # Base criteria for different audience levels
        base_criteria = {
            "beginner": [
                "Can identify key elements",
                "Can explain in simple terms",
                "Can recognize examples"
            ],
            "general": [
                "Can explain concepts clearly",
                "Can apply to new situations",
                "Can identify relationships"
            ],
            "intermediate": [
                "Can analyze components",
                "Can evaluate effectiveness",
                "Can suggest improvements"
            ],
            "expert": [
                "Can critique methodologies",
                "Can design solutions",
                "Can create innovations"
            ]
        }
        
        # Get base criteria for target audience
        if target_audience in base_criteria:
            criteria.extend(base_criteria[target_audience])
        
        return criteria
    
    def _create_enhanced_elements(self, data_points: List[str], key_concepts: List[str], 
                                visual_metaphors: List[str], information_hierarchy: Dict[str, List[str]],
                                learning_objectives: List[str], assessment_criteria: List[str],
                                target_audience: str) -> List[EducationalElement]:
        """Create enhanced educational elements"""
        elements = []
        
        # Add data points
        for data_point in data_points:
            elements.append(EducationalElement(
                element_type=EducationalElementType.DATA_POINT,
                content=data_point,
                importance_level=4,
                visual_complexity=2,
                target_audience=target_audience,
                learning_objective="Understand quantitative information"
            ))
        
        # Add key concepts
        for concept in key_concepts:
            elements.append(EducationalElement(
                element_type=EducationalElementType.KEY_CONCEPT,
                content=concept,
                importance_level=5,
                visual_complexity=3,
                target_audience=target_audience,
                learning_objective="Master core concepts"
            ))
        
        # Add visual metaphors
        for metaphor in visual_metaphors:
            elements.append(EducationalElement(
                element_type=EducationalElementType.VISUAL_METAPHOR,
                content=metaphor,
                importance_level=3,
                visual_complexity=4,
                target_audience=target_audience,
                learning_objective="Visualize abstract concepts"
            ))
        
        # Add information hierarchy
        for level, items in information_hierarchy.items():
            for item in items:
                elements.append(EducationalElement(
                    element_type=EducationalElementType.INFORMATION_HIERARCHY,
                    content=f"{level}: {item}",
                    importance_level=4 if level == "primary" else 3 if level == "secondary" else 2,
                    visual_complexity=3,
                    target_audience=target_audience,
                    learning_objective="Understand information structure"
                ))
        
        # Add learning objectives
        for objective in learning_objectives:
            elements.append(EducationalElement(
                element_type=EducationalElementType.LEARNING_OBJECTIVE,
                content=objective,
                importance_level=5,
                visual_complexity=2,
                target_audience=target_audience,
                learning_objective=objective
            ))
        
        # Add assessment criteria
        for criterion in assessment_criteria:
            elements.append(EducationalElement(
                element_type=EducationalElementType.ASSESSMENT_CRITERIA,
                content=criterion,
                importance_level=4,
                visual_complexity=2,
                target_audience=target_audience,
                learning_objective="Meet learning standards"
            ))
        
        return elements
    
    def _calculate_complexity_score(self, elements: List[EducationalElement], target_audience: str) -> float:
        """Calculate complexity score based on elements and audience"""
        if not elements:
            return 0.0
        
        # Calculate average complexity
        total_complexity = sum(element.visual_complexity for element in elements)
        average_complexity = total_complexity / len(elements)
        
        # Adjust for target audience
        audience_adjustments = {
            "beginner": 0.8,
            "general": 1.0,
            "intermediate": 1.2,
            "expert": 1.5
        }
        
        adjustment = audience_adjustments.get(target_audience, 1.0)
        adjusted_complexity = average_complexity * adjustment
        
        # Normalize to 0.0-1.0 scale
        return min(1.0, adjusted_complexity / 5.0)
    
    def _calculate_educational_density(self, elements: List[EducationalElement]) -> float:
        """Calculate educational density score"""
        if not elements:
            return 0.0
        
        # Count different types of elements
        element_counts = {}
        for element in elements:
            element_type = element.element_type.value
            element_counts[element_type] = element_counts.get(element_type, 0) + 1
        
        # Calculate density based on variety and quantity
        variety_score = len(element_counts) / len(EducationalElementType)
        quantity_score = min(1.0, len(elements) / 20)  # Normalize to 20 elements max
        
        # Combine scores
        density_score = (variety_score + quantity_score) / 2
        
        return density_score
    
    def generate_enhanced_prompt(self, enhanced_content: EnhancedEducationalContent) -> str:
        """Generate enhanced prompt with educational depth"""
        
        prompt_parts = []
        
        # Add learning objectives
        if enhanced_content.learning_objectives:
            prompt_parts.append("LEARNING OBJECTIVES:")
            for objective in enhanced_content.learning_objectives:
                prompt_parts.append(f"- {objective}")
        
        # Add key concepts
        if enhanced_content.key_concepts:
            prompt_parts.append("\nKEY CONCEPTS TO HIGHLIGHT:")
            for concept in enhanced_content.key_concepts:
                prompt_parts.append(f"- {concept}")
        
        # Add data points
        if enhanced_content.data_points:
            prompt_parts.append("\nSPECIFIC DATA POINTS:")
            for data_point in enhanced_content.data_points:
                prompt_parts.append(f"- {data_point}")
        
        # Add visual metaphors
        if enhanced_content.visual_metaphors:
            prompt_parts.append("\nVISUAL METAPHORS TO USE:")
            for metaphor in enhanced_content.visual_metaphors:
                prompt_parts.append(f"- {metaphor}")
        
        # Add information hierarchy
        if enhanced_content.information_hierarchy:
            prompt_parts.append("\nINFORMATION HIERARCHY:")
            for level, items in enhanced_content.information_hierarchy.items():
                if items:
                    prompt_parts.append(f"{level.upper()}:")
                    for item in items:
                        prompt_parts.append(f"  - {item}")
        
        # Add assessment criteria
        if enhanced_content.assessment_criteria:
            prompt_parts.append("\nASSESSMENT CRITERIA:")
            for criterion in enhanced_content.assessment_criteria:
                prompt_parts.append(f"- {criterion}")
        
        # Add complexity and density information
        prompt_parts.append(f"\nCOMPLEXITY SCORE: {enhanced_content.complexity_score:.2f}")
        prompt_parts.append(f"EDUCATIONAL DENSITY: {enhanced_content.educational_density:.2f}")
        
        return "\n".join(prompt_parts)

# Test function
def test_educational_enhancer():
    """Test the EducationalEnhancer"""
    enhancer = EducationalEnhancer()
    
    # Test scene data
    test_scene = {
        "dialogue": "the company was created in 1886 by Dr. John Pemberton and now sells 1.9 billion servings daily worldwide.",
        "educational_content": {
            "key_concepts": ["the company origin", "Global marketing"],
            "specific_facts": ["Created in 1886", "1.9 billion servings daily"],
            "statistics": ["1886 creation date", "1.9 billion daily servings"]
        },
        "image_create_prompt": "Educational scene about the company's history and global reach"
    }
    
    # Enhance educational content
    enhanced = enhancer.enhance_educational_content(test_scene, "general")
    
    print(f"Enhanced educational content:")
    print(f"Data points: {enhanced.data_points}")
    print(f"Key concepts: {enhanced.key_concepts}")
    print(f"Visual metaphors: {enhanced.visual_metaphors}")
    print(f"Learning objectives: {enhanced.learning_objectives}")
    print(f"Complexity score: {enhanced.complexity_score:.2f}")
    print(f"Educational density: {enhanced.educational_density:.2f}")
    
    # Generate enhanced prompt
    enhanced_prompt = enhancer.generate_enhanced_prompt(enhanced)
    print(f"\nEnhanced prompt:\n{enhanced_prompt}")

if __name__ == "__main__":
    test_educational_enhancer()
