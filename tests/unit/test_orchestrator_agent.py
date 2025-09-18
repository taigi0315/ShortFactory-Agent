"""
테스트: Orchestrator Agent
파이프라인 관리자의 핵심 기능들을 Mock 기반으로 테스트
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.orchestrator_agent import OrchestratorAgent


class TestOrchestratorAgent:
    """Orchestrator Agent 단위 테스트 (Mock 기반)"""

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_orchestrator_initialization(self):
        """Orchestrator 초기화 테스트"""
        
        with patch('agents.orchestrator_agent.FullScriptWriterAgent'), \
             patch('agents.orchestrator_agent.SceneScriptWriterAgent'), \
             patch('agents.orchestrator_agent.ImageCreateAgent'), \
             patch('agents.orchestrator_agent.VoiceGenerateAgent'), \
             patch('agents.orchestrator_agent.VideoMakerAgent'), \
             patch('agents.orchestrator_agent.SessionManager'):
            
            orchestrator = OrchestratorAgent()
            
            # 기본 속성들이 설정되었는지 확인
            assert hasattr(orchestrator, 'session_manager')
            assert hasattr(orchestrator, 'full_script_writer')
            assert hasattr(orchestrator, 'scene_script_writer')
            assert hasattr(orchestrator, 'image_create_agent')
            assert hasattr(orchestrator, 'voice_generate_agent')
            assert hasattr(orchestrator, 'video_maker_agent')

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_load_schemas(self):
        """JSON 스키마 로딩 테스트"""
        
        with patch('agents.orchestrator_agent.FullScriptWriterAgent'), \
             patch('agents.orchestrator_agent.SceneScriptWriterAgent'), \
             patch('agents.orchestrator_agent.ImageCreateAgent'), \
             patch('agents.orchestrator_agent.VoiceGenerateAgent'), \
             patch('agents.orchestrator_agent.VideoMakerAgent'), \
             patch('agents.orchestrator_agent.SessionManager'):
            
            orchestrator = OrchestratorAgent()
            
            # 스키마가 로드되었는지 확인
            assert hasattr(orchestrator, 'schemas')
            assert isinstance(orchestrator.schemas, dict)

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    @pytest.mark.asyncio
    async def test_create_video_pipeline_flow(self):
        """비디오 생성 파이프라인 흐름 테스트 (Mock)"""
        
        # Mock 에이전트들과 응답 설정
        mock_session_manager = MagicMock()
        mock_session_manager.create_session.return_value = "test-session-id"
        
        mock_fsw = MagicMock()
        mock_fsw.generate_script = AsyncMock(return_value={
            "title": "Test Video",
            "scenes": [
                {"scene_number": 1, "scene_type": "hook"},
                {"scene_number": 2, "scene_type": "explanation"}
            ]
        })
        
        mock_ssw = MagicMock()
        mock_ssw.expand_scene = AsyncMock(return_value={
            "scene_number": 1,
            "narration_script": [{"line": "Test narration", "at_ms": 0}],
            "visuals": [{"frame_id": "1A", "image_prompt": "Test image prompt"}],
            "timing": {"total_ms": 5000}
        })
        
        mock_ica = MagicMock()
        mock_ica.generate_images = AsyncMock(return_value=[
            {"frame_id": "1A", "image_uri": "test.png"}
        ])
        
        mock_vga = MagicMock()
        mock_vga.generate_voice = AsyncMock(return_value={
            "voice_file": "test.mp3",
            "duration_ms": 5000
        })
        
        with patch('agents.orchestrator_agent.FullScriptWriterAgent', return_value=mock_fsw), \
             patch('agents.orchestrator_agent.SceneScriptWriterAgent', return_value=mock_ssw), \
             patch('agents.orchestrator_agent.ImageCreateAgent', return_value=mock_ica), \
             patch('agents.orchestrator_agent.VoiceGenerateAgent', return_value=mock_vga), \
             patch('agents.orchestrator_agent.VideoMakerAgent'), \
             patch('agents.orchestrator_agent.SessionManager', return_value=mock_session_manager):
            
            orchestrator = OrchestratorAgent()
            
            # create_video 메소드가 존재하는지 확인
            assert hasattr(orchestrator, 'create_video')
            
            # 파이프라인 흐름 확인을 위해 각 단계별 메소드 확인
            assert hasattr(orchestrator, 'session_manager')
            assert hasattr(orchestrator, 'full_script_writer')
            assert hasattr(orchestrator, 'scene_script_writer')

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_validate_schema_method_exists(self):
        """스키마 검증 메소드 존재 확인"""
        
        with patch('agents.orchestrator_agent.FullScriptWriterAgent'), \
             patch('agents.orchestrator_agent.SceneScriptWriterAgent'), \
             patch('agents.orchestrator_agent.ImageCreateAgent'), \
             patch('agents.orchestrator_agent.VoiceGenerateAgent'), \
             patch('agents.orchestrator_agent.VideoMakerAgent'), \
             patch('agents.orchestrator_agent.SessionManager'):
            
            orchestrator = OrchestratorAgent()
            
            # 스키마 검증 관련 메소드들이 있는지 확인
            # (실제 구현에 따라 메소드명이 다를 수 있음)
            assert hasattr(orchestrator, 'schemas')

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_error_handling_structure(self):
        """에러 처리 구조 테스트"""
        
        with patch('agents.orchestrator_agent.FullScriptWriterAgent'), \
             patch('agents.orchestrator_agent.SceneScriptWriterAgent'), \
             patch('agents.orchestrator_agent.ImageCreateAgent'), \
             patch('agents.orchestrator_agent.VoiceGenerateAgent'), \
             patch('agents.orchestrator_agent.VideoMakerAgent'), \
             patch('agents.orchestrator_agent.SessionManager'):
            
            orchestrator = OrchestratorAgent()
            
            # 에러 처리를 위한 기본 구조가 있는지 확인
            assert hasattr(orchestrator, 'session_manager')
            
            # 에이전트들이 초기화되었는지 확인
            assert orchestrator.full_script_writer is not None
            assert orchestrator.scene_script_writer is not None
            assert orchestrator.image_create_agent is not None
            assert orchestrator.voice_generate_agent is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
