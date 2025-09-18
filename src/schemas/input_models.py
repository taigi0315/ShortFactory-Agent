"""
ADK 입력 스키마 모델들
Pydantic 기반으로 각 에이전트의 입력 데이터 구조를 정의
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


class LengthPreference(str, Enum):
    """비디오 길이 선호도"""
    SHORT = "30-45s"
    MEDIUM = "60-90s" 
    LONG = "2-3min"
    EXTENDED = "3-5min"


class Language(str, Enum):
    """지원 언어"""
    ENGLISH = "English"
    KOREAN = "Korean"
    SPANISH = "Spanish"
    FRENCH = "French"
    GERMAN = "German"
    JAPANESE = "Japanese"


class FullScriptInput(BaseModel):
    """
    Full Script Writer 입력 스키마
    ADK input_schema로 자동 변환됨
    """
    topic: str = Field(
        min_length=5, 
        max_length=200,
        description="비디오 주제 - 명확하고 구체적인 주제",
        examples=["Why are dachshunds so short?", "How blockchain technology works"]
    )
    
    length_preference: LengthPreference = Field(
        default=LengthPreference.MEDIUM,
        description="원하는 비디오 길이"
    )
    
    style_profile: str = Field(
        default="educational and engaging",
        min_length=10,
        description="전체적인 스타일과 톤",
        examples=["educational and engaging", "serious and informative", "playful and entertaining"]
    )
    
    target_audience: str = Field(
        default="general",
        description="대상 청중",
        examples=["general", "students", "professionals", "children"]
    )
    
    language: Language = Field(
        default=Language.ENGLISH,
        description="콘텐츠 언어"
    )
    
    knowledge_refs: Optional[List[str]] = Field(
        default=None,
        description="참고 자료 (URL, 논문, 책 등)",
        examples=[
            ["https://example.com/research", "Smith et al. (2023) Nature Paper"]
        ]
    )

    class Config:
        """Pydantic 설정"""
        json_schema_extra = {
            "title": "FullScriptInput",
            "description": "Full Script Writer Agent의 입력 데이터 구조"
        }


class SceneExpansionInput(BaseModel):
    """
    Scene Script Writer 입력 스키마
    FSW의 출력을 받아서 상세한 씬으로 확장
    """
    scene_data: Dict[str, Any] = Field(
        description="FSW에서 생성된 씬 비트 데이터",
        examples=[{
            "scene_number": 1,
            "scene_type": "hook",
            "beats": ["Introduce surprising fact about topic"],
            "learning_objectives": ["Capture viewer attention"],
            "needs_animation": True,
            "scene_importance": 5
        }]
    )
    
    global_context: Dict[str, Any] = Field(
        description="글로벌 컨텍스트 (캐릭터, 스타일, 제약사항)",
        examples=[{
            "main_character": "Glowbie",
            "cosplay_instructions": "Scientist with lab coat",
            "overall_style": "educational and engaging",
            "target_audience": "general"
        }]
    )
    
    previous_scenes: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="연속성을 위한 이전 씬들 (선택사항)"
    )
    
    educational_enhancement_guidelines: Optional[Dict[str, Any]] = Field(
        default=None,
        description="교육적 강화 가이드라인"
    )

    class Config:
        json_schema_extra = {
            "title": "SceneExpansionInput", 
            "description": "Scene Script Writer Agent의 입력 데이터 구조"
        }


class ImageGenerationInput(BaseModel):
    """
    Image Create Agent 입력 스키마
    SSW의 비주얼 사양을 받아서 이미지 생성
    """
    visual_specs: List[Dict[str, Any]] = Field(
        min_length=1,
        description="비주얼 프레임 사양들",
        examples=[[{
            "frame_id": "1A",
            "shot_type": "medium",
            "image_prompt": "Educational scene with Glowbie character explaining concept",
            "aspect_ratio": "16:9",
            "character_pose": "pointing to diagram",
            "background": "classroom setting"
        }]]
    )
    
    session_id: str = Field(
        description="세션 ID (파일 저장 경로 결정)",
        pattern=r"^\d{8}-[a-f0-9-]{36}$"
    )
    
    cost_saving_mode: bool = Field(
        default=False,
        description="비용 절약 모드 (Mock 이미지 사용)"
    )
    
    character_reference: Optional[str] = Field(
        default=None,
        description="캐릭터 일관성을 위한 참조 이미지 경로"
    )

    class Config:
        json_schema_extra = {
            "title": "ImageGenerationInput",
            "description": "Image Create Agent의 입력 데이터 구조"
        }


class VoiceGenerationInput(BaseModel):
    """
    Voice Generate Agent 입력 스키마
    SSW의 나레이션을 받아서 TTS 생성
    """
    scene_packages: List[Dict[str, Any]] = Field(
        min_length=1,
        description="음성을 생성할 씬 패키지들"
    )
    
    session_id: str = Field(
        description="세션 ID",
        pattern=r"^\d{8}-[a-f0-9-]{36}$"
    )
    
    voice_settings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="음성 설정 (엔진, 음성, 속도 등)"
    )

    class Config:
        json_schema_extra = {
            "title": "VoiceGenerationInput",
            "description": "Voice Generate Agent의 입력 데이터 구조"
        }


class VideoAssemblyInput(BaseModel):
    """
    Video Maker Agent 입력 스키마
    모든 에셋을 받아서 최종 비디오 조립
    """
    session_id: str = Field(
        description="세션 ID",
        pattern=r"^\d{8}-[a-f0-9-]{36}$"
    )
    
    image_assets: List[Dict[str, Any]] = Field(
        description="이미지 에셋들"
    )
    
    voice_assets: List[Dict[str, Any]] = Field(
        description="음성 에셋들"
    )
    
    scene_packages: List[Dict[str, Any]] = Field(
        description="타이밍 정보가 포함된 씬 패키지들"
    )
    
    video_settings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="비디오 설정 (해상도, FPS, 품질 등)"
    )

    class Config:
        json_schema_extra = {
            "title": "VideoAssemblyInput",
            "description": "Video Maker Agent의 입력 데이터 구조"
        }
