"""
pytest 설정 파일
테스트 마커, 픽스처, 설정 등을 정의
"""

import pytest
import time
import os
from datetime import datetime


def pytest_configure(config):
    """pytest 설정"""
    # 커스텀 마커 등록
    config.addinivalue_line(
        "markers", "integration: 실제 API를 사용하는 통합 테스트"
    )
    config.addinivalue_line(
        "markers", "minimal: 최소 비용 통합 테스트 ($0.05 이하)"
    )
    config.addinivalue_line(
        "markers", "slow: 느린 테스트 (30초 이상)"
    )
    config.addinivalue_line(
        "markers", "performance: 성능 벤치마크 테스트"
    )


@pytest.fixture(autouse=True)
def test_performance_monitor(request):
    """모든 테스트의 성능 자동 모니터링"""
    start_time = time.time()
    yield
    duration = time.time() - start_time
    
    # 느린 테스트 경고
    if duration > 5.0:
        print(f"\n⚠️ 느린 테스트: {request.node.name} took {duration:.2f}s")


@pytest.fixture
def api_key():
    """API 키 픽스처"""
    key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not key:
        pytest.skip("API 키가 없어서 테스트 스킵")
    return key


@pytest.fixture
def test_config():
    """테스트 설정 픽스처"""
    return {
        "unit": {
            "use_mocks": True,
            "api_calls": False,
            "cost": 0.0
        },
        "integration_minimal": {
            "use_mocks": False,
            "max_api_calls": 3,
            "max_cost": 0.05,
            "max_scenes": 1,
            "skip_voice": True,
            "skip_images": True  # 텍스트 생성만
        },
        "integration_full": {
            "use_mocks": False,
            "max_api_calls": 10,
            "max_cost": 0.50,
            "max_scenes": 2,
            "frames_per_scene": 1,
            "cost_saving_mode": True
        }
    }


@pytest.fixture
def minimal_script_data():
    """최소 스크립트 데이터 픽스처"""
    return {
        "title": "Test Video",
        "logline": "A simple test video",
        "overall_style": "educational",
        "story_summary": "This is a test video for integration testing purposes.",
        "scenes": [
            {
                "scene_number": 1,
                "scene_type": "explanation",
                "beats": ["Introduce the topic"],
                "learning_objectives": ["Understand basics"],
                "needs_animation": False,
                "transition_to_next": "fade",
                "scene_importance": 3
            }
        ]
    }


@pytest.fixture
def minimal_scene_data():
    """최소 씬 데이터 픽스처"""
    return {
        "scene_number": 1,
        "narration_script": [
            {
                "line": "This is a test narration for minimal cost testing.",
                "at_ms": 0,
                "pause_ms": 500
            }
        ],
        "visuals": [
            {
                "frame_id": "1A",
                "shot_type": "medium",
                "image_prompt": "A simple educational scene with friendly character explaining a basic concept",
                "aspect_ratio": "16:9"
            }
        ],
        "tts": {
            "engine": "lemonfox",
            "voice": "sarah",
            "language": "en-US"
        },
        "timing": {
            "total_ms": 5000
        }
    }


class CostTracker:
    """테스트 비용 추적"""
    
    def __init__(self):
        self.api_calls = 0
        self.estimated_cost = 0.0
        self.start_time = datetime.now()
    
    def track_api_call(self, tokens: int = 1000, model: str = "gemini-flash"):
        """API 호출 비용 추적"""
        self.api_calls += 1
        
        # 모델별 비용 (대략적)
        costs = {
            "gemini-flash": 0.000000075,  # $0.075 per 1M tokens
            "lemonfox": 0.0000025,        # $2.50 per 1M characters
        }
        
        cost_per_token = costs.get(model, 0.000000075)
        self.estimated_cost += tokens * cost_per_token
    
    def get_summary(self):
        """비용 요약 반환"""
        duration = (datetime.now() - self.start_time).total_seconds()
        return {
            "api_calls": self.api_calls,
            "estimated_cost": self.estimated_cost,
            "duration_seconds": duration,
            "cost_per_second": self.estimated_cost / duration if duration > 0 else 0
        }


@pytest.fixture
def cost_tracker():
    """비용 추적 픽스처"""
    return CostTracker()


def pytest_runtest_teardown(item, nextitem):
    """테스트 후 정리"""
    # 통합 테스트 후 비용 체크
    if "integration" in item.keywords:
        # 비용 추적 로직 (실제 구현 시 추가)
        pass
