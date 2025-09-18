"""
테스트: 강화된 응답 모델 (Pydantic 기반)
LLM 응답의 다양한 변형을 Pydantic으로 완전히 흡수하는지 확인
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.enhanced_response_models import (
    EnhancedSFXCue, 
    EnhancedNarrationLine, 
    EnhancedScenePackage,
    LLMResponseProcessor,
    TransitionType
)


class TestEnhancedSFXCue:
    """강화된 SFX 큐 테스트"""

    def test_standard_format(self):
        """표준 형식 처리"""
        data = {
            "cue": "SFX_TYPING",
            "at_ms": 1000,
            "duration_ms": 2000,
            "volume": 0.7
        }
        
        sfx = EnhancedSFXCue.model_validate(data)
        
        assert sfx.cue == "SFX_TYPING"
        assert sfx.at_ms == 1000
        assert sfx.duration_ms == 2000
        assert sfx.volume == 0.7

    def test_llm_field_name_variations(self):
        """LLM이 다른 필드명을 사용하는 경우"""
        # Case 1: sfx_name, start_ms, end_ms
        data1 = {
            "sfx_name": "TYPING_SOUND",
            "start_ms": 1000,
            "end_ms": 3000
        }
        
        sfx1 = EnhancedSFXCue.model_validate(data1)
        assert sfx1.cue == "SFX_TYPING_SOUND"
        assert sfx1.at_ms == 1000
        assert sfx1.duration_ms == 2000  # end_ms - start_ms
        
        # Case 2: effect, begin_ms, duration
        data2 = {
            "effect": "keyboard typing",
            "begin_ms": 500,
            "duration": 1500
        }
        
        sfx2 = EnhancedSFXCue.model_validate(data2)
        assert sfx2.cue == "SFX_KEYBOARD_TYPING"
        assert sfx2.at_ms == 500
        assert sfx2.duration_ms == 1500

    def test_string_input(self):
        """LLM이 단순 문자열로 응답하는 경우"""
        sfx = EnhancedSFXCue.model_validate("typing sound")
        
        assert sfx.cue == "SFX_TYPING_SOUND"
        assert sfx.at_ms == 0
        assert sfx.duration_ms == 2000
        assert sfx.volume == 0.5

    def test_string_number_conversion(self):
        """문자열 숫자 변환"""
        data = {
            "cue": "BELL",
            "at_ms": "1500",
            "duration_ms": "2500.0"
        }
        
        sfx = EnhancedSFXCue.model_validate(data)
        
        assert sfx.at_ms == 1500
        assert sfx.duration_ms == 2500

    def test_missing_fields_with_defaults(self):
        """필수 필드 누락 시 기본값 설정"""
        data = {"sound_effect": "BELL"}  # 다른 필드들 누락
        
        sfx = EnhancedSFXCue.model_validate(data)
        
        assert sfx.cue == "SFX_BELL"
        assert sfx.at_ms == 0  # 기본값
        assert sfx.duration_ms == 2000  # 기본값
        assert sfx.volume == 0.5  # 기본값


class TestEnhancedNarrationLine:
    """강화된 나레이션 라인 테스트"""

    def test_standard_format(self):
        """표준 형식 처리"""
        data = {
            "line": "Hello, this is a test narration.",
            "at_ms": 1000,
            "duration_ms": 3000,
            "pause_after_ms": 500
        }
        
        narration = EnhancedNarrationLine.model_validate(data)
        
        assert narration.line == "Hello, this is a test narration."
        assert narration.at_ms == 1000
        assert narration.duration_ms == 3000
        assert narration.pause_after_ms == 500

    def test_string_input(self):
        """단순 문자열 입력"""
        narration = EnhancedNarrationLine.model_validate("This is a simple narration line.")
        
        assert narration.line == "This is a simple narration line."
        assert narration.at_ms == 0
        assert narration.duration_ms >= 2000  # 텍스트 길이 기반 계산
        assert narration.pause_after_ms == 500

    def test_field_name_variations(self):
        """다양한 필드명 변형"""
        # Case 1: text, start_ms, end_ms
        data1 = {
            "text": "Welcome to the show",
            "start_ms": 2000,
            "end_ms": 5000
        }
        
        narration1 = EnhancedNarrationLine.model_validate(data1)
        assert narration1.line == "Welcome to the show"
        assert narration1.at_ms == 2000
        assert narration1.duration_ms == 3000  # end_ms - start_ms
        
        # Case 2: content, timing
        data2 = {
            "content": "This is the content",
            "timing": 4000
        }
        
        narration2 = EnhancedNarrationLine.model_validate(data2)
        assert narration2.line == "This is the content"
        assert narration2.duration_ms == 4000

    def test_time_string_conversion(self):
        """시간 문자열 변환"""
        data = {
            "line": "Test line",
            "at_ms": "1.5s",  # 1.5초
            "duration_ms": "3s",  # 3초
            "pause_after_ms": "0.5s"  # 0.5초
        }
        
        narration = EnhancedNarrationLine.model_validate(data)
        
        assert narration.at_ms == 1500  # 1.5s -> 1500ms
        assert narration.duration_ms == 3000  # 3s -> 3000ms
        assert narration.pause_after_ms == 500  # 0.5s -> 500ms

    def test_auto_duration_calculation(self):
        """자동 지속시간 계산"""
        short_text = "Hi"
        long_text = "This is a much longer narration line that should have a longer duration."
        
        short_narration = EnhancedNarrationLine.model_validate(short_text)
        long_narration = EnhancedNarrationLine.model_validate(long_text)
        
        assert short_narration.duration_ms >= 1000  # 최소 1초
        assert long_narration.duration_ms > short_narration.duration_ms


class TestEnhancedScenePackage:
    """강화된 씬 패키지 테스트"""

    def test_standard_format(self):
        """표준 형식 처리"""
        data = {
            "scene_number": 1,
            "narration_script": [
                {
                    "line": "Welcome to scene 1",
                    "at_ms": 0,
                    "duration_ms": 3000
                }
            ],
            "visuals": [],
            "sfx_cues": [
                {
                    "cue": "SFX_INTRO",
                    "at_ms": 0,
                    "duration_ms": 1000
                }
            ],
            "timing": {"total_ms": 5000}
        }
        
        scene = EnhancedScenePackage.model_validate(data)
        
        assert scene.scene_number == 1
        assert len(scene.narration_script) == 1
        assert len(scene.sfx_cues) == 1
        assert scene.timing["total_ms"] == 5000

    def test_field_name_variations(self):
        """다양한 필드명 변형"""
        data = {
            "scene_id": 2,  # scene_number 대신
            "script": [  # narration_script 대신
                "This is a narration line"
            ],
            "sound_effects": [  # sfx_cues 대신
                {
                    "name": "BACKGROUND_MUSIC",
                    "start": 0,
                    "length": 3000
                }
            ],
            "text_overlays": []  # on_screen_text 대신
        }
        
        scene = EnhancedScenePackage.model_validate(data)
        
        assert scene.scene_number == 2
        assert len(scene.narration_script) == 1
        assert scene.narration_script[0].line == "This is a narration line"
        assert len(scene.sfx_cues) == 1
        assert scene.sfx_cues[0].cue == "SFX_BACKGROUND_MUSIC"

    def test_missing_required_fields(self):
        """필수 필드 누락 시 기본값 설정"""
        data = {
            "narration_script": ["Hello world"]
        }
        # scene_number 누락
        
        scene = EnhancedScenePackage.model_validate(data)
        
        assert scene.scene_number == 1  # 기본값
        assert len(scene.narration_script) == 1
        assert isinstance(scene.visuals, list)
        assert isinstance(scene.sfx_cues, list)
        assert isinstance(scene.timing, dict)

    def test_transition_normalization(self):
        """전환 타입 정규화"""
        data = {
            "scene_number": 1,
            "transition_in": "fade_to_black",  # 비표준 값
            "transition_out": "hard_cut"       # 비표준 값
        }
        
        scene = EnhancedScenePackage.model_validate(data)
        
        assert scene.transition_in == TransitionType.FADE
        assert scene.transition_out == TransitionType.CUT

    def test_completely_malformed_data(self):
        """완전히 잘못된 데이터 처리"""
        # 딕셔너리가 아닌 데이터
        scene = EnhancedScenePackage.model_validate("not a dict")
        
        assert scene.scene_number == 1
        assert isinstance(scene.narration_script, list)
        assert isinstance(scene.timing, dict)


class TestLLMResponseProcessor:
    """LLM 응답 프로세서 테스트"""

    def test_clean_json_response(self):
        """깨끗한 JSON 응답 처리"""
        response = '''
        {
            "scene_number": 1,
            "narration_script": [
                {
                    "line": "Welcome to our video",
                    "at_ms": 0,
                    "duration_ms": 3000
                }
            ],
            "sfx_cues": [
                {
                    "cue": "SFX_INTRO",
                    "at_ms": 0,
                    "duration_ms": 1000
                }
            ],
            "timing": {"total_ms": 5000}
        }
        '''
        
        scene = LLMResponseProcessor.safe_parse_scene(response)
        
        assert scene.scene_number == 1
        assert len(scene.narration_script) == 1
        assert scene.narration_script[0].line == "Welcome to our video"
        assert len(scene.sfx_cues) == 1

    def test_markdown_wrapped_json(self):
        """마크다운으로 감싸진 JSON"""
        response = '''
        Here's the scene package:
        
        ```json
        {
            "scene_number": 2,
            "narration_script": ["Hello from scene 2"],
            "timing": {"total_ms": 4000}
        }
        ```
        
        Hope this helps!
        '''
        
        scene = LLMResponseProcessor.safe_parse_scene(response)
        
        assert scene.scene_number == 2
        assert len(scene.narration_script) == 1

    def test_malformed_json_response(self):
        """잘못된 JSON 응답"""
        response = '''
        {
            "scene_number": 1,
            "narration_script": ["Hello world",  // 후행 쉼표
        '''
        
        # 파싱이 실패해도 fallback이 동작해야 함
        scene = LLMResponseProcessor.safe_parse_scene(response, fallback_scene_number=3)
        
        assert scene.scene_number == 3  # fallback 값 사용
        assert len(scene.narration_script) >= 1  # 최소 하나의 라인

    def test_completely_invalid_response(self):
        """완전히 무효한 응답"""
        response = "I'm sorry, I cannot help with that request."
        
        scene = LLMResponseProcessor.safe_parse_scene(response, fallback_scene_number=5)
        
        assert scene.scene_number == 5
        assert len(scene.narration_script) >= 1
        # 텍스트에서 추출했으므로 원본 텍스트나 fallback 메시지가 있어야 함
        line_text = scene.narration_script[0].line.lower()
        assert ("sorry" in line_text) or ("issue" in line_text)

    def test_mixed_field_names_response(self):
        """혼합된 필드명 사용"""
        response = '''
        {
            "scene_id": 3,
            "script": [
                {
                    "text": "Mixed field names test",
                    "start_ms": 1000,
                    "end_ms": 4000
                }
            ],
            "sound_effects": [
                {
                    "effect": "typing sound",
                    "begin_ms": 2000,
                    "duration": 1000
                }
            ]
        }
        '''
        
        scene = LLMResponseProcessor.safe_parse_scene(response)
        
        assert scene.scene_number == 3
        assert len(scene.narration_script) == 1
        assert scene.narration_script[0].line == "Mixed field names test"
        assert scene.narration_script[0].at_ms == 1000
        assert scene.narration_script[0].duration_ms == 3000  # end_ms - start_ms
        
        assert len(scene.sfx_cues) == 1
        assert scene.sfx_cues[0].cue == "SFX_TYPING_SOUND"
        assert scene.sfx_cues[0].at_ms == 2000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
