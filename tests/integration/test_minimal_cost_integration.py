"""
비용 효율적인 통합 테스트
실제 API를 사용하지만 최소 비용으로 핵심 기능 검증
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from main import NewArchitectureRunner


# 통합 테스트 설정
INTEGRATION_TEST_CONFIG = {
    "max_scenes": 1,           # 최대 1개 씬만
    "frames_per_scene": 1,     # 씬당 1개 프레임만
    "cost_saving_mode": True,  # Mock 이미지 사용
    "voice_generation": False, # 음성 생성 스킵 (비용 절약)
    "short_topic": True,       # 짧은 토픽 사용
}


class TestMinimalCostIntegration:
    """최소 비용 통합 테스트"""

    def setup_method(self):
        """테스트 전 API 키 확인"""
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            pytest.skip("API 키가 없어서 통합 테스트 스킵")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_minimal_video_generation_text_only(self):
        """최소 비용으로 텍스트 생성만 테스트 (~$0.02)"""
        
        # 매우 짧은 토픽으로 비용 최소화
        topic = "AI"  # 2글자로 최소화
        
        try:
            runner = NewArchitectureRunner()
            
            # Mock을 사용해서 비용 최소화
            with patch.object(runner.orchestrator, 'scene_script_writer') as mock_ssw, \
                 patch.object(runner.orchestrator, 'image_create_agent') as mock_ica, \
                 patch.object(runner.orchestrator, 'voice_generate_agent') as mock_vga, \
                 patch.object(runner.orchestrator, 'video_maker_agent') as mock_vma:
                
                # 텍스트 생성만 실제로 하고 나머지는 Mock
                mock_ssw.expand_scene.return_value = {
                    "scene_number": 1,
                    "narration_script": [{"line": "Test narration", "at_ms": 0}],
                    "visuals": [{"frame_id": "1A", "image_prompt": "Test prompt"}],
                    "timing": {"total_ms": 3000}
                }
                
                mock_ica.generate_images.return_value = [
                    {"frame_id": "1A", "image_uri": "mock.png"}
                ]
                
                mock_vga.generate_voice.return_value = {
                    "voice_file": "mock.mp3", "duration_ms": 3000
                }
                
                mock_vma.create_video.return_value = {
                    "video_path": "mock.mp4", "duration_ms": 3000
                }
                
                # 실제 FSW만 호출 (텍스트 생성, 저비용)
                result = await runner.create_video(
                    topic=topic,
                    length_preference="30-45s",  # 최단 길이
                    cost_saving_mode=True
                )
                
                # 결과 검증
                assert 'session_id' in result
                assert 'full_script' in result
                assert result['full_script']['title']
                
                # FSW가 실제로 호출되었는지 확인
                assert len(result['full_script']['scenes']) >= 1
                
        except Exception as e:
            pytest.fail(f"최소 비용 통합 테스트 실패: {e}")

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_single_scene_real_api_minimal(self):
        """1개 씬으로 실제 API 테스트 (~$0.05)"""
        
        # Skip if no API key
        if not self.api_key:
            pytest.skip("API 키 없음")
        
        topic = "Test"  # 최소 토픽
        
        try:
            runner = NewArchitectureRunner()
            
            # 이미지와 음성은 Mock, 텍스트만 실제 API
            with patch.object(runner.orchestrator, 'image_create_agent') as mock_ica, \
                 patch.object(runner.orchestrator, 'voice_generate_agent') as mock_vga, \
                 patch.object(runner.orchestrator, 'video_maker_agent') as mock_vma:
                
                mock_ica.generate_images.return_value = [
                    {"frame_id": "1A", "image_uri": "mock.png"}
                ]
                
                mock_vga.generate_voice.return_value = {
                    "voice_file": "mock.mp3", "duration_ms": 5000
                }
                
                mock_vma.create_video.return_value = {
                    "video_path": "mock.mp4", "duration_ms": 5000
                }
                
                # FSW + SSW는 실제 API 사용 (저비용)
                result = await runner.create_video(
                    topic=topic,
                    length_preference="30-45s",
                    cost_saving_mode=True  # 이미지는 여전히 Mock
                )
                
                # 실제 AI 응답 검증
                assert 'session_id' in result
                assert 'full_script' in result
                assert 'scene_packages' in result
                
                # 실제 생성된 내용 확인
                full_script = result['full_script']
                assert full_script['title']
                assert len(full_script['scenes']) >= 1
                
                scene_packages = result['scene_packages']
                assert len(scene_packages) >= 1
                
                first_scene = scene_packages[0]
                assert first_scene['scene_number'] == 1
                assert 'narration_script' in first_scene
                assert len(first_scene['narration_script']) >= 1
                
        except Exception as e:
            pytest.fail(f"실제 API 통합 테스트 실패: {e}")

    @pytest.mark.integration
    def test_cost_tracking(self):
        """비용 추적 시스템 테스트"""
        
        class CostTracker:
            def __init__(self):
                self.api_calls = 0
                self.estimated_cost = 0.0
            
            def track_api_call(self, tokens: int = 1000):
                self.api_calls += 1
                # Gemini Flash 대략적 비용: $0.075 per 1M tokens
                self.estimated_cost += tokens * 0.000000075
        
        tracker = CostTracker()
        
        # 테스트 시나리오 비용 계산
        tracker.track_api_call(2000)  # FSW 호출
        tracker.track_api_call(3000)  # SSW 호출
        
        # 비용이 제한 내에 있는지 확인
        assert tracker.estimated_cost < 0.01, f"테스트 비용이 너무 높음: ${tracker.estimated_cost:.6f}"
        assert tracker.api_calls == 2

    @pytest.mark.integration
    def test_environment_validation(self):
        """통합 테스트 환경 검증"""
        
        # API 키 존재 확인
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        assert api_key, "GEMINI_API_KEY 또는 GOOGLE_API_KEY가 필요합니다"
        
        # API 키 형식 기본 검증
        assert len(api_key) > 20, "API 키가 너무 짧습니다"
        assert api_key.startswith('AI'), "Gemini API 키는 'AI'로 시작해야 합니다"
        
        # 필수 디렉토리 존재 확인
        required_dirs = ['src', 'src/agents', 'src/core', 'schemas']
        for dir_name in required_dirs:
            assert Path(dir_name).exists(), f"필수 디렉토리 누락: {dir_name}"

    @pytest.mark.integration
    def test_schema_files_exist(self):
        """스키마 파일들 존재 확인"""
        
        schema_files = [
            'schemas/FullScript.json',
            'schemas/ScenePackage.json', 
            'schemas/ImageAsset.json'
        ]
        
        for schema_file in schema_files:
            assert Path(schema_file).exists(), f"스키마 파일 누락: {schema_file}"
            
            # JSON 파일이 유효한지 확인
            import json
            with open(schema_file, 'r') as f:
                schema_data = json.load(f)
            assert isinstance(schema_data, dict)
            assert 'type' in schema_data or 'properties' in schema_data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
