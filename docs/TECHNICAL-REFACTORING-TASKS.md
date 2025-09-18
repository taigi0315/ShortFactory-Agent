# 기술 리팩토링 및 개선 태스크 목록

*작성일: 2025년 9월 18일*  
*작성자: 시니어 기술 리드 엔지니어*

## 🎯 프로젝트 현황 요약

**ShortFactory Agent**는 다중 에이전트 기반 비디오 생성 시스템으로, 2025년 9월에 대대적인 아키텍처 개편을 완료했습니다. 현재 상태:

- ✅ **새로운 다중 에이전트 아키텍처** 완성 (FSW, SSW, ICA, VGA, Orchestrator)
- ✅ **JSON 스키마 검증 시스템** 구현 및 안정화 (95% 성공률)
- ✅ **프로덕션 레디** 출력 품질 달성
- ⚠️ **레거시 코드 및 문서** 정리 필요
- ⚠️ **보안 및 안정성** 개선 필요

---

## 🧹 Priority 1: 코드베이스 정리 및 최적화

### T001: 레거시 코드 제거
**현재 상황**: 레거시 ADK 기반 코드와 중복된 파일들이 혼재  
**목표**: 깔끔하고 유지보수 가능한 코드베이스 구축  
**예상 결과**: 코드베이스 크기 30% 감소, 개발자 혼란 방지

#### 제거 대상:
- `legacy/` 폴더 전체 (legacy_main_adk.py, legacy_run_adk.py)
- `src/agents/legacy/` 폴더 전체 (5개 레거시 에이전트)
- `docs/legacy/` 폴더 내 구식 문서들
- 사용되지 않는 테스트 파일들 (`tests/legacy/`)

#### 작업 순서:
1. 현재 사용 중인 코드에서 레거시 import 확인 및 제거
2. Git 히스토리 보존을 위해 `git rm` 사용하여 파일 삭제
3. README.md에서 레거시 관련 내용 제거
4. CI/CD 스크립트에서 레거시 경로 참조 제거

---

### T002: 불필요한 문서 정리
**현재 상황**: docs/legacy/ 폴더에 구식 문서 10개 존재  
**목표**: 최신 상태만 유지하는 깔끔한 문서 구조  
**예상 결과**: 문서 혼란 방지, 새 팀원 온보딩 개선

#### 제거 대상:
- `docs/legacy/ADK-ARCHITECTURE.md` (구식 아키텍처)
- `docs/legacy/ADK-MIGRATION-PLAN.md` (완료된 마이그레이션)
- `docs/legacy/DEVELOPMENT-PLAN.md` (구식 개발 계획)
- `docs/legacy/COMPREHENSIVE-GUIDE.md` (중복 내용)
- `docs/legacy/architecture-diagram.md` (구식 다이어그램)

#### 유지할 문서:
- `docs/ARCHITECTURE.md` (최신 아키텍처)
- `docs/AGENTS-AND-VALIDATORS.md` (에이전트 가이드)
- `docs/PROJECT-STATUS-2025.md` (프로젝트 현황)
- `docs/JSON-PARSING-SYSTEM.md` (중요한 시스템 가이드)

---

## 🚨 Priority 2: 핵심 안정성 문제 해결 (CRITICAL)

### T003: LLM 응답 구조화 시스템 완전 개편 ⚠️ **URGENT**
**현재 상황**: LLM이 복잡한 JSON 스키마를 제대로 따르지 않아 파이프라인 실패 빈발  
**근본 문제**: LLM에게 완벽한 JSON 스키마 준수를 기대하는 것은 비현실적  
**목표**: Pydantic 기반 강력한 데이터 검증 및 자동 수정 시스템 구축  
**예상 결과**: 파이프라인 안정성 60% → 98% 향상, LLM 응답 변동성 완전 흡수

#### 현재 문제점 분석:
```python
# 현재 방식의 문제점
{
  "scenes": [
    {
      "scene_number": 1,
      "narration_script": [...],
      "visuals": [...],
      "sfx_cues": [...],    # LLM이 "sound_effects"로 잘못 생성
      "on_screen_text": [...], # LLM이 누락하거나 다른 이름으로 생성
      "timing": {
        "total_ms": 45000,
        "at_ms": 0          # LLM이 "start_ms"로 잘못 생성
      }
    }
  ]
}
```

