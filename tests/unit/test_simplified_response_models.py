"""
테스트: 단순화된 응답 모델
실제 사용되는 기능들만 포함한 실용적인 모델 테스트
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.simplified_response_models import (
    SimplifiedNarrationLine,
    SimplifiedVisual, 
    SimplifiedTTSSettings,
    SimplifiedTiming,
    SimplifiedScenePackage,
    SimplifiedLLMResponseProcessor
)


class TestSimplifiedNarrationLine:
    """단순화된 나레이션 라인 테스트"""

    def test_standard_format(self):
        """표준 형식 처리"""
        data = {
            "line": "Hello, this is a test narration.",
            "at_ms": 1000,
            "pause_ms": 500
        }
        
        narration = SimplifiedNarrationLine.model_validate(data)
        
        assert narration.line == "Hello, this is a test narration."
        assert narration.at_ms == 1000
        assert narration.pause_ms == 500

    def test_string_input(self):
        """단순 문자열 입력"""
        narration = SimplifiedNarrationLine.model_validate("This is a simple narration line.")
        
        assert narration.line == "This is a simple narration line."
        assert narration.at_ms == 0
        assert narration.pause_ms == 500

    def test_field_name_variations(self):
        """다양한 필드명 변형"""
        data = {
            "text": "Welcome to the show",
            "start_ms": 2000,
            "pause": 800
        }
        
        narration = SimplifiedNarrationLine.model_validate(data)
        assert narration.line == "Welcome to the show"
        assert narration.at_ms == 2000
        assert narration.pause_ms == 800


class TestSimplifiedVisual:
    """단순화된 비주얼 테스트"""

    def test_standard_format(self):
        """표준 형식 처리"""
        data = {
            "frame_id": "1A",
            "shot_type": "medium",
            "image_prompt": "A detailed educational scene with character",
            "aspect_ratio": "16:9"
        }
        
        visual = SimplifiedVisual.model_validate(data)
        
        assert visual.frame_id == "1A"
        assert visual.shot_type == "medium"
        assert visual.image_prompt == "A detailed educational scene with character"
        assert visual.aspect_ratio == "16:9"

    def test_field_name_variations(self):
        """필드명 변형 처리"""
        data = {
            "id": "2B",
            "prompt": "A complex scene with multiple elements",
            "negative": "low quality, blurry"
        }
        
        visual = SimplifiedVisual.model_validate(data)
        assert visual.frame_id == "2B"
        assert visual.image_prompt == "A complex scene with multiple elements"
        assert visual.negative_prompt == "low quality, blurry"

    def test_missing_required_fields(self):
        """필수 필드 누락 시 기본값"""
        data = {"shot_type": "close"}
        
        visual = SimplifiedVisual.model_validate(data)
        assert visual.frame_id == "1A"  # 기본값
        assert len(visual.image_prompt) >= 40  # 기본값


class TestSimplifiedTTSSettings:
    """단순화된 TTS 설정 테스트"""

    def test_standard_format(self):
        """표준 형식 처리"""
        data = {
            "engine": "lemonfox",
            "voice": "sarah",
            "language": "en-US",
            "speed": 1.2
        }
        
        tts = SimplifiedTTSSettings.model_validate(data)
        
        assert tts.engine == "lemonfox"
        assert tts.voice == "sarah"
        assert tts.speed == 1.2

    def test_elevenlabs_fields_removed(self):
        """ElevenLabs 관련 필드들이 제거되는지 테스트"""
        data = {
            "engine": "elevenlabs",  # 이건 유지
            "voice": "Adam",
            "elevenlabs_settings": {  # 이건 제거되어야 함
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.7
            },
            "stability": 0.5,  # 이것도 제거되어야 함
            "speed": 1.1
        }
        
        tts = SimplifiedTTSSettings.model_validate(data)
        
        # ElevenLabs 필드들이 제거되고 기본값으로 변경
        assert tts.engine == "lemonfox"  # elevenlabs -> lemonfox로 변경
        assert tts.voice == "sarah"      # Adam -> sarah로 변경
        assert tts.speed == 1.0          # 기본값으로 변경

    def test_empty_input(self):
        """빈 입력 시 기본값 설정"""
        tts = SimplifiedTTSSettings.model_validate({})
        
        assert tts.engine == "lemonfox"
        assert tts.voice == "sarah"
        assert tts.language == "en-US"
        assert tts.speed == 1.0


class TestSimplifiedTiming:
    """단순화된 타이밍 테스트"""

    def test_standard_format(self):
        """표준 형식 처리"""
        data = {
            "total_ms": 15000,
            "estimated": False
        }
        
        timing = SimplifiedTiming.model_validate(data)
        
        assert timing.total_ms == 15000
        assert timing.estimated == False

    def test_duration_field_mapping(self):
        """duration 필드 매핑"""
        data = {"duration": 8000}
        
        timing = SimplifiedTiming.model_validate(data)
        assert timing.total_ms == 8000
        assert timing.estimated == True  # 기본값

    def test_empty_input(self):
        """빈 입력 시 기본값"""
        timing = SimplifiedTiming.model_validate({})
        
        assert timing.total_ms == 5000
        assert timing.estimated == True


class TestSimplifiedScenePackage:
    """단순화된 씬 패키지 테스트"""

    def test_standard_format(self):
        """표준 형식 처리"""
        data = {
            "scene_number": 1,
            "narration_script": [
                {
                    "line": "Welcome to scene 1",
                    "at_ms": 0,
                    "pause_ms": 500
                }
            ],
            "visuals": [
                {
                    "frame_id": "1A",
                    "image_prompt": "A detailed educational scene",
                    "aspect_ratio": "16:9"
                }
            ],
            "tts": {
                "engine": "lemonfox",
                "voice": "sarah"
            },
            "timing": {"total_ms": 5000}
        }
        
        scene = SimplifiedScenePackage.model_validate(data)
        
        assert scene.scene_number == 1
        assert len(scene.narration_script) == 1
        assert len(scene.visuals) == 1
        assert scene.tts.engine == "lemonfox"
        assert scene.timing.total_ms == 5000

    def test_sfx_fields_removed(self):
        """SFX 관련 필드들이 제거되는지 테스트"""
        data = {
            "scene_number": 2,
            "narration_script": ["Hello world"],
            "visuals": [],
            "sfx_cues": [  # 이건 제거되어야 함
                {
                    "cue": "whoosh_sound",
                    "at_ms": 1000,
                    "duration_ms": 500
                }
            ],
            "sound_effects": [  # 이것도 제거되어야 함
                {"effect": "background_music"}
            ]
        }
        
        scene = SimplifiedScenePackage.model_validate(data)
        
        # SFX 필드들이 제거되었는지 확인
        scene_dict = scene.model_dump()
        assert 'sfx_cues' not in scene_dict
        assert 'sound_effects' not in scene_dict
        
        # 다른 필드들은 정상 처리
        assert scene.scene_number == 2

    def test_elevenlabs_settings_removed_from_tts(self):
        """TTS에서 ElevenLabs 설정이 제거되는지 테스트"""
        data = {
            "scene_number": 1,
            "tts": {
                "engine": "elevenlabs",
                "voice": "Adam", 
                "elevenlabs_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8
                }
            }
        }
        
        scene = SimplifiedScenePackage.model_validate(data)
        
        # ElevenLabs 관련이 제거되고 LemonFox로 변경
        assert scene.tts.engine == "lemonfox"
        assert scene.tts.voice == "sarah"
        
        # ElevenLabs 설정이 없는지 확인
        tts_dict = scene.tts.model_dump()
        assert 'elevenlabs_settings' not in tts_dict
        assert 'stability' not in tts_dict

    def test_timing_should_be_calculated_from_tts(self):
        """타이밍은 TTS 결과를 기반으로 계산되어야 함"""
        data = {
            "scene_number": 1,
            "narration_script": [
                {"line": "Short line", "at_ms": 0},
                {"line": "This is a much longer narration line that should take more time", "at_ms": 2000}
            ],
            "timing": {"total_ms": 1000}  # 실제로는 더 길어야 함
        }
        
        scene = SimplifiedScenePackage.model_validate(data)
        
        # 타이밍이 estimated=True로 설정되어야 함 (실제 TTS 기반 계산 필요)
        assert scene.timing.estimated == True
        
        # 실제 구현에서는 narration_script 길이를 기반으로 timing 재계산해야 함
        # (이는 별도 로직에서 처리)

    def test_missing_required_fields_with_defaults(self):
        """필수 필드 누락 시 기본값 설정"""
        data = {
            "narration_script": ["Hello world"]
        }
        # scene_number, visuals, tts, timing 누락
        
        scene = SimplifiedScenePackage.model_validate(data)
        
        assert scene.scene_number == 1  # 기본값
        assert len(scene.visuals) == 0  # 빈 리스트
        assert scene.tts.engine == "lemonfox"  # 기본값
        assert scene.timing.total_ms == 5000  # 기본값


class TestSimplifiedLLMResponseProcessor:
    """단순화된 LLM 응답 프로세서 테스트"""

    def test_clean_json_response_without_sfx(self):
        """SFX 없는 깨끗한 JSON 응답 처리"""
        response = '''
        {
            "scene_number": 1,
            "narration_script": [
                {
                    "line": "Welcome to our video",
                    "at_ms": 0,
                    "pause_ms": 500
                }
            ],
            "visuals": [
                {
                    "frame_id": "1A",
                    "image_prompt": "Educational scene with character",
                    "aspect_ratio": "16:9"
                }
            ],
            "tts": {
                "engine": "lemonfox",
                "voice": "sarah"
            },
            "timing": {"total_ms": 5000}
        }
        '''
        
        scene = SimplifiedLLMResponseProcessor.safe_parse_scene(response)
        
        assert scene.scene_number == 1
        assert len(scene.narration_script) == 1
        assert len(scene.visuals) == 1
        assert scene.tts.engine == "lemonfox"
        
        # SFX 관련 필드가 없어야 함
        scene_dict = scene.model_dump()
        assert 'sfx_cues' not in scene_dict or len(scene_dict.get('sfx_cues', [])) == 0

    def test_response_with_sfx_gets_cleaned(self):
        """SFX가 포함된 응답이 정리되는지 테스트"""
        response = '''
        {
            "scene_number": 2,
            "narration_script": ["Hello from scene 2"],
            "sfx_cues": [
                {"cue": "whoosh_sound", "at_ms": 1000}
            ],
            "sound_effects": [
                {"effect": "background_music"}
            ]
        }
        '''
        
        scene = SimplifiedLLMResponseProcessor.safe_parse_scene(response)
        
        assert scene.scene_number == 2
        
        # SFX 관련 필드들이 제거되었는지 확인
        scene_dict = scene.model_dump()
        assert 'sfx_cues' not in scene_dict
        assert 'sound_effects' not in scene_dict

    def test_timing_marked_as_estimated(self):
        """타이밍이 추정값으로 표시되는지 테스트"""
        response = '''
        {
            "scene_number": 1,
            "timing": {"total_ms": 8000}
        }
        '''
        
        scene = SimplifiedLLMResponseProcessor.safe_parse_scene(response)
        
        # 타이밍이 추정값으로 표시되어야 함 (실제 TTS 기반 계산 필요)
        assert scene.timing.estimated == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
