from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class SceneType(str, Enum):
    EXPLANATION = "explanation"  # Character explaining concepts
    VISUAL_DEMO = "visual_demo"  # Visual demonstration/example scene
    COMPARISON = "comparison"    # Comparison explanation scene
    STORY_TELLING = "story_telling"  # Story-telling scene
    HOOK = "hook"  # Opening hook scene
    CONCLUSION = "conclusion"  # Closing/summary scene
    EXAMPLE = "example"  # Example scene
    STATISTIC = "statistic"  # Statistical information scene
    CALL_TO_ACTION = "call_to_action"  # Call to action scene
    SUMMARY = "summary"  # Summary scene
    
    # Additional scene types for diverse storytelling
    STORY = "story"  # Detailed narrative scene
    ANALYSIS = "analysis"  # Deep analysis scene
    CONTROVERSY = "controversy"  # Debate/controversy scene
    TIMELINE = "timeline"  # Timeline/historical scene
    INTERVIEW = "interview"  # Interview-style scene
    DEMONSTRATION = "demonstration"  # Live demonstration scene
    PREDICTION = "prediction"  # Future prediction scene
    DEBATE = "debate"  # Debate discussion scene
    REVELATION = "revelation"  # Surprising revelation scene
    JOURNEY = "journey"  # Journey/process scene
    TRANSFORMATION = "transformation"  # Transformation scene
    CONFLICT = "conflict"  # Conflict/tension scene
    RESOLUTION = "resolution"  # Resolution scene

class ImageStyle(str, Enum):
    # Basic styles
    SINGLE_CHARACTER = "single_character"
    CHARACTER_WITH_BACKGROUND = "character_with_background"
    
    # Educational styles
    INFOGRAPHIC = "infographic"
    DIAGRAM_EXPLANATION = "diagram_explanation"
    BEFORE_AFTER_COMPARISON = "before_after_comparison"
    STEP_BY_STEP_VISUAL = "step_by_step_visual"
    
    # Comic/Story styles
    FOUR_CUT_CARTOON = "four_cut_cartoon"
    COMIC_PANEL = "comic_panel"
    SPEECH_BUBBLE = "speech_bubble"
    
    # Cinematic styles
    CINEMATIC = "cinematic"
    CLOSE_UP_REACTION = "close_up_reaction"
    WIDE_ESTABLISHING_SHOT = "wide_establishing_shot"
    
    # Special effects
    SPLIT_SCREEN = "split_screen"
    OVERLAY_GRAPHICS = "overlay_graphics"
    CUTAWAY_ILLUSTRATION = "cutaway_illustration"

class VoiceTone(str, Enum):
    # Basic emotions
    EXCITED = "excited"
    CURIOUS = "curious"
    SERIOUS = "serious"
    FRIENDLY = "friendly"
    
    # Additional emotions
    SAD = "sad"
    MYSTERIOUS = "mysterious"
    SURPRISED = "surprised"
    CONFIDENT = "confident"
    
    # Educational tones
    INFORMATIVE = "informative"
    ENTHUSIASTIC = "enthusiastic"
    IMPRESSED = "impressed"
    ENCOURAGING = "encouraging"
    WORRIED = "worried"
    PLAYFUL = "playful"
    DRAMATIC = "dramatic"
    CALM = "calm"

class TransitionType(str, Enum):
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE = "slide"
    CUT = "cut"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    PUSH = "push"
    SPIN = "spin"
    FLIP = "flip"
    NONE = "none"  # Direct connection without transition

class HookTechnique(str, Enum):
    SHOCKING_FACT = "shocking_fact"  # "The water you drink daily contains dinosaur urine"
    INTRIGUING_QUESTION = "intriguing_question"  # "Why is the ocean salty but rain is not?"
    VISUAL_SURPRISE = "visual_surprise"  # Unexpected visual element
    CONTRADICTION = "contradiction"  # "Truth that contradicts common sense"
    MYSTERY_SETUP = "mystery_setup"  # "There's a secret that nobody knows..."

