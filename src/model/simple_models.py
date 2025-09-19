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


class SimpleNarration(BaseModel):
    """Simple narration line"""
    line: str = Field(description="Narration text")
    at_ms: int = Field(description="Start time in milliseconds")


class SimpleVisual(BaseModel):
    """Simple visual frame"""
    frame_id: str = Field(description="Frame identifier")
    shot_type: str = Field(description="Camera shot type")
    image_prompt: str = Field(description="Image generation prompt")


class SimpleTTS(BaseModel):
    """Simple TTS settings"""
    engine: str = Field(description="TTS engine")
    voice: str = Field(description="Voice name")
    speed: float = Field(description="Speech speed")


class SimpleTiming(BaseModel):
    """Simple timing info"""
    total_ms: int = Field(description="Total duration in milliseconds")
    estimated: bool = Field(description="Whether timing is estimated")


class SimpleScenePackage(BaseModel):
    """Simple scene package output - Gemini API compatible"""
    scene_number: int = Field(description="Scene number")
    narration_script: List[SimpleNarration] = Field(description="Narration lines")
    visuals: List[SimpleVisual] = Field(description="Visual frames")
    tts: SimpleTTS = Field(description="TTS settings")
    timing: SimpleTiming = Field(description="Timing information")
