"""
Simplified Response Models - 실제 사용되는 기능만 포함
SFX, ElevenLabs 등 사용하지 않는 기능 제거하고 실용적인 모델 구성
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Union, Any, Dict
from enum import Enum


class TransitionType(str, Enum):
    """전환 타입 - 실제 사용되는 것들만"""
    FADE = "fade"
    CUT = "cut"
    DISSOLVE = "dissolve"
    SLIDE = "slide"


class SimplifiedNarrationLine(BaseModel):
    """
    단순화된 나레이션 라인 - 실제 필요한 것들만
    timing은 TTS 결과를 기반으로 자동 계산됨
    """
    line: str = Field(..., min_length=1, description="Text to be spoken")
    at_ms: int = Field(default=0, ge=0, description="Start time in milliseconds")
    pause_ms: int = Field(default=500, ge=0, description="Pause after this line")

    @model_validator(mode='before')
    @classmethod
    def normalize_narration_data(cls, data: Any) -> Dict[str, Any]:
        """다양한 나레이션 형식을 정규화"""
        
        # 단순 문자열인 경우
        if isinstance(data, str):
            return {
                'line': data,
                'at_ms': 0,
                'pause_ms': 500
            }
        
        if not isinstance(data, dict):
            return data
        
        result = data.copy()
        
        # 필드명 매핑 (실제 LLM이 사용하는 변형들)
        field_mappings = {
            'text': 'line',
            'content': 'line',
            'narration': 'line',
            'script': 'line',
            'start_ms': 'at_ms',
            'begin_ms': 'at_ms',
            'pause': 'pause_ms',
            'pause_after_ms': 'pause_ms',
        }
        
        for old_key, new_key in field_mappings.items():
            if old_key in result and new_key not in result:
                result[new_key] = result[old_key]
                del result[old_key]
        
        # 필수 필드 기본값
        if 'line' not in result:
            result['line'] = "Generated content"
        
        return result


class SimplifiedVisual(BaseModel):
    """
    단순화된 비주얼 프레임 - 이미지 생성에 실제 필요한 것들만
    """
    frame_id: str = Field(..., description="Frame identifier like '1A', '2B'")
    shot_type: str = Field(default="medium", description="Camera shot type")
    image_prompt: str = Field(..., min_length=40, description="Detailed image generation prompt")
    negative_prompt: Optional[str] = Field(default=None, description="Negative prompt for image generation")
    aspect_ratio: str = Field(default="16:9", description="Image aspect ratio")
    
    # 선택적 비주얼 요소들
    character_pose: Optional[str] = Field(default=None, description="Character positioning")
    expression: Optional[str] = Field(default=None, description="Character expression")
    background: Optional[str] = Field(default=None, description="Background description")
    lighting: Optional[str] = Field(default=None, description="Lighting description")
    color_mood: Optional[str] = Field(default=None, description="Color palette and mood")

    @model_validator(mode='before')
    @classmethod
    def normalize_visual_data(cls, data: Any) -> Dict[str, Any]:
        """비주얼 데이터 정규화"""
        if not isinstance(data, dict):
            return data
        
        result = data.copy()
        
        # 필드명 매핑
        field_mappings = {
            'id': 'frame_id',
            'prompt': 'image_prompt',
            'negative': 'negative_prompt',
            'pose': 'character_pose',
        }
        
        for old_key, new_key in field_mappings.items():
            if old_key in result and new_key not in result:
                result[new_key] = result[old_key]
                del result[old_key]
        
        # 필수 필드 기본값
        if 'frame_id' not in result:
            result['frame_id'] = "1A"
        if 'image_prompt' not in result:
            result['image_prompt'] = "A simple educational scene with friendly character"
        
        return result


class SimplifiedTTSSettings(BaseModel):
    """
    단순화된 TTS 설정 - LemonFox 사용, ElevenLabs 제거
    """
    engine: str = Field(default="lemonfox", description="TTS engine")
    voice: str = Field(default="sarah", description="Voice name")
    language: str = Field(default="en-US", description="Language code")
    
    # LemonFox 설정 (ElevenLabs 설정 제거)
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")
    
    @model_validator(mode='before')
    @classmethod
    def normalize_tts_data(cls, data: Any) -> Dict[str, Any]:
        """TTS 데이터 정규화 - ElevenLabs 설정 무시"""
        if not isinstance(data, dict):
            return {
                'engine': 'lemonfox',
                'voice': 'sarah',
                'language': 'en-US',
                'speed': 1.0
            }
        
        result = data.copy()
        
        # ElevenLabs 관련 필드들 제거
        elevenlabs_fields = [
            'elevenlabs_settings', 'stability', 'similarity_boost', 
            'style', 'loudness'
        ]
        for field in elevenlabs_fields:
            if field in result:
                del result[field]
        
        # 기본값 설정
        if 'engine' not in result:
            result['engine'] = 'lemonfox'
        if 'voice' not in result:
            result['voice'] = 'sarah'
        if 'language' not in result:
            result['language'] = 'en-US'
        
        return result


class SimplifiedTiming(BaseModel):
    """
    단순화된 타이밍 - TTS 결과 기반으로 자동 계산
    """
    total_ms: int = Field(default=5000, gt=0, description="Total scene duration (calculated from TTS)")
    estimated: bool = Field(default=True, description="Whether timing is estimated or actual")
    
    @model_validator(mode='before')
    @classmethod
    def normalize_timing_data(cls, data: Any) -> Dict[str, Any]:
        """타이밍 데이터 정규화"""
        if not isinstance(data, dict):
            return {'total_ms': 5000, 'estimated': True}
        
        result = data.copy()
        
        # 필드명 매핑
        if 'duration' in result and 'total_ms' not in result:
            result['total_ms'] = result['duration']
            del result['duration']
        
        # 기본값
        if 'total_ms' not in result:
            result['total_ms'] = 5000
        if 'estimated' not in result:
            result['estimated'] = True
        
        return result


class SimplifiedScenePackage(BaseModel):
    """
    단순화된 씬 패키지 - 실제 사용되는 기능들만
    SFX, ElevenLabs, 복잡한 continuity 제거
    """
    scene_number: int = Field(..., ge=1, description="Scene number")
    narration_script: List[SimplifiedNarrationLine] = Field(
        default_factory=list, 
        description="Narration lines"
    )
    visuals: List[SimplifiedVisual] = Field(
        default_factory=list,
        description="Visual frames for image generation"
    )
    tts: SimplifiedTTSSettings = Field(
        default_factory=SimplifiedTTSSettings,
        description="TTS configuration"
    )
    timing: SimplifiedTiming = Field(
        default_factory=SimplifiedTiming,
        description="Scene timing (calculated from TTS)"
    )
    
    # 선택적 필드들
    dialogue: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Optional dialogue lines"
    )
    on_screen_text: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Optional on-screen text elements"
    )
    
    # 전환 관련 (단순화)
    transition_in: Optional[TransitionType] = Field(
        default=TransitionType.FADE,
        description="How this scene transitions in"
    )
    transition_out: Optional[TransitionType] = Field(
        default=TransitionType.FADE, 
        description="How this scene transitions out"
    )

    @model_validator(mode='before')
    @classmethod
    def normalize_scene_data(cls, data: Any) -> Dict[str, Any]:
        """씬 데이터의 모든 변형을 정규화"""
        
        if not isinstance(data, dict):
            # 완전히 잘못된 데이터인 경우 최소 구조 생성
            return {
                'scene_number': 1,
                'narration_script': [],
                'visuals': [],
                'tts': {},
                'timing': {}
            }
        
        result = data.copy()
        
        # 필드명 매핑 테이블
        field_mappings = {
            'scene_id': 'scene_number',
            'number': 'scene_number',
            'id': 'scene_number',
            
            'narration': 'narration_script',
            'script': 'narration_script',
            'lines': 'narration_script',
            
            'text_overlays': 'on_screen_text',
            'overlays': 'on_screen_text',
            'texts': 'on_screen_text',
        }
        
        # 필드명 정규화
        for old_key, new_key in field_mappings.items():
            if old_key in result and new_key not in result:
                result[new_key] = result[old_key]
        
        # SFX 관련 필드들 제거 (사용하지 않음)
        sfx_fields = ['sfx_cues', 'sfx', 'sound_effects', 'effects']
        for field in sfx_fields:
            if field in result:
                del result[field]
        
        # 복잡한 continuity 필드 제거 (단순한 transition만 유지)
        if 'continuity' in result:
            continuity = result['continuity']
            if isinstance(continuity, dict):
                if 'in_from' in continuity:
                    result['transition_in'] = continuity['in_from']
                if 'out_to' in continuity:
                    result['transition_out'] = continuity['out_to']
            del result['continuity']
        
        # 필수 필드 기본값 설정
        if 'scene_number' not in result:
            result['scene_number'] = 1
            
        # 빈 리스트 기본값
        for field in ['narration_script', 'visuals', 'dialogue', 'on_screen_text']:
            if field not in result or result[field] is None:
                result[field] = []
        
        # TTS와 timing 기본값
        if 'tts' not in result or not isinstance(result['tts'], dict):
            result['tts'] = {}
        if 'timing' not in result or not isinstance(result['timing'], dict):
            result['timing'] = {}
        
        return result

    @field_validator('scene_number', mode='before')
    @classmethod
    def convert_scene_number(cls, v: Any) -> int:
        """씬 번호를 정수로 변환"""
        if isinstance(v, str):
            try:
                return int(v)
            except (ValueError, TypeError):
                return 1
        return int(v)


class SimplifiedLLMResponseProcessor:
    """
    단순화된 LLM 응답 프로세서
    실제 사용되는 기능들만 포함
    """
    
    @staticmethod
    def safe_parse_scene(raw_response: str, fallback_scene_number: int = 1) -> SimplifiedScenePackage:
        """
        LLM 응답을 안전하게 단순화된 씬 패키지로 변환
        
        Args:
            raw_response: LLM의 원시 응답
            fallback_scene_number: 실패 시 사용할 씬 번호
            
        Returns:
            SimplifiedScenePackage: 검증된 씬 패키지
        """
        import json
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # 1단계: JSON 추출 시도
            json_str = raw_response.strip()
            
            # 마크다운 코드 블록 제거
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            elif json_str.startswith('```'):
                json_str = json_str[3:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            
            # JSON 경계 찾기
            start_idx = json_str.find('{')
            end_idx = json_str.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = json_str[start_idx:end_idx]
            
            # 2단계: JSON 파싱 시도
            try:
                parsed_data = json.loads(json_str)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 텍스트에서 정보 추출 시도
                logger.warning("JSON 파싱 실패, 텍스트에서 정보 추출 시도")
                parsed_data = SimplifiedLLMResponseProcessor._extract_data_from_text(raw_response, fallback_scene_number)
            
            # 3단계: Pydantic 모델로 검증 및 정규화
            scene_package = SimplifiedScenePackage.model_validate(parsed_data)
            
            logger.info(f"✅ 씬 {scene_package.scene_number} 성공적으로 파싱됨 (단순화된 모델)")
            return scene_package
            
        except Exception as e:
            logger.error(f"씬 파싱 실패: {e}, fallback 사용")
            
            # 4단계: 완전한 fallback - 최소 유효 씬 생성
            fallback_data = {
                'scene_number': fallback_scene_number,
                'narration_script': [{
                    'line': f"This is scene {fallback_scene_number}. Content generation encountered an issue.",
                    'at_ms': 0,
                    'pause_ms': 500
                }],
                'visuals': [{
                    'frame_id': f'{fallback_scene_number}A',
                    'image_prompt': 'A simple educational scene with friendly character',
                    'aspect_ratio': '16:9'
                }],
                'tts': {
                    'engine': 'lemonfox',
                    'voice': 'sarah'
                },
                'timing': {'total_ms': 5000, 'estimated': True}
            }
            
            return SimplifiedScenePackage.model_validate(fallback_data)
    
    @staticmethod
    def _extract_data_from_text(text: str, fallback_scene_number: int = 1) -> Dict[str, Any]:
        """텍스트에서 구조화된 데이터 추출 (최후 수단)"""
        import re
        
        # 기본 구조
        result = {
            'scene_number': fallback_scene_number,
            'narration_script': [],
            'visuals': [],
            'tts': {'engine': 'lemonfox', 'voice': 'sarah'},
            'timing': {'total_ms': 5000, 'estimated': True}
        }
        
        # 씬 번호 추출
        scene_match = re.search(r'scene[:\s]+(\d+)', text, re.IGNORECASE)
        if scene_match:
            result['scene_number'] = int(scene_match.group(1))
        
        # 나레이션 텍스트 추출 (간단한 패턴)
        lines = text.split('\n')
        narration_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('{') and not line.startswith('}') and len(line) > 10:
                # 실제 나레이션처럼 보이는 라인
                if any(word in line.lower() for word in ['the', 'this', 'that', 'how', 'why', 'what']):
                    narration_lines.append({
                        'line': line,
                        'at_ms': len(narration_lines) * 3000,
                        'pause_ms': 500
                    })
        
        if narration_lines:
            result['narration_script'] = narration_lines
        else:
            # 완전히 추출 실패한 경우
            result['narration_script'] = [{
                'line': "Content could not be properly extracted from the response.",
                'at_ms': 0,
                'pause_ms': 500
            }]
        
        # 기본 비주얼 프레임 추가
        result['visuals'] = [{
            'frame_id': f'{result["scene_number"]}A',
            'image_prompt': 'A simple educational scene with friendly character explaining the topic',
            'aspect_ratio': '16:9'
        }]
        
        return result
