"""
Simple Pydantic Models - Gemini API Compatible
Based on your example: clean, simple models without additionalProperties
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SimpleScene(BaseModel):
    """Simple scene structure"""
    scene_number: int
    scene_type: str
    title: str
    beats: List[str]


class SimpleFullScript(BaseModel):
    """Simple full script output - Gemini API compatible"""
    title: str = Field(description="Video title")
    overall_style: str = Field(description="Overall style")
    story_summary: str = Field(description="Story summary")
    scenes: List[SimpleScene] = Field(description="List of scenes")


class SimpleVoiceSettings(BaseModel):
    """Voice settings for narration"""
    speed: Optional[float] = Field(default=1.0, description="Speech speed (0.7-1.3)")
    emphasis: Optional[str] = Field(default="normal", description="Emphasis level")
    pause_after: Optional[str] = Field(default="none", description="Pause after line")
    tone: Optional[str] = Field(default="conversational", description="Voice tone")


class SimpleNarration(BaseModel):
    """Simple narration line"""
    line: str = Field(description="Narration text")
    voice_settings: Optional[SimpleVoiceSettings] = Field(default=None, description="Voice control settings")


class SimpleCharacter(BaseModel):
    """Character information for visuals"""
    name: Optional[str] = Field(default="Glowbie", description="Character name")
    expression: Optional[str] = Field(default="cheerful", description="Facial expression")
    pose: Optional[str] = Field(default="standing", description="Character pose")
    outfit: Optional[str] = Field(default="default", description="Character outfit")


class SimpleCamera(BaseModel):
    """Camera settings for visuals"""
    angle: Optional[str] = Field(default="eye level", description="Camera angle")
    motion: Optional[str] = Field(default="static", description="Camera movement")
    focus: Optional[str] = Field(default="character", description="Camera focus")


class SimpleVisual(BaseModel):
    """Simple visual frame"""
    frame_id: str = Field(description="Frame identifier")
    shot_type: str = Field(description="Camera shot type")
    character: Optional[SimpleCharacter] = Field(default=None, description="Character information")
    camera: Optional[SimpleCamera] = Field(default=None, description="Camera settings")
    scene_prompt: str = Field(description="Scene description without character details")
    background: Optional[str] = Field(default=None, description="Background description")
    lighting: Optional[str] = Field(default=None, description="Lighting setup")
    style_hints: Optional[List[str]] = Field(default=None, description="Style keywords")


class SimpleTTS(BaseModel):
    """Simple TTS settings"""
    engine: str = Field(default="lemonfox", description="TTS engine")
    voice: str = Field(default="sarah", description="Voice name")
    language: Optional[str] = Field(default="en-US", description="Language code")
    speed: Optional[float] = Field(default=1.0, description="Global speech speed")


class SimpleTiming(BaseModel):
    """Simple timing info"""
    estimated_duration_seconds: Optional[float] = Field(default=None, description="Estimated scene duration in seconds")
    word_count: Optional[int] = Field(default=None, description="Total word count in narration")


class SimpleScenePackage(BaseModel):
    """Simple scene package output - Gemini API compatible"""
    scene_number: int = Field(description="Scene number")
    narration_script: List[SimpleNarration] = Field(description="Narration lines")
    visuals: List[SimpleVisual] = Field(description="Visual frames")
    tts: SimpleTTS = Field(description="TTS settings")
    timing: SimpleTiming = Field(description="Timing information")
