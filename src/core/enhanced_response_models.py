"""
Enhanced Response Models with Pydantic
LLM 응답의 변동성을 완전히 흡수하는 강력한 Pydantic 모델들
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Union, Any, Dict
from enum import Enum


class TransitionType(str, Enum):
    """전환 타입 - LLM이 다양하게 표현할 수 있는 값들"""
    FADE = "fade"
    CUT = "cut"
    DISSOLVE = "dissolve"
    SLIDE = "slide"
    WIPE = "wipe"
    PUSH = "push"


class EnhancedSFXCue(BaseModel):
    """
    강화된 SFX 큐 - LLM 응답의 다양한 변형을 자동 처리
    
    LLM이 이렇게 응답해도 모두 처리:
    - {"sfx_name": "TYPING", "start_ms": 1000, "end_ms": 3000}
    - {"effect": "TYPING_SOUND", "begin_ms": 1000, "duration": 2000}  
    - {"cue": "SFX_TYPING", "at_ms": 1000, "duration_ms": 2000}
    - {"sound_effect": "typing", "start": 1000, "length": 2000}
    """
    cue: str = Field(..., description="Sound effect cue name")
    at_ms: int = Field(..., description="Start time in milliseconds")
    duration_ms: int = Field(..., description="Duration in milliseconds")
    volume: float = Field(default=0.5, ge=0.0, le=1.0, description="Volume level")

    @model_validator(mode='before')
    @classmethod
    def normalize_llm_fields(cls, data: Any) -> Dict[str, Any]:
        """LLM이 다른 필드명을 사용해도 자동 매핑"""
        if isinstance(data, str):
            # LLM이 단순 문자열로 응답한 경우
            return {
                'cue': data.upper().replace(' ', '_'),
                'at_ms': 0,
                'duration_ms': 2000,
                'volume': 0.5
            }
        
        if not isinstance(data, dict):
            return data
        
        result = data.copy()
        
        # 필드명 매핑 테이블
        field_mappings = {
            # cue 필드 매핑
            'sfx_name': 'cue',
            'effect': 'cue', 
            'sound_effect': 'cue',
            'name': 'cue',
            'sfx': 'cue',
            
            # 시작 시간 매핑
            'start_ms': 'at_ms',
            'begin_ms': 'at_ms',
            'start': 'at_ms',
            'begin': 'at_ms',
            'start_time': 'at_ms',
            
            # 지속 시간 매핑
            'duration': 'duration_ms',
            'length_ms': 'duration_ms',
            'length': 'duration_ms',
            # end_ms는 여기서 매핑하지 않고 별도 처리
        }
        
        # 필드명 정규화
        for old_key, new_key in field_mappings.items():
            if old_key in result and new_key not in result:
                result[new_key] = result[old_key]
                del result[old_key]
        
        # end_ms를 duration_ms로 변환 (특별 처리)
        if 'end_ms' in result:
            start_time = result.get('at_ms', 0)
            if 'duration_ms' not in result:
                result['duration_ms'] = result['end_ms'] - start_time
            del result['end_ms']
        
        # 필수 필드 기본값 설정
        if 'cue' not in result:
            result['cue'] = 'SFX_GENERIC'
        if 'at_ms' not in result:
            result['at_ms'] = 0
        if 'duration_ms' not in result:
            result['duration_ms'] = 2000
        
        return result

    @field_validator('cue')
    @classmethod
    def normalize_cue_name(cls, v: str) -> str:
        """SFX 큐명 정규화"""
        if not v:
            return "SFX_GENERIC"
        
        # 대문자로 변환하고 공백을 언더스코어로
        normalized = str(v).upper().replace(' ', '_').replace('-', '_')
        
        # SFX_ 접두사가 없으면 추가
        if not normalized.startswith('SFX_'):
            normalized = f'SFX_{normalized}'
        
        return normalized

    @field_validator('at_ms', 'duration_ms', mode='before')
    @classmethod
    def convert_to_int(cls, v: Any) -> int:
        """문자열 숫자도 정수로 변환 (시간 문자열 포함)"""
        if isinstance(v, str):
            # "3.5s", "1000ms", "2s" 등의 형식 처리
            v_clean = v.lower().replace('ms', '').replace('s', '')
            try:
                float_val = float(v_clean)
                # 원본 문자열에 's'가 있고 'ms'가 없으면 초 단위로 간주
                if 's' in v.lower() and 'ms' not in v.lower():
                    return int(float_val * 1000)
                return int(float_val)
            except (ValueError, TypeError):
                return 0 if v == 'at_ms' else 1000
        return int(v)


class EnhancedNarrationLine(BaseModel):
    """
    강화된 나레이션 라인 - 다양한 LLM 응답 형식 지원
    
    LLM이 이렇게 응답해도 모두 처리:
    - "Hello world"  (단순 문자열)
    - {"text": "Hello", "timing": 3000}
    - {"line": "Hello", "start_ms": 0, "end_ms": 3000}
    - {"content": "Hello", "duration": "3.5s"}
    """
    line: str = Field(..., min_length=1, description="Text to be spoken")
    at_ms: int = Field(default=0, ge=0, description="Start time in milliseconds")
    duration_ms: int = Field(..., gt=0, description="Duration in milliseconds")
    pause_after_ms: int = Field(default=500, ge=0, description="Pause after this line")
    emphasis: Optional[str] = Field(default=None, description="Emphasis type")

    @model_validator(mode='before')
    @classmethod
    def normalize_narration_data(cls, data: Any) -> Dict[str, Any]:
        """다양한 나레이션 형식을 정규화"""
        
        # 단순 문자열인 경우
        if isinstance(data, str):
            text_length = len(data)
            estimated_duration = max(text_length * 80, 1000)  # 최소 1초
            return {
                'line': data,
                'at_ms': 0,
                'duration_ms': estimated_duration,
                'pause_after_ms': 500
            }
        
        if not isinstance(data, dict):
            return data
        
        result = data.copy()
        
        # 필드명 매핑
        field_mappings = {
            'text': 'line',
            'content': 'line',
            'narration': 'line',
            'script': 'line',
            'start_ms': 'at_ms',
            'begin_ms': 'at_ms',
            'timing': 'duration_ms',
            'length_ms': 'duration_ms',
            'pause': 'pause_after_ms',
        }
        
        for old_key, new_key in field_mappings.items():
            if old_key in result and new_key not in result:
                result[new_key] = result[old_key]
                del result[old_key]
        
        # duration_ms 자동 계산
        if 'duration_ms' not in result:
            if 'end_ms' in result:
                start_time = result.get('at_ms', 0)
                result['duration_ms'] = result['end_ms'] - start_time
                del result['end_ms']
            elif 'line' in result:
                # 텍스트 길이 기반 추정
                text_length = len(result['line'])
                result['duration_ms'] = max(text_length * 80, 1000)
        
        # 필수 필드 기본값
        if 'line' not in result:
            result['line'] = "Generated content"
        if 'duration_ms' not in result:
            result['duration_ms'] = 3000
        
        return result

    @field_validator('duration_ms', 'at_ms', 'pause_after_ms', mode='before')
    @classmethod
    def convert_time_values(cls, v: Any) -> int:
        """시간 값들을 정수로 변환 (문자열 포함)"""
        if isinstance(v, str):
            # "3.5s", "3000ms", "3s" 등의 형식 처리
            v_clean = v.lower().replace('ms', '').replace('s', '')
            try:
                float_val = float(v_clean)
                # 원본 문자열에 's'가 있고 'ms'가 없으면 초 단위로 간주
                if 's' in v.lower() and 'ms' not in v.lower():
                    return int(float_val * 1000)
                return int(float_val)
            except (ValueError, TypeError):
                return 3000  # 기본값
        return int(v)


class EnhancedScenePackage(BaseModel):
    """
    강화된 씬 패키지 - LLM 응답의 모든 변형을 처리
    
    LLM이 어떤 필드명을 사용하든 자동으로 매핑하고 처리
    """
    scene_number: int = Field(..., ge=1, description="Scene number")
    narration_script: List[EnhancedNarrationLine] = Field(
        default_factory=list, 
        description="Narration lines with timing"
    )
    visuals: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Visual frames"
    )
    sfx_cues: List[EnhancedSFXCue] = Field(
        default_factory=list,
        description="Sound effect cues"
    )
    on_screen_text: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="On-screen text elements"
    )
    timing: Dict[str, Any] = Field(
        default_factory=lambda: {"total_ms": 5000},
        description="Scene timing"
    )
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
                'sfx_cues': [],
                'on_screen_text': [],
                'timing': {'total_ms': 5000}
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
            'dialogue': 'narration_script',
            
            'sound_effects': 'sfx_cues',
            'sfx': 'sfx_cues',
            'sounds': 'sfx_cues',
            'effects': 'sfx_cues',
            
            'text_overlays': 'on_screen_text',
            'overlays': 'on_screen_text',
            'texts': 'on_screen_text',
            'captions': 'on_screen_text',
        }
        
        # 필드명 정규화
        for old_key, new_key in field_mappings.items():
            if old_key in result and new_key not in result:
                result[new_key] = result[old_key]
                # 원본 키는 삭제하지 않음 (혹시 모르니)
        
        # 필수 필드 기본값 설정
        if 'scene_number' not in result:
            result['scene_number'] = 1
            
        # 빈 리스트 기본값
        for field in ['narration_script', 'visuals', 'sfx_cues', 'on_screen_text']:
            if field not in result or result[field] is None:
                result[field] = []
        
        # timing 기본값
        if 'timing' not in result or not isinstance(result['timing'], dict):
            result['timing'] = {'total_ms': 5000}
        
        return result

    @field_validator('scene_number')
    @classmethod
    def convert_scene_number(cls, v: Any) -> int:
        """씬 번호를 정수로 변환"""
        if isinstance(v, str):
            try:
                return int(v)
            except (ValueError, TypeError):
                return 1
        return int(v)

    @field_validator('transition_in', 'transition_out', mode='before')
    @classmethod
    def normalize_transition(cls, v: Any) -> str:
        """전환 타입 정규화"""
        if not v:
            return "fade"
        
        v_str = str(v).lower().replace('_', '').replace('-', '')
        
        # 일반적인 매핑
        transition_mappings = {
            'fadetoblack': 'fade',
            'fadeout': 'fade',
            'fadein': 'fade',
            'crossfade': 'fade',
            'cutaway': 'cut',
            'hardcut': 'cut',
            'jumpcut': 'cut',
            'slideright': 'slide',
            'slideleft': 'slide',
            'slidein': 'slide',
            'slideout': 'slide',
        }
        
        # 매핑된 값이 있으면 사용
        if v_str in transition_mappings:
            return transition_mappings[v_str]
        
        # 유효한 enum 값인지 확인
        valid_transitions = [t.value for t in TransitionType]
        if v_str in valid_transitions:
            return v_str
        
        # 기본값
        return "fade"


class LLMResponseProcessor:
    """
    LLM 응답을 안전하게 처리하는 프로세서
    Pydantic의 강력한 검증 기능을 활용
    """
    
    @staticmethod
    def safe_parse_scene(raw_response: str, fallback_scene_number: int = 1) -> EnhancedScenePackage:
        """
        LLM 응답을 안전하게 씬 패키지로 변환
        
        Args:
            raw_response: LLM의 원시 응답
            fallback_scene_number: 실패 시 사용할 씬 번호
            
        Returns:
            EnhancedScenePackage: 검증된 씬 패키지
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
                parsed_data = LLMResponseProcessor._extract_data_from_text(raw_response, fallback_scene_number)
            
            # 3단계: Pydantic 모델로 검증 및 정규화
            scene_package = EnhancedScenePackage.model_validate(parsed_data)
            
            logger.info(f"✅ 씬 {scene_package.scene_number} 성공적으로 파싱됨")
            return scene_package
            
        except Exception as e:
            logger.error(f"씬 파싱 실패: {e}, fallback 사용")
            
            # 4단계: 완전한 fallback - 최소 유효 씬 생성
            fallback_data = {
                'scene_number': fallback_scene_number,
                'narration_script': [{
                    'line': f"This is scene {fallback_scene_number}. Content generation encountered an issue.",
                    'at_ms': 0,
                    'duration_ms': 4000
                }],
                'visuals': [],
                'sfx_cues': [],
                'on_screen_text': [],
                'timing': {'total_ms': 5000}
            }
            
            return EnhancedScenePackage.model_validate(fallback_data)
    
    @staticmethod
    def _extract_data_from_text(text: str, fallback_scene_number: int = 1) -> Dict[str, Any]:
        """텍스트에서 구조화된 데이터 추출 (최후 수단)"""
        import re
        
        # 기본 구조
        result = {
            'scene_number': fallback_scene_number,
            'narration_script': [],
            'visuals': [],
            'sfx_cues': [],
            'timing': {'total_ms': 5000}
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
                        'duration_ms': max(len(line) * 80, 2000)
                    })
        
        if narration_lines:
            result['narration_script'] = narration_lines
        else:
            # 완전히 추출 실패한 경우
            result['narration_script'] = [{
                'line': "Content could not be properly extracted from the response.",
                'at_ms': 0,
                'duration_ms': 4000
            }]
        
        return result
