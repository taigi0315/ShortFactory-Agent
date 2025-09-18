"""
통합 테스트: 강화된 씬 스크립트 라이터 에이전트
실제 SceneScriptWriterAgent가 새로운 Enhanced 모델을 잘 사용하는지 확인
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.scene_script_writer_agent import SceneScriptWriterAgent
from core.enhanced_response_models import EnhancedScenePackage, LLMResponseProcessor


class TestEnhancedSceneWriterIntegration:
    """강화된 씬 라이터 통합 테스트"""

    def test_parse_response_with_enhanced_processor(self):
        """새로운 Enhanced 프로세서를 사용한 응답 파싱 테스트"""
        
        # Mock response with field name variations (LLM이 다른 필드명 사용)
        mock_llm_response = '''
        {
            "scene_id": 2,
            "script": [
                {
                    "text": "Welcome to our enhanced scene",
                    "start_ms": 1000,
                    "end_ms": 4000
                }
            ],
            "sound_effects": [
                {
                    "effect": "background music",
                    "begin_ms": 500,
                    "duration": 3000
                }
            ],
            "timing": {"total_ms": 5000}
        }
        '''
        
        # SceneScriptWriterAgent 인스턴스 생성 (API 키 없이)
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            agent = SceneScriptWriterAgent()
        
        # Enhanced processor를 사용한 파싱 테스트
        result = agent._parse_response_with_pydantic(mock_llm_response, scene_number=2)
        
        # 결과 검증
        assert isinstance(result, dict)
        assert result['scene_number'] == 2
        
        # 필드명이 정규화되었는지 확인
        assert 'narration_script' in result
        assert len(result['narration_script']) == 1
        
        narration = result['narration_script'][0]
        assert narration['line'] == "Welcome to our enhanced scene"
        assert narration['at_ms'] == 1000
        assert narration['duration_ms'] == 3000  # end_ms - start_ms
        
        # SFX 정규화 확인
        assert 'sfx_cues' in result
        assert len(result['sfx_cues']) == 1
        
        sfx = result['sfx_cues'][0]
        assert sfx['cue'] == "SFX_BACKGROUND_MUSIC"
        assert sfx['at_ms'] == 500
        assert sfx['duration_ms'] == 3000

    def test_parse_malformed_json_with_fallback(self):
        """잘못된 JSON도 fallback으로 처리되는지 테스트"""
        
        # 심각하게 손상된 JSON
        malformed_response = '''
        {
            "scene_number": 3,
            "narration_script": ["Hello world",  // 후행 쉼표와 주석
        '''
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            agent = SceneScriptWriterAgent()
        
        # 잘못된 JSON도 처리되어야 함
        result = agent._parse_response_with_pydantic(malformed_response, scene_number=3)
        
        # 결과 검증 - fallback이 동작해야 함
        assert isinstance(result, dict)
        assert result['scene_number'] == 3
        assert 'narration_script' in result
        assert len(result['narration_script']) >= 1
        
        # fallback이 사용되었다는 표시가 있어야 함 (로그에서 확인 가능)

    def test_parse_completely_invalid_response(self):
        """완전히 무효한 응답도 처리되는지 테스트"""
        
        invalid_response = "I'm sorry, I cannot help with that request."
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            agent = SceneScriptWriterAgent()
        
        # 무효한 응답도 처리되어야 함
        result = agent._parse_response_with_pydantic(invalid_response, scene_number=5)
        
        # 결과 검증
        assert isinstance(result, dict)
        assert result['scene_number'] == 5
        assert 'narration_script' in result
        assert len(result['narration_script']) >= 1
        
        # 텍스트에서 추출하거나 fallback 메시지가 있어야 함
        line_text = result['narration_script'][0]['line'].lower()
        assert len(line_text) > 0

    def test_enhanced_processor_direct_usage(self):
        """Enhanced 프로세서를 직접 사용하는 테스트"""
        
        # 복잡한 필드명 변형이 있는 응답
        complex_response = '''
        {
            "scene_id": 4,
            "narration": [
                {
                    "content": "This is a complex test",
                    "timing": "2.5s"
                }
            ],
            "sfx": [
                {
                    "name": "typing sound",
                    "start": "1s",
                    "length": "1.5s"
                }
            ]
        }
        '''
        
        # LLMResponseProcessor 직접 사용
        scene_package = LLMResponseProcessor.safe_parse_scene(
            complex_response, 
            fallback_scene_number=4
        )
        
        # 결과 검증
        assert isinstance(scene_package, EnhancedScenePackage)
        assert scene_package.scene_number == 4
        
        # 나레이션 정규화 확인
        assert len(scene_package.narration_script) == 1
        narration = scene_package.narration_script[0]
        assert narration.line == "This is a complex test"
        assert narration.duration_ms == 2500  # "2.5s" -> 2500ms
        
        # SFX 정규화 확인
        assert len(scene_package.sfx_cues) == 1
        sfx = scene_package.sfx_cues[0]
        assert sfx.cue == "SFX_TYPING_SOUND"
        assert sfx.at_ms == 1000  # "1s" -> 1000ms
        assert sfx.duration_ms == 1500  # "1.5s" -> 1500ms

    def test_backward_compatibility_with_dict_conversion(self):
        """기존 코드와의 호환성을 위한 dict 변환 테스트"""
        
        response = '''
        {
            "scene_number": 1,
            "narration_script": [
                {
                    "line": "Compatibility test",
                    "at_ms": 0,
                    "duration_ms": 2000
                }
            ]
        }
        '''
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            agent = SceneScriptWriterAgent()
        
        result = agent._parse_response_with_pydantic(response, scene_number=1)
        
        # dict 형태로 반환되는지 확인
        assert isinstance(result, dict)
        
        # 기존 코드에서 기대하는 구조인지 확인
        assert 'scene_number' in result
        assert 'narration_script' in result
        assert 'visuals' in result
        assert 'sfx_cues' in result
        assert 'timing' in result
        
        # 모든 필드가 JSON 직렬화 가능한지 확인
        import json
        json_str = json.dumps(result)
        assert len(json_str) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