#### A. Pydantic 모델 기반 강력한 검증 시스템
```python
# src/core/response_models.py
from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Union, Any
from enum import Enum

class TransitionType(str, Enum):
    FADE = "fade"
    CUT = "cut"
    DISSOLVE = "dissolve"
    SLIDE = "slide"

class SFXCue(BaseModel):
    """SFX 큐 - 다양한 LLM 응답 형식을 자동 정규화"""
    cue: str = Field(..., description="Sound effect cue name")
    at_ms: int = Field(..., description="Start time in milliseconds")
    duration_ms: int = Field(..., description="Duration in milliseconds")
    volume: float = Field(default=0.5, ge=0.0, le=1.0)
    
    @root_validator(pre=True)
    def normalize_fields(cls, values):
        """LLM이 다른 필드명을 사용해도 자동 매핑"""
        # 필드명 정규화
        field_mappings = {
            'sfx_name': 'cue',
            'sound_effect': 'cue', 
            'effect': 'cue',
            'start_ms': 'at_ms',
            'begin_ms': 'at_ms',
            'length_ms': 'duration_ms',
            'duration': 'duration_ms'
        }
        
        for old_key, new_key in field_mappings.items():
            if old_key in values and new_key not in values:
                values[new_key] = values[old_key]
                del values[old_key]
        
        # 필수 필드 기본값 설정
        if 'duration_ms' not in values and 'end_ms' in values:
            values['duration_ms'] = values['end_ms'] - values.get('at_ms', 0)
        
        return values
    
    @validator('cue')
    def validate_cue(cls, v):
        """SFX 큐명 정규화"""
        if not v:
            return "SFX_GENERIC"
        return v.upper().replace(' ', '_')

class NarrationLine(BaseModel):
    """나레이션 라인 - LLM 응답 유연성 확보"""
    line: str = Field(..., min_length=1)
    at_ms: int = Field(..., ge=0)
    duration_ms: int = Field(..., gt=0)
    pause_after_ms: int = Field(default=500, ge=0)
    emphasis: Optional[str] = Field(default=None)
    
    @root_validator(pre=True)
    def normalize_timing(cls, values):
        """타이밍 필드 자동 계산 및 정규화"""
        if isinstance(values, str):
            # LLM이 단순 문자열로 응답한 경우
            return {
                'line': values,
                'at_ms': 0,
                'duration_ms': len(values) * 100,  # 대략적 계산
                'pause_after_ms': 500
            }
        
        # 타이밍 자동 계산
        if 'duration_ms' not in values and 'line' in values:
            # 텍스트 길이 기반 duration 추정
            text_length = len(values['line'])
            values['duration_ms'] = max(text_length * 80, 1000)  # 최소 1초
        
        return values

class ScenePackage(BaseModel):
    """씬 패키지 - 완전한 LLM 응답 정규화"""
    scene_number: int = Field(..., ge=1)
    narration_script: List[NarrationLine] = Field(default_factory=list)
    visuals: List[dict] = Field(default_factory=list)  # 별도 모델로 정의 예정
    sfx_cues: List[SFXCue] = Field(default_factory=list)
    on_screen_text: List[dict] = Field(default_factory=list)
    timing: dict = Field(default_factory=dict)
    
    @root_validator(pre=True)
    def handle_llm_variations(cls, values):
        """LLM 응답의 다양한 변형 처리"""
        if not isinstance(values, dict):
            raise ValueError("Scene package must be a dictionary")
        
        # 필드명 정규화
        field_mappings = {
            'scene_id': 'scene_number',
            'number': 'scene_number',
            'narration': 'narration_script',
            'script': 'narration_script',
            'sound_effects': 'sfx_cues',
            'sfx': 'sfx_cues',
            'sounds': 'sfx_cues',
            'text_overlays': 'on_screen_text',
            'overlays': 'on_screen_text'
        }
        
        for old_key, new_key in field_mappings.items():
            if old_key in values and new_key not in values:
                values[new_key] = values[old_key]
        
        # 빈 리스트 기본값 설정
        for field in ['narration_script', 'visuals', 'sfx_cues', 'on_screen_text']:
            if field not in values or values[field] is None:
                values[field] = []
        
        return values
    
    @validator('narration_script', pre=True)
    def normalize_narration(cls, v):
        """나레이션 스크립트 정규화"""
        if not v:
            return []
        
        if isinstance(v, str):
            # LLM이 단순 문자열로 응답한 경우
            return [{'line': v, 'at_ms': 0, 'duration_ms': len(v) * 80}]
        
        if isinstance(v, list):
            normalized = []
            current_time = 0
            
            for item in v:
                if isinstance(item, str):
                    # 문자열 항목을 객체로 변환
                    duration = len(item) * 80
                    normalized.append({
                        'line': item,
                        'at_ms': current_time,
                        'duration_ms': duration
                    })
                    current_time += duration + 500
                elif isinstance(item, dict):
                    normalized.append(item)
            
            return normalized
        
        return v
```