class ElevenLabsSettings(BaseModel):
    stability: float = Field(ge=0.0, le=1.0, description="Consistency vs emotional expression")
    similarity_boost: float = Field(ge=0.0, le=1.0, description="Closeness to reference voice")
    style: float = Field(ge=0.0, le=1.0, description="Expressiveness (exaggeration)")
    speed: float = Field(ge=0.7, le=1.2, description="Speech delivery rate")
    loudness: float = Field(ge=-1.0, le=1.0, description="Audio output volume")
    
    @classmethod
    def for_tone(cls, tone: VoiceTone) -> 'ElevenLabsSettings':
        """Return recommended settings for each voice tone"""
        settings_map = {
            VoiceTone.EXCITED: cls(stability=0.3, similarity_boost=0.8, style=0.8, speed=1.1, loudness=0.2),
            VoiceTone.SERIOUS: cls(stability=0.8, similarity_boost=0.9, style=0.3, speed=0.9, loudness=0.0),
            VoiceTone.SAD: cls(stability=0.7, similarity_boost=0.8, style=0.6, speed=0.8, loudness=-0.2),
            VoiceTone.MYSTERIOUS: cls(stability=0.6, similarity_boost=0.7, style=0.7, speed=0.85, loudness=-0.1),
            VoiceTone.CURIOUS: cls(stability=0.4, similarity_boost=0.8, style=0.7, speed=1.0, loudness=0.0),
            VoiceTone.FRIENDLY: cls(stability=0.5, similarity_boost=0.8, style=0.6, speed=1.0, loudness=0.1),
            VoiceTone.SURPRISED: cls(stability=0.2, similarity_boost=0.7, style=0.9, speed=1.2, loudness=0.3),
            VoiceTone.CONFIDENT: cls(stability=0.7, similarity_boost=0.9, style=0.4, speed=0.95, loudness=0.1),
            VoiceTone.WORRIED: cls(stability=0.6, similarity_boost=0.8, style=0.5, speed=0.85, loudness=-0.1),
            VoiceTone.PLAYFUL: cls(stability=0.3, similarity_boost=0.7, style=0.8, speed=1.1, loudness=0.2),
            VoiceTone.DRAMATIC: cls(stability=0.4, similarity_boost=0.8, style=0.9, speed=0.9, loudness=0.2),
            VoiceTone.CALM: cls(stability=0.8, similarity_boost=0.9, style=0.2, speed=0.85, loudness=-0.1),
            VoiceTone.ENTHUSIASTIC: cls(stability=0.2, similarity_boost=0.8, style=0.9, speed=1.15, loudness=0.3)
        }
        return settings_map.get(tone, cls(stability=0.5, similarity_boost=0.8, style=0.5, speed=1.0, loudness=0.0))

class VideoGenerationPrompt(BaseModel):
    """
    Detailed prompt for video generation including character movements, 
    background animations, and visual effects
    """
    base_description: str = Field(description="Basic description of what should happen in the video")
    
    # Character movement/gesture
    character_gesture: Optional[str] = Field(default=None, description="Character gestures: 'pointing at screen', 'nodding enthusiastically', 'looking surprised'")
    character_expression: Optional[str] = Field(default=None, description="Character facial expression: 'excited smile', 'thoughtful frown', 'wide-eyed wonder'")
    
    # Background/environment movement
    background_animation: Optional[str] = Field(default=None, description="Background animations: 'floating particles', 'gentle waves', 'rotating gears'")
    environmental_effects: Optional[str] = Field(default=None, description="Environmental effects: 'wind blowing leaves', 'bubbles rising', 'sparkles appearing'")
    
    # Camera/visual effects
    camera_behavior: Optional[str] = Field(default=None, description="Camera movements: 'slow zoom into character face', 'pan across the scene'")
    visual_emphasis: Optional[str] = Field(default=None, description="Visual emphasis: 'highlight important text', 'glow effect on key objects'")
    
    # Purpose of video generation
    animation_purpose: str = Field(description="Why animation is needed: 'to show emotion change', 'to demonstrate concept', 'to maintain engagement'")

