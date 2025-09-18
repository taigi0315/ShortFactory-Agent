"""
ADK Output Schema Models
Pydantic-based output data structures for each agent
Automatically converted to ADK output_schema
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


class SceneType(str, Enum):
    """Scene type definitions"""
    HOOK = "hook"
    EXPLANATION = "explanation"
    STORY = "story"
    ANALYSIS = "analysis"
    REVELATION = "revelation"
    SUMMARY = "summary"
    EXAMPLE = "example"
    COMPARISON = "comparison"


class TransitionType(str, Enum):
    """Transition type definitions"""
    FADE = "fade"
    CUT = "cut"
    DISSOLVE = "dissolve"
    SLIDE = "slide"


class SceneBeat(BaseModel):
    """Scene beat data"""
    scene_number: int = Field(ge=1, description="Scene number")
    scene_type: SceneType = Field(description="Scene type")
    beats: List[str] = Field(min_length=1, description="High-level story beats")
    learning_objectives: Optional[List[str]] = Field(default=None, description="Learning objectives")
    needs_animation: bool = Field(description="Whether animation is needed")
    transition_to_next: TransitionType = Field(description="Transition to next scene")
    scene_importance: int = Field(ge=1, le=5, description="Scene importance level (1-5)")


class FullScriptOutput(BaseModel):
    """
    Full Script Writer output schema
    Structure enforced by ADK output_schema
    """
    title: str = Field(
        min_length=5, 
        max_length=100,
        description="Video title"
    )
    
    logline: Optional[str] = Field(
        default=None,
        max_length=200,
        description="One-line summary"
    )
    
    overall_style: str = Field(
        description="Overall tone and style"
    )
    
    main_character: Optional[str] = Field(
        default=None,
        description="Main character description"
    )
    
    cosplay_instructions: Optional[str] = Field(
        default=None,
        description="Character cosplay instructions"
    )
    
    story_summary: str = Field(
        min_length=60,
        max_length=2000,
        description="Story summary"
    )
    
    scenes: List[SceneBeat] = Field(
        min_length=3,
        max_length=10,
        description="Scene beats"
    )

    class Config:
        json_schema_extra = {
            "title": "FullScriptOutput",
            "description": "Output data structure for Full Script Writer Agent - ADK output_schema compliant"
        }


class NarrationLine(BaseModel):
    """Narration line"""
    line: str = Field(min_length=1, description="Narration text")
    at_ms: int = Field(ge=0, description="Start time (milliseconds)")
    pause_ms: int = Field(default=500, ge=0, description="Pause after line (milliseconds)")


class VisualFrame(BaseModel):
    """Visual frame specification"""
    frame_id: str = Field(
        pattern=r"^[0-9]+[A-Z]$",
        description="Frame identifier (예: '1A', '2B')"
    )
    
    shot_type: Literal["wide", "medium", "close", "macro", "extreme_wide", "extreme_close"] = Field(
        description="Camera shot type"
    )
    
    image_prompt: str = Field(
        min_length=40,
        description="Detailed prompt for image generation"
    )
    
    negative_prompt: Optional[str] = Field(
        default=None,
        description="Unwanted elements"
    )
    
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:5", "3:2", "2:3"] = Field(
        default="16:9",
        description="Image aspect ratio"
    )
    
    # 선택적 비주얼 요소들
    character_pose: Optional[str] = Field(default=None, description="캐릭터 포즈")
    expression: Optional[str] = Field(default=None, description="캐릭터 표정")
    background: Optional[str] = Field(default=None, description="배경 설명")
    lighting: Optional[str] = Field(default=None, description="조명 설명")
    color_mood: Optional[str] = Field(default=None, description="색상 분위기")


class TTSSettings(BaseModel):
    """TTS 설정 - LemonFox 기반"""
    engine: str = Field(default="lemonfox", description="TTS 엔진")
    voice: str = Field(default="sarah", description="음성 이름")
    language: str = Field(default="en-US", description="언어 코드")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="말하기 속도")


class TimingInfo(BaseModel):
    """타이밍 정보"""
    total_ms: int = Field(gt=0, description="총 씬 지속시간 (밀리초)")
    estimated: bool = Field(default=True, description="추정값 여부 (TTS 결과로 업데이트됨)")


class OnScreenTextElement(BaseModel):
    """온스크린 텍스트 요소 (선택사항)"""
    text: str = Field(description="표시할 텍스트")
    at_ms: int = Field(ge=0, description="표시 시작 시간")
    duration_ms: int = Field(gt=0, description="표시 지속시간")
    style: str = Field(default="normal", description="텍스트 스타일")
    position: str = Field(default="center", description="텍스트 위치")


class ScenePackageOutput(BaseModel):
    """
    Scene Script Writer 출력 스키마
    ADK output_schema로 강제되는 구조
    실제 사용되는 기능들만 포함 (SFX 제거)
    """
    scene_number: int = Field(ge=1, description="씬 번호")
    
    narration_script: List[NarrationLine] = Field(
        min_length=1,
        description="타이밍이 포함된 나레이션 스크립트"
    )
    
    visuals: List[VisualFrame] = Field(
        min_length=1,
        max_length=8,
        description="비주얼 프레임들 (씬당 1-8개)"
    )
    
    tts: TTSSettings = Field(
        description="TTS 설정"
    )
    
    timing: TimingInfo = Field(
        description="씬 타이밍 정보"
    )
    
    # 선택적 필드들
    dialogue: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="대화 라인들 (선택사항)"
    )
    
    on_screen_text: Optional[List[OnScreenTextElement]] = Field(
        default=None,
        description="온스크린 텍스트 요소들 (선택사항)"
    )
    
    # 전환 정보 (단순화)
    transition_in: Optional[TransitionType] = Field(
        default=TransitionType.FADE,
        description="씬 시작 전환"
    )
    
    transition_out: Optional[TransitionType] = Field(
        default=TransitionType.FADE,
        description="씬 종료 전환"
    )

    class Config:
        json_schema_extra = {
            "title": "ScenePackageOutput",
            "description": "Scene Script Writer Agent의 출력 데이터 구조 - 실제 사용 기능만 포함"
        }


class ImageAssetOutput(BaseModel):
    """
    Image Create Agent 출력 스키마
    생성된 이미지 에셋 정보
    """
    frame_id: str = Field(description="Frame identifier")
    image_uri: str = Field(description="이미지 파일 경로")
    thumbnail_uri: Optional[str] = Field(default=None, description="썸네일 경로")
    
    generation_metadata: Dict[str, Any] = Field(
        description="생성 메타데이터",
        examples=[{
            "model": "stability-ai",
            "prompt_used": "actual prompt used",
            "generation_time_ms": 1500,
            "file_size_bytes": 245760,
            "dimensions": {"width": 1920, "height": 1080}
        }]
    )
    
    safety_result: Optional[str] = Field(
        default=None,
        description="안전성 검사 결과"
    )

    class Config:
        json_schema_extra = {
            "title": "ImageAssetOutput",
            "description": "Image Create Agent의 출력 데이터 구조"
        }


class VoiceAssetOutput(BaseModel):
    """
    Voice Generate Agent 출력 스키마
    생성된 음성 에셋 정보
    """
    scene_number: int = Field(ge=1, description="씬 번호")
    voice_file: str = Field(description="음성 파일 경로")
    duration_ms: int = Field(gt=0, description="실제 음성 지속시간 (밀리초)")
    
    text_used: str = Field(description="TTS에 실제 사용된 텍스트")
    
    voice_settings: Dict[str, Any] = Field(
        description="사용된 음성 설정",
        examples=[{
            "engine": "lemonfox",
            "voice": "sarah",
            "speed": 1.0,
            "language": "en-US"
        }]
    )
    
    generation_metadata: Dict[str, Any] = Field(
        description="생성 메타데이터",
        examples=[{
            "generation_time_ms": 3200,
            "file_size_bytes": 1048576,
            "estimated_cost": 0.002
        }]
    )

    class Config:
        json_schema_extra = {
            "title": "VoiceAssetOutput",
            "description": "Voice Generate Agent의 출력 데이터 구조"
        }


class VideoOutput(BaseModel):
    """
    Video Maker Agent 출력 스키마
    최종 비디오 정보
    """
    video_path: str = Field(description="최종 비디오 파일 경로")
    duration_ms: int = Field(gt=0, description="비디오 총 지속시간")
    
    video_metadata: Dict[str, Any] = Field(
        description="비디오 메타데이터",
        examples=[{
            "resolution": "1920x1080",
            "fps": 30,
            "file_size_bytes": 15728640,
            "scenes_count": 5,
            "total_frames": 150
        }]
    )
    
    assembly_info: Dict[str, Any] = Field(
        description="조립 과정 정보",
        examples=[{
            "generation_time_ms": 8500,
            "audio_sync": "perfect",
            "transitions_applied": 4
        }]
    )

    class Config:
        json_schema_extra = {
            "title": "VideoOutput",
            "description": "Video Maker Agent의 출력 데이터 구조"
        }