#### B. 강력한 LLM 응답 처리 파이프라인
```python
# src/core/llm_response_processor.py
from typing import Dict, Any, Optional, Type, TypeVar
import json
import logging
from pydantic import BaseModel, ValidationError

T = TypeVar('T', bound=BaseModel)

class LLMResponseProcessor:
    """LLM 응답을 안정적으로 처리하는 프로세서"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_response(self, 
                        raw_response: str, 
                        target_model: Type[T],
                        fallback_data: Optional[Dict[str, Any]] = None) -> T:
        """
        LLM 응답을 목표 모델로 안전하게 변환
        
        Args:
            raw_response: LLM의 원시 응답
            target_model: 목표 Pydantic 모델
            fallback_data: 실패 시 사용할 기본 데이터
            
        Returns:
            검증된 모델 인스턴스
        """
        
        # 1단계: JSON 추출 및 파싱
        try:
            parsed_data = self._extract_and_parse_json(raw_response)
        except Exception as e:
            self.logger.warning(f"JSON 파싱 실패: {e}")
            if fallback_data:
                parsed_data = fallback_data
            else:
                raise ValueError(f"JSON 파싱 실패 및 fallback 데이터 없음: {e}")
        
        # 2단계: Pydantic 모델 검증 및 자동 수정
        try:
            return target_model(**parsed_data)
        except ValidationError as e:
            self.logger.warning(f"초기 검증 실패: {e}")
            
            # 3단계: 자동 수정 시도
            corrected_data = self._auto_correct_data(parsed_data, target_model, e)
            
            try:
                return target_model(**corrected_data)
            except ValidationError as final_error:
                self.logger.error(f"자동 수정 후에도 검증 실패: {final_error}")
                
                # 4단계: 최후 수단 - 최소 유효 데이터 생성
                return self._create_minimal_valid_instance(target_model, parsed_data)
    
    def _auto_correct_data(self, 
                          data: Dict[str, Any], 
                          model: Type[T], 
                          validation_error: ValidationError) -> Dict[str, Any]:
        """검증 오류를 기반으로 데이터 자동 수정"""
        corrected = data.copy()
        
        for error in validation_error.errors():
            field_path = error['loc']
            error_type = error['type']
            
            if error_type == 'missing':
                # 필수 필드 누락 - 기본값 추가
                self._add_missing_field(corrected, field_path, model)
            elif error_type == 'type_error':
                # 타입 오류 - 타입 변환 시도
                self._fix_type_error(corrected, field_path, error)
            elif error_type == 'value_error':
                # 값 오류 - 유효한 값으로 교체
                self._fix_value_error(corrected, field_path, error)
        
        return corrected
    
    def _create_minimal_valid_instance(self, 
                                     model: Type[T], 
                                     original_data: Dict[str, Any]) -> T:
        """최소한의 유효한 인스턴스 생성"""
        self.logger.warning(f"최소 유효 {model.__name__} 인스턴스 생성")
        
        # 모델의 필수 필드만으로 최소 인스턴스 생성
        minimal_data = {}
        
        for field_name, field_info in model.__fields__.items():
            if field_info.required:
                if field_name in original_data:
                    minimal_data[field_name] = original_data[field_name]
                else:
                    # 타입 기반 기본값 생성
                    minimal_data[field_name] = self._generate_default_value(field_info.type_)
        
        return model(**minimal_data)
```

#### C. 에이전트별 응답 처리 통합
```python
# src/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import TypeVar, Type, Dict, Any
from src.core.llm_response_processor import LLMResponseProcessor

T = TypeVar('T', bound=BaseModel)

class BaseAgent(ABC):
    """모든 에이전트의 기본 클래스"""
    
    def __init__(self):
        self.response_processor = LLMResponseProcessor()
    
    def safe_llm_call(self, 
                      prompt: str, 
                      response_model: Type[T],
                      fallback_data: Dict[str, Any] = None) -> T:
        """안전한 LLM 호출 및 응답 처리"""
        
        # LLM 호출
        raw_response = self._call_llm(prompt)
        
        # 안전한 응답 처리
        return self.response_processor.process_response(
            raw_response=raw_response,
            target_model=response_model,
            fallback_data=fallback_data
        )
    
    @abstractmethod
    def _call_llm(self, prompt: str) -> str:
        """실제 LLM 호출 (각 에이전트에서 구현)"""
        pass
```

#### D. 실제 적용 예시
```python
# src/agents/scene_script_writer_agent.py (개선된 버전)
from src.core.response_models import ScenePackage
from src.agents.base_agent import BaseAgent

class SceneScriptWriterAgent(BaseAgent):
    
    async def generate_scene_package(self, scene_data: dict) -> ScenePackage:
        """씬 패키지 생성 - 안정적인 응답 처리"""
        
        prompt = self._build_scene_prompt(scene_data)
        
        # 실패 시 사용할 기본 데이터
        fallback_data = {
            'scene_number': scene_data.get('scene_number', 1),
            'narration_script': [
                {
                    'line': f"This is scene {scene_data.get('scene_number', 1)}.",
                    'at_ms': 0,
                    'duration_ms': 3000
                }
            ],
            'visuals': [],
            'sfx_cues': [],
            'on_screen_text': [],
            'timing': {'total_ms': 3000}
        }
        
        # 안전한 LLM 호출 및 응답 처리
        scene_package = self.safe_llm_call(
            prompt=prompt,
            response_model=ScenePackage,
            fallback_data=fallback_data
        )
        
        return scene_package
```

### T004: API 키 보안 강화
**현재 상황**: API 키가 환경변수로만 관리되고 있음  
**목표**: 더 안전한 API 키 관리 시스템 구축  
**예상 결과**: 보안 취약점 제거, 프로덕션 환경 안전성 확보