class Scene(BaseModel):
    scene_number: int
    scene_type: SceneType
    
    # Dialogue/narration
    dialogue: Optional[str] = Field(default=None, description="What the character will say")
    voice_tone: VoiceTone
    elevenlabs_settings: ElevenLabsSettings
    
    # Image related
    image_style: ImageStyle
    image_create_prompt: str = Field(description="Detailed prompt for image generation - be very specific about visual elements, lighting, composition, and style")
    character_pose: Optional[str] = Field(default=None, description="Character pose: 'pointing', 'thinking', 'surprised'")
    character_expression: Optional[str] = Field(default=None, description="Character emotional expression: 'smiling', 'winking', 'excited', 'surprised', 'confident'")
    background_description: Optional[str] = Field(default=None, description="Background setting description")
    
    # Video related (8 seconds fixed duration)
    needs_animation: bool = Field(description="Whether this scene needs video animation or static image is enough")
    video_prompt: Optional[str] = Field(default=None, description="Detailed video generation prompt if animation is needed")
    
    # Scene connectivity
    transition_to_next: TransitionType = Field(description="How to transition to the next scene")
    
    # Hook technique (only for first scene)
    hook_technique: Optional[HookTechnique] = Field(default=None, description="Hook technique used if this is the first scene")

class ScenePlan(BaseModel):
    """Scene plan for story development"""
    scene_number: int
    scene_type: SceneType
    scene_purpose: str
    key_content: str
    scene_focus: str

class StoryScript(BaseModel):
    """Story script model for overall story planning"""
    title: str
    main_character_description: str = Field(description="Consistent character description for all scenes")
    character_cosplay_instructions: str = Field(description="Instructions for how to cosplay the main character (e.g., 'cosplay like Elon Musk', 'dress as a music industry idol')")
    overall_style: str = Field(description="Overall video style: 'educational', 'entertaining', 'documentary'")
    overall_story: str = Field(description="The specific, focused story developed from the subject")
    story_summary: str = Field(description="Brief summary of the overall narrative and key points")
    scene_plan: List[ScenePlan] = Field(description="Plan for all scenes in order")

class VideoScript(BaseModel):
    """
    Complete video script with detailed scenes
    First scene is always the hook scene
    """
    title: str
    main_character_description: str = Field(description="Consistent character description for all scenes")
    character_cosplay_instructions: str = Field(description="Instructions for how to cosplay the main character (e.g., 'cosplay like Elon Musk', 'dress as a music industry idol')")
    overall_style: str = Field(description="Overall video style: 'educational', 'entertaining', 'documentary'")
    overall_story: str = Field(description="The specific, focused story developed from the subject")
    story_summary: str = Field(description="Brief summary of the overall narrative and key points")
    
    # All scenes in order
    scenes: List[Scene] = Field(description="All scenes in order, first scene is always the hook scene")
    
    @property
    def all_scenes(self) -> List[Scene]:
        """Return all scenes in order"""
        return self.scenes
    
    @property
    def total_scene_count(self) -> int:
        """Return total number of scenes"""
        return len(self.scenes)
    
    @property
    def hook_scene(self) -> Scene:
        """Return the first scene (hook scene)"""
        return self.scenes[0] if self.scenes else None
    
    def get_scene_by_number(self, scene_number: int) -> Optional[Scene]:
        """Get scene by its number"""
        for scene in self.scenes:
            if scene.scene_number == scene_number:
                return scene
        return None

# Animation decision guidelines for Agent 1
ANIMATION_GUIDELINES = """
USE ANIMATION when:
- Showing emotional changes (surprising fact reveal)
- Explaining complex concepts visually
- Need to focus viewer attention
- Character gestures help content understanding
- Demonstrating processes or movements
- Creating dramatic emphasis

USE STATIC IMAGE when:
- Simple information delivery
- Text or diagram-focused explanations
- Calm tone explanations
- Character is just speaking without emphasis
- Background information scenes
"""

# Video prompt examples for Agent 1
VIDEO_PROMPT_EXAMPLES = """
Good video_prompt examples:
- "Character starts with curious expression, then eyes widen with realization as floating salt molecules appear around them"
- "Character points enthusiastically at a diagram while gentle ocean waves move in background"
- "Character looks directly at camera with serious expression, background slowly darkens for dramatic effect"
- "Character nods thoughtfully while abstract thought bubbles float above their head"
- "Character gestures excitedly as colorful particles swirl around them to illustrate the concept"
"""

# Validation Models for 2-Stage Validation System

class ValidationStatus(str, Enum):
    """Status of validation result"""
    PASS = "pass"
    REVISE = "revise"
    CRITICAL_FAILURE = "critical_failure"

class ValidationSeverity(str, Enum):
    """Severity of validation issues"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ValidationIssue(BaseModel):
    """Individual validation issue"""
    severity: ValidationSeverity
    category: str  # "fun_factor", "interest_level", "uniqueness", etc.
    description: str
    suggestion: str
    affected_element: Optional[str] = None  # Which part of the script/scene

class ValidationResult(BaseModel):
    """Result of validation process"""
    status: ValidationStatus
    overall_score: float  # 0.0 to 1.0
    issues: List[ValidationIssue] = []
    feedback: str
    revision_instructions: Optional[str] = None
    revision_count: int = 0
    max_revisions: int = 3

class ScriptValidationResult(ValidationResult):
    """Result of script-level validation"""
    fun_score: float
    interest_score: float
    uniqueness_score: float
    educational_score: float
    coherence_score: float

class SceneValidationResult(ValidationResult):
    """Result of scene-level validation"""
    scene_number: int
    scene_quality_score: float
    visual_potential_score: float
    educational_density_score: float
    character_utilization_score: float
    connection_score: float

class SceneValidationSummary(BaseModel):
    """Summary of all scene validations"""
    total_scenes: int
    passed_scenes: int
    failed_scenes: int
    overall_connection_score: float
    scene_results: List[SceneValidationResult]
    needs_revision: bool
    revision_scenes: List[int] = []  # Scene numbers that need revision

# State Management Models

class ScriptState(str, Enum):
    """State of script in the workflow"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    REVISION_LIMIT_REACHED = "revision_limit_reached"