#### 개선사항:
1. **API 키 검증 로직 추가**
   ```python
   def validate_api_key(key: str) -> bool:
       """API 키 형식 및 유효성 검증"""
       if not key or len(key) < 32:
           return False
       # 키 형식 검증 로직 추가
       return True
   ```

2. **키 로테이션 지원**
   - 만료된 키 감지 및 경고
   - 새 키로 자동 전환 메커니즘

3. **민감 정보 로깅 방지**
   - API 키 일부만 로그에 기록 (예: `key[:10]...`)
   - 응답 데이터에서 민감 정보 필터링

---

### T004: 에러 처리 및 복구 시스템 개선
**현재 상황**: 359개의 try/except 블록이 있지만 일관성 부족  
**목표**: 체계적인 에러 처리 및 복구 시스템 구축  
**예상 결과**: 시스템 안정성 95% → 99% 향상

#### 개선사항:
1. **표준화된 에러 클래스 생성**
   ```python
   class ShortFactoryError(Exception):
       """기본 에러 클래스"""
   
   class APIError(ShortFactoryError):
       """API 관련 에러"""
   
   class ValidationError(ShortFactoryError):
       """검증 관련 에러"""
   ```

2. **Circuit Breaker 패턴 구현**
   - API 호출 실패 시 자동 차단
   - 점진적 복구 메커니즘

3. **Graceful Degradation 강화**
   - 부분적 실패 시에도 가능한 결과 반환
   - 대체 서비스 자동 활용

---

### T005: 의존성 관리 및 보안 업데이트
**현재 상황**: requirements.txt 파일이 없어 의존성 관리 부재  
**목표**: 체계적인 의존성 관리 및 보안 업데이트  
**예상 결과**: 보안 취약점 제거, 재현 가능한 환경 구축

#### 작업 내용:
1. **requirements.txt 생성**
   ```
   google-generativeai>=0.7.0,<0.8.0
   pydantic>=2.0.0,<3.0.0
   jsonschema>=4.0.0,<5.0.0
   python-dotenv>=1.0.0,<2.0.0
   requests>=2.31.0,<3.0.0
   ```

2. **개발 의존성 분리**
   - `requirements-dev.txt` 생성
   - 테스트, 린팅, 포맷팅 도구 포함

3. **보안 스캔 자동화**
   - `pip-audit` 또는 `safety` 도구 도입
   - CI/CD에서 자동 보안 검사

---

## ⚡ Priority 3: 성능 및 확장성 개선

### T006: 병렬 처리 시스템 구현
**현재 상황**: 순차적 처리로 인한 긴 생성 시간 (5-6분)  
**목표**: 병렬 처리를 통한 성능 향상  
**예상 결과**: 생성 시간 50% 단축 (5분 → 2.5분)

#### 개선사항:
1. **씬 별 병렬 처리**
   ```python
   import asyncio
   import concurrent.futures
   
   async def process_scenes_parallel(scenes):
       tasks = [process_scene(scene) for scene in scenes]
       return await asyncio.gather(*tasks)
   ```

2. **이미지 생성 병렬화**
   - 프레임별 동시 생성
   - 배치 처리 최적화

3. **캐싱 시스템 도입**
   - 유사한 프롬프트 결과 캐시
   - 세션 간 재사용 가능한 에셋 캐시

---

### T007: 메모리 사용량 최적화
**현재 상황**: 대용량 세션 데이터로 인한 메모리 부족 가능성  
**목표**: 효율적인 메모리 관리 시스템 구축  
**예상 결과**: 메모리 사용량 40% 감소, 대용량 프로젝트 지원

#### 개선사항:
1. **스트리밍 처리**
   - 큰 파일을 청크 단위로 처리
   - 메모리에 모든 데이터를 로드하지 않음

2. **가비지 컬렉션 최적화**
   - 사용하지 않는 객체 명시적 해제
   - 메모리 프로파일링 도구 도입

3. **데이터 압축**
   - JSON 데이터 압축 저장
   - 이미지 최적화 및 압축

---

## 🧪 Priority 4: 테스트 및 품질 보증

### T008: 견고한 테스트 시스템 구축
**현재 상황**: 테스트 파일은 있지만 체계적이지 않고 비용 고려 부족  
**목표**: 90% 이상 단위 테스트 커버리지 + 비용 효율적인 통합 테스트  
**예상 결과**: 버그 발생률 70% 감소, 안전한 리팩토링, 개발 비용 절약

#### A. 단위 테스트 시스템 (API 호출 없음)
1. **pytest 및 coverage 도구 도입**
   ```bash
   pip install pytest pytest-cov pytest-asyncio pytest-mock
   pytest --cov=src --cov-report=html --cov-fail-under=90
   ```

2. **핵심 메소드별 단위 테스트 작성**
   ```python
   # tests/unit/test_json_parser.py
   def test_parse_json_with_trailing_comma():
       malformed = '{"key": "value",}'
       result = robust_json_parse(malformed)
       assert result == {"key": "value"}
   
   # tests/unit/test_orchestrator.py  
   @pytest.mark.asyncio
   async def test_orchestrator_create_session():
       orchestrator = OrchestratorAgent()
       session_id = await orchestrator.create_session("test topic")
       assert session_id.startswith("20")
   
   # tests/unit/test_agents.py
   def test_full_script_writer_prompt_generation():
       agent = FullScriptWriterAgent()
       prompt = agent._generate_prompt("AI technology", "60-90s")
       assert "AI technology" in prompt
       assert "60-90s" in prompt
   ```

3. **Mock 기반 에이전트 테스트**
   ```python
   # API 호출을 Mock으로 대체
   @patch('agents.full_script_writer_agent.genai.Client')
   def test_full_script_writer_generate(mock_client):
       mock_response = {"title": "Test", "scenes": []}
       mock_client.return_value.generate.return_value = mock_response
       
       agent = FullScriptWriterAgent()
       result = await agent.generate_script("test topic")
       assert result["title"] == "Test"
   ```

#### B. 비용 효율적인 통합 테스트 (실제 API 호출)
1. **최소 비용 테스트 설정**
   ```python
   # tests/integration/conftest.py
   INTEGRATION_TEST_CONFIG = {
       "max_scenes": 2,           # 최대 2개 씬만
       "frames_per_scene": 1,     # 씬당 1개 프레임만
       "cost_saving_mode": True,  # Mock 이미지 사용
       "voice_generation": False, # 음성 생성 스킵
       "short_prompts": True,     # 짧은 프롬프트 사용
   }
   ```

2. **실제 API 통합 테스트 (저비용)**
   ```python
   # tests/integration/test_end_to_end_minimal.py
   @pytest.mark.integration
   @pytest.mark.asyncio
   async def test_minimal_video_generation():
       """최소 비용으로 전체 파이프라인 테스트"""
       runner = NewArchitectureRunner()
       
       result = await runner.create_video(
           topic="Test topic for integration",
           length_preference="30-45s",  # 최단 길이
           cost_saving_mode=True,       # Mock 이미지
           max_scenes=2,                # 최소 씬 수
           skip_voice=True              # 음성 생성 스킵
       )
       
       # 핵심 구조만 검증
       assert result["session_id"]
       assert len(result["scene_packages"]) == 2
       assert result["build_report"]["success"] is True
   
   @pytest.mark.integration  
   @pytest.mark.slow
   async def test_single_scene_with_real_api():
       """1개 씬으로 실제 API 테스트"""
       agent = SceneScriptWriterAgent()
       
       scene_data = {
           "scene_number": 1,
           "scene_type": "introduction",
           "learning_objective": "Test learning",
           "importance_level": 3
       }
       
       result = await agent.generate_scene_package(scene_data)
       
       # 실제 AI 응답 검증
       assert result["scene_number"] == 1
       assert "narration_script" in result
       assert len(result["visuals"]) >= 1
   ```

3. **비용 모니터링 테스트**
   ```python
   # tests/integration/test_cost_monitoring.py
   class CostTracker:
       def __init__(self):
           self.api_calls = 0
           self.estimated_cost = 0.0
       
       def track_api_call(self, tokens: int):
           self.api_calls += 1
           self.estimated_cost += tokens * 0.00001  # 대략적 비용
   
   @pytest.mark.integration
   def test_integration_cost_limit():
       """통합 테스트 비용이 $0.10 이하인지 확인"""
       tracker = CostTracker()
       
       # 테스트 실행...
       
       assert tracker.estimated_cost < 0.10, f"테스트 비용이 너무 높음: ${tracker.estimated_cost}"
   ```

#### C. 테스트 환경 분리
1. **테스트 설정 파일**
   ```python
   # tests/test_config.py
   TEST_SETTINGS = {
       "unit": {
           "use_mocks": True,
           "api_calls": False,
           "cost": 0.0
       },
       "integration_minimal": {
           "use_mocks": False,
           "max_api_calls": 5,
           "max_cost": 0.05,
           "max_scenes": 1,
           "skip_voice": True,
           "skip_images": True  # 텍스트 생성만
       },
       "integration_full": {
           "use_mocks": False,
           "max_api_calls": 20,
           "max_cost": 0.50,
           "max_scenes": 2,
           "frames_per_scene": 1,
           "cost_saving_mode": True
       }
   }
   ```

2. **테스트 실행 스크립트**
   ```bash
   # scripts/run_tests.sh
   
   # 단위 테스트 (무료)
   pytest tests/unit/ -v
   
   # 최소 통합 테스트 (< $0.05)
   pytest tests/integration/ -m "minimal" -v
   
   # 전체 통합 테스트 (< $0.50)  
   pytest tests/integration/ -m "not minimal" -v --maxfail=3
   
   # 야간 전체 테스트 (비용 제한 없음)
   pytest tests/ -v --integration-full
   ```

#### D. 테스트 데이터 관리
1. **재사용 가능한 테스트 픽스처**
   ```python
   # tests/fixtures.py
   @pytest.fixture
   def minimal_script():
       return {
           "title": "Test Video",
           "scenes": [
               {
                   "scene_number": 1,
                   "scene_type": "introduction",
                   "learning_objective": "Understand basics"
               }
           ]
       }
   
   @pytest.fixture  
   def mock_api_responses():
       return {
           "script_response": {...},
           "scene_response": {...},
           "image_response": {...}
       }
   ```

2. **테스트 결과 캐싱**
   ```python
   # 비싼 API 응답을 캐시하여 재사용
   @pytest.fixture(scope="session")
   def cached_api_response():
       cache_file = "tests/.cache/api_responses.json"
       if os.path.exists(cache_file):
           return json.load(open(cache_file))
       
       # 실제 API 호출 (1회만)
       response = expensive_api_call()
       
       # 캐시 저장
       json.dump(response, open(cache_file, 'w'))
       return response
   ```

---

### T014: 테스트 자동화 및 CI/CD 통합
**현재 상황**: 수동 테스트 실행, CI/CD 파이프라인 부재  
**목표**: 자동화된 테스트 실행 및 지속적 품질 관리  
**예상 결과**: 개발 속도 향상, 버그 조기 발견, 배포 안정성 확보

#### 작업 내용:
1. **GitHub Actions 워크플로우 구성**
   ```yaml
   # .github/workflows/test.yml
   name: Test Suite
   
   on: [push, pull_request]
   
   jobs:
     unit-tests:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Setup Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         - name: Install dependencies
           run: |
             pip install -r requirements.txt
             pip install -r requirements-dev.txt
         - name: Run unit tests
           run: pytest tests/unit/ --cov=src --cov-report=xml
         - name: Upload coverage
           uses: codecov/codecov-action@v3
   
     integration-tests:
       runs-on: ubuntu-latest
       if: github.event_name == 'push' && github.ref == 'refs/heads/main'
       steps:
         - uses: actions/checkout@v3
         - name: Setup Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         - name: Install dependencies
           run: |
             pip install -r requirements.txt
             pip install -r requirements-dev.txt
         - name: Run minimal integration tests
           env:
             GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
           run: pytest tests/integration/ -m "minimal" --maxfail=1
   ```

2. **테스트 성과 모니터링**
   ```python
   # tests/conftest.py
   import pytest
   import time
   from datetime import datetime
   
   @pytest.fixture(autouse=True)
   def test_performance_monitor(request):
       start_time = time.time()
       yield
       duration = time.time() - start_time
       
       # 느린 테스트 경고
       if duration > 5.0:
           print(f"⚠️ Slow test: {request.node.name} took {duration:.2f}s")
   ```

3. **테스트 결과 리포팅**
   ```bash
   # scripts/test_report.sh
   #!/bin/bash
   
   echo "🧪 Running comprehensive test suite..."
   
   # 단위 테스트
   echo "1️⃣ Unit Tests (Free)"
   pytest tests/unit/ --cov=src --cov-report=term-missing
   
   # 최소 통합 테스트  
   echo "2️⃣ Minimal Integration Tests (~$0.05)"
   pytest tests/integration/ -m "minimal" -v
   
   # 성능 테스트
   echo "3️⃣ Performance Tests"
   pytest tests/performance/ -v
   
   echo "✅ Test suite completed!"
   ```

---

### T015: 성능 벤치마크 및 회귀 테스트
**현재 상황**: 성능 측정 및 추적 시스템 부재  
**목표**: 성능 회귀 방지 및 최적화 효과 측정  
**예상 결과**: 성능 저하 조기 발견, 최적화 효과 정량화

#### 작업 내용:
1. **성능 벤치마크 테스트**
   ```python
   # tests/performance/test_benchmarks.py
   import pytest
   import time
   from src.agents.orchestrator_agent import OrchestratorAgent
   
   @pytest.mark.performance
   @pytest.mark.asyncio
   async def test_full_pipeline_performance():
       """전체 파이프라인 성능 벤치마크"""
       start_time = time.time()
       
       orchestrator = OrchestratorAgent()
       result = await orchestrator.create_video(
           topic="Performance test topic",
           cost_saving_mode=True,
           max_scenes=2
       )
       
       duration = time.time() - start_time
       
       # 성능 기준: 2분 이내 완료
       assert duration < 120, f"Pipeline too slow: {duration:.2f}s"
       
       # 결과 품질 검증
       assert result["build_report"]["success"] is True
       assert len(result["scene_packages"]) == 2
   
   @pytest.mark.performance
   def test_json_parser_performance():
       """JSON 파서 성능 테스트"""
       from src.core.json_parser import robust_json_parse
       
       # 큰 JSON 데이터로 테스트
       large_json = '{"scenes": [' + ','.join(['{"id": %d}' % i for i in range(1000)]) + ']}'
       
       start_time = time.time()
       result = robust_json_parse(large_json)
       duration = time.time() - start_time
       
       # 성능 기준: 1초 이내
       assert duration < 1.0, f"JSON parser too slow: {duration:.3f}s"
       assert len(result["scenes"]) == 1000
   ```

2. **성능 회귀 감지**
   ```python
   # tests/performance/conftest.py
   import json
   import os
   from pathlib import Path
   
   PERFORMANCE_BASELINE_FILE = "tests/performance/baselines.json"
   
   def load_performance_baselines():
       if os.path.exists(PERFORMANCE_BASELINE_FILE):
           return json.load(open(PERFORMANCE_BASELINE_FILE))
       return {}
   
   def save_performance_baseline(test_name: str, duration: float):
       baselines = load_performance_baselines()
       baselines[test_name] = duration
       json.dump(baselines, open(PERFORMANCE_BASELINE_FILE, 'w'), indent=2)
   
   def check_performance_regression(test_name: str, current_duration: float):
       baselines = load_performance_baselines()
       if test_name in baselines:
           baseline = baselines[test_name]
           regression_threshold = baseline * 1.2  # 20% 성능 저하 허용
           
           if current_duration > regression_threshold:
               pytest.fail(f"Performance regression detected in {test_name}: "
                          f"{current_duration:.2f}s > {regression_threshold:.2f}s "
                          f"(baseline: {baseline:.2f}s)")
   ```

---

### T009: 코드 품질 도구 도입
**현재 상황**: 코드 스타일 및 품질 관리 도구 부재  
**목표**: 일관된 코드 품질 및 스타일 유지  
**예상 결과**: 코드 리뷰 효율성 향상, 버그 사전 방지

#### 도입할 도구:
1. **Linting 도구**
   - `flake8` 또는 `ruff` for Python linting
   - `mypy` for type checking

2. **포맷팅 도구**
   - `black` for code formatting
   - `isort` for import sorting

3. **Pre-commit hooks**
   ```yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 23.7.0
       hooks:
         - id: black
   ```

---

## 🔧 Priority 5: 개발자 경험 개선

### T010: 개발 환경 표준화
**현재 상황**: 개발 환경 설정 가이드 부족  
**목표**: 일관되고 재현 가능한 개발 환경 제공  
**예상 결과**: 새 개발자 온보딩 시간 50% 단축

#### 작업 내용:
1. **Docker 컨테이너 환경 구성**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "run_shortfactory.py"]
   ```

2. **개발 환경 스크립트**
   ```bash
   # setup.sh
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **VS Code 설정 파일**
   - `.vscode/settings.json`
   - `.vscode/launch.json`

---

### T011: 로깅 및 모니터링 시스템 개선
**현재 상황**: 기본적인 로깅만 구현됨  
**목표**: 체계적인 로깅 및 모니터링 시스템 구축  
**예상 결과**: 디버깅 시간 60% 단축, 프로덕션 이슈 빠른 감지

#### 개선사항:
1. **구조화된 로깅**
   ```python
   import structlog
   
   logger = structlog.get_logger()
   logger.info("Scene generated", 
               scene_id=scene.id, 
               duration_ms=scene.duration,
               frame_count=len(scene.frames))
   ```

2. **로그 레벨 세분화**
   - DEBUG: 개발 시 상세 정보
   - INFO: 일반적인 작업 진행
   - WARNING: 주의가 필요한 상황
   - ERROR: 에러 발생
   - CRITICAL: 시스템 중단 수준

3. **메트릭 수집**
   - 생성 시간 추적
   - 성공/실패율 모니터링
   - API 사용량 추적

---

## 🚀 Priority 6: 아키텍처 현대화

### T012: 설정 관리 시스템 구축
**현재 상황**: 하드코딩된 설정값들이 산재  
**목표**: 중앙집중식 설정 관리 시스템  
**예상 결과**: 환경별 설정 관리 용이, 운영 효율성 향상

#### 작업 내용:
1. **Pydantic Settings 활용**
   ```python
   from pydantic import BaseSettings
   
   class Settings(BaseSettings):
       gemini_api_key: str
       lemonfox_api_key: str
       stability_api_key: str = None
       max_scenes: int = 8
       cost_saving_mode: bool = False
       
       class Config:
           env_file = ".env"
   ```

2. **환경별 설정 파일**
   - `config/development.env`
   - `config/production.env`
   - `config/testing.env`

---

### T013: 플러그인 시스템 구축
**현재 상황**: 새로운 에이전트 추가 시 코드 수정 필요  
**목표**: 확장 가능한 플러그인 아키텍처  
**예상 결과**: 새 기능 추가 시간 70% 단축, 유지보수성 향상

#### 설계:
1. **Agent Interface 정의**
   ```python
   from abc import ABC, abstractmethod
   
   class AgentInterface(ABC):
       @abstractmethod
       async def process(self, input_data: dict) -> dict:
           pass
   ```

2. **Dynamic Loading 시스템**
   - 런타임에 에이전트 로드
   - 플러그인 디스커버리 메커니즘

---

## 📊 구현 우선순위 및 타임라인

### Phase 1 (1주): 🚨 **CRITICAL** - 핵심 안정성 문제 해결
- **T003**: LLM 응답 구조화 시스템 완전 개편 ⚠️ **URGENT** (5일)
  - Pydantic 모델 기반 검증 시스템 (2일)
  - LLM 응답 처리 파이프라인 (2일)
  - 에이전트별 통합 및 테스트 (1일)

### Phase 2 (2-3주): 코드베이스 정리 및 기본 안정성
- **T001**: 레거시 코드 제거 (3일)
- **T002**: 불필요한 문서 정리 (2일)
- **T005**: 의존성 관리 (3일)
- **T004**: API 키 보안 강화 (3일)

### Phase 3 (3-5주): 견고한 테스트 시스템
- **T008**: 견고한 테스트 시스템 구축 (10일)
  - 단위 테스트 시스템 (4일)
  - 비용 효율적 통합 테스트 (4일)
  - 테스트 환경 및 도구 설정 (2일)

### Phase 4 (4-6주): 성능 최적화
- **T006**: 병렬 처리 시스템 (10일)
- **T007**: 메모리 최적화 (5일)
- **T011**: 로깅 시스템 개선 (3일)

### Phase 5 (6-8주): 개발자 경험 및 자동화
- **T009**: 코드 품질 도구 (3일)
- **T010**: 개발 환경 표준화 (5일)
- **T014**: 테스트 자동화 및 CI/CD 통합 (7일)
- **T012**: 설정 관리 시스템 (7일)

### Phase 6 (8-10주): 고급 기능 및 아키텍처 현대화
- **T015**: 성능 벤치마크 및 회귀 테스트 (5일)
- **T013**: 플러그인 시스템 (14일)

---

## 🎯 성공 지표

### 정량적 지표:
- **코드베이스 크기**: 30% 감소 (레거시 코드 제거)
- **단위 테스트 커버리지**: 90% 이상
- **통합 테스트 비용**: 일일 $0.10 이하 유지
- **생성 시간**: 50% 단축 (5분 → 2.5분)
- **메모리 사용량**: 40% 감소
- **버그 발생률**: 70% 감소
- **CI/CD 파이프라인**: 10분 이내 완료

### 정성적 지표:
- **개발자 온보딩**: 새 팀원이 1일 내 개발 환경 구축 가능
- **코드 품질**: 일관된 스타일과 높은 가독성 (linting 통과율 100%)
- **시스템 안정성**: 프로덕션 환경에서 99% 가용성
- **확장성**: 새 에이전트 추가 시 기존 코드 수정 최소화
- **테스트 신뢰성**: 단위 테스트는 무료, 통합 테스트는 저비용으로 신뢰할 수 있는 품질 보장

### 테스트 관련 특별 지표:
- **단위 테스트 실행 시간**: 30초 이내
- **최소 통합 테스트 비용**: $0.05 이하
- **전체 통합 테스트 비용**: $0.50 이하
- **성능 회귀 감지**: 20% 이상 성능 저하 시 자동 알림
- **테스트 안정성**: 95% 이상 성공률 유지

---

## 📝 결론

현재 ShortFactory Agent는 기능적으로는 완성도가 높은 상태이지만, **LLM 응답 구조화 문제**가 가장 큰 걸림돌이 되고 있습니다. 

### 🚨 **최우선 해결 과제**:
**LLM이 복잡한 JSON 스키마를 완벽하게 따르기를 기대하는 것은 비현실적**입니다. 이 문제를 해결하지 않으면 다른 모든 개선사항이 무의미해집니다.

### 📋 **핵심 전략**:
1. **Pydantic 기반 강력한 검증 시스템** - LLM 응답 변동성 완전 흡수
2. **자동 필드명 매핑** - `sfx_name` → `cue`, `start_ms` → `at_ms` 등
3. **Graceful Fallback** - 검증 실패 시에도 최소 유효 데이터 생성
4. **비용 효율적인 테스트** - 단위 테스트는 무료, 통합 테스트는 저비용

### 🎯 **제안된 15개 태스크의 기대 효과**:
1. **🚨 즉시 해결**: LLM 응답 문제로 인한 파이프라인 실패 98% 감소
2. **더 안전하고 안정적인** 시스템 - Pydantic 검증 + 보안 강화
3. **더 빠르고 효율적인** 성능 - 병렬 처리 + 메모리 최적화
4. **더 쉽고 즐거운** 개발 경험 - 자동화된 테스트 + CI/CD
5. **더 확장 가능한** 아키텍처 - 플러그인 시스템

### ⏰ **권장 실행 순서**:
**Phase 1 (1주)**: LLM 응답 구조화 시스템 완전 개편 ⚠️ **URGENT**  
→ 이것만 해결해도 시스템 안정성이 극적으로 향상됩니다.

**LLM에게 완벽한 JSON을 기대하지 말고, 우리가 유연하게 처리하는 것**이 핵심입니다! 🎯

---

*이 문서는 정기적으로 업데이트되며, 각 태스크의 진행 상황과 결과를 추적합니다.*