class SceneState(str, Enum):
    """State of individual scene"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    REVISION_LIMIT_REACHED = "revision_limit_reached"

class WorkflowState(BaseModel):
    """Overall workflow state tracking"""
    session_id: str
    current_stage: str  # "script_generation", "script_validation", "scene_generation", etc.
    script_state: ScriptState
    scene_states: Dict[int, SceneState] = {}  # scene_number -> state
    revision_history: List[Dict[str, Any]] = []
    validation_history: List[ValidationResult] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# New Architecture Pydantic Models

class NarrationLine(BaseModel):
    """Individual line in narration script"""
    line: str = Field(min_length=1, description="Text to be spoken")
    at_ms: int = Field(ge=0, description="Timestamp when this line starts")
    pause_ms: Optional[int] = Field(default=0, ge=0, description="Pause duration after this line")

class DialogueLine(BaseModel):
    """Individual dialogue line"""
    speaker: str = Field(description="Name of the speaker")
    line: str = Field(description="Text spoken by the character")

class Visual(BaseModel):
    """Visual frame specification"""
    frame_id: str = Field(pattern=r"^[0-9]+[A-Z]$", description="Frame identifier like '1A', '2B'")
    shot_type: Literal["wide", "medium", "close", "macro", "extreme_wide", "extreme_close"]
    camera_motion: Optional[str] = Field(default=None, description="Camera movement description")
    character_pose: Optional[str] = Field(default=None, description="Character positioning")
    expression: Optional[str] = Field(default=None, description="Character facial expression")
    background: Optional[str] = Field(default=None, description="Background setting")
    foreground_props: Optional[str] = Field(default=None, description="Props in foreground")
    lighting: Optional[str] = Field(default=None, description="Lighting description")
    color_mood: Optional[str] = Field(default=None, description="Color palette and mood")
    image_prompt: str = Field(min_length=40, description="Detailed image generation prompt")
    negative_prompt: Optional[str] = Field(default=None, description="Negative prompt")
    model_hints: Optional[List[str]] = Field(default=None, description="Style keywords")
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:5", "3:2", "2:3"]
    seed: Optional[int] = Field(default=None, description="Random seed")
    guidance_scale: Optional[float] = Field(default=7.5, ge=1.0, le=20.0, description="Guidance scale")

class TTSSettings(BaseModel):
    """Text-to-speech settings"""
    engine: Literal["elevenlabs", "openai", "google", "azure"]
    voice: str = Field(description="Voice identifier")
    language: Optional[str] = Field(default="en-US", description="Language code")
    elevenlabs_settings: Optional[Dict[str, float]] = Field(default=None, description="ElevenLabs specific settings")

class SFXCue(BaseModel):
    """Sound effect cue"""
    cue: str = Field(description="Sound effect description")
    at_ms: int = Field(ge=0, description="When to play the sound effect")
    duration_ms: int = Field(ge=0, description="Duration of the sound effect")

class OnScreenText(BaseModel):
    """On-screen text element"""
    text: str = Field(description="Text to display")
    at_ms: int = Field(ge=0, description="When to show the text")
    duration_ms: int = Field(ge=0, description="How long to show the text")
    style: Optional[str] = Field(default=None, description="Text styling")

class Timing(BaseModel):
    """Timing information for the scene"""
    total_ms: int = Field(ge=1000, description="Total duration of the scene in milliseconds")

class Continuity(BaseModel):
    """Continuity information for scene transitions"""
    in_from: Optional[str] = Field(default=None, description="How this scene transitions in")
    out_to: Optional[str] = Field(default=None, description="How this scene transitions out")
    callback_tags: Optional[List[str]] = Field(default=None, description="Visual motifs")

class ScenePackage(BaseModel):
    """Production-ready scene package from Scene Script Writer"""
    scene_number: int = Field(ge=1, description="Scene number")
    narration_script: List[NarrationLine] = Field(description="Narration lines with timing")
    dialogue: Optional[List[DialogueLine]] = Field(default=None, description="Dialogue lines")
    visuals: List[Visual] = Field(min_items=1, description="Visual frames for the scene")
    tts: TTSSettings = Field(description="Text-to-speech configuration")
    sfx_cues: Optional[List[SFXCue]] = Field(default=None, description="Sound effect cues")
    on_screen_text: Optional[List[OnScreenText]] = Field(default=None, description="On-screen text elements")
    timing: Timing = Field(description="Scene timing information")
    continuity: Optional[Continuity] = Field(default=None, description="Continuity information")
    safety_checks: Optional[List[str]] = Field(default=None, description="Safety check results")

class SceneBeat(BaseModel):
    """Individual scene beat/point"""
    scene_number: int = Field(ge=1)
    scene_type: Literal["hook", "explanation", "story", "analysis", "revelation", "summary", "credits", "example", "controversy", "comparison", "timeline", "interview", "demonstration", "prediction", "debate", "journey", "transformation", "conflict", "resolution"]
    beats: List[str] = Field(description="High-level story beats")
    learning_objectives: Optional[List[str]] = Field(default=None, description="Learning objectives")
    needs_animation: bool = Field(description="Whether animation is needed")
    transition_to_next: Literal["cut", "fade", "wipe", "morph", "dissolve", "credits", "end"]
    scene_importance: int = Field(ge=1, le=5, description="Importance level (1-5)")

class FullScript(BaseModel):
    """High-level story structure from Full Script Writer"""
    title: str = Field(min_length=5, description="Video title")
    logline: Optional[str] = Field(default=None, description="One-sentence summary")
    overall_style: str = Field(description="Overall tone and style")
    main_character: Optional[str] = Field(default=None, description="Main character description")
    cosplay_instructions: Optional[str] = Field(default=None, description="Character cosplay instructions")
    story_summary: str = Field(min_length=60, max_length=2000, description="Story summary")
    scenes: List[SceneBeat] = Field(min_items=3, max_items=10, description="Scene beats")

class ImageAsset(BaseModel):
    """Generated image asset from Image Create Agent"""
    frame_id: str = Field(pattern=r"^[0-9]+[A-Z]$", description="Frame identifier")
    image_uri: str = Field(description="URI to generated image")
    thumbnail_uri: Optional[str] = Field(default=None, description="Thumbnail URI")
    prompt_used: str = Field(min_length=1, description="Final prompt used")
    negative_prompt_used: Optional[str] = Field(default=None, description="Negative prompt used")
    model: Literal["stable-diffusion-xl", "flux-1", "flux-1-pro", "midjourney", "dall-e-3", "gemini-imagen", "gemini-2.5-flash-image-preview", "mock"]
    sampler: Optional[str] = Field(default=None, description="Sampling method")
    cfg: Optional[float] = Field(default=None, ge=1.0, le=20.0, description="CFG scale")
    steps: Optional[int] = Field(default=None, ge=1, le=150, description="Inference steps")
    seed: Optional[int] = Field(default=None, description="Random seed")
    safety_result: Optional[Literal["safe", "flagged", "blocked"]] = Field(default=None, description="Safety check result")
    generation_time_ms: Optional[int] = Field(default=None, ge=0, description="Generation time")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")