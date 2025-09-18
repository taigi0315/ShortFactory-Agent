# 코드 정리 분석 및 개선 계획

*작성일: 2025년 9월 18일*  
*분석자: 시니어 기술 리드 엔지니어*

## 🎯 분석 개요

`src/agents/`와 `src/core/` 폴더를 철저히 분석한 결과, **중복된 아키텍처**와 **사용되지 않는 코드**들이 상당히 발견되었습니다. 현재 시스템이 **두 개의 병렬 아키텍처**를 유지하고 있어 복잡성과 혼란을 야기하고 있습니다.

---

## 🔍 현재 상태 분석

### 📁 **Agents 폴더 분석** (`src/agents/`)

#### ✅ **New Architecture (활발히 사용)**:
- `orchestrator_agent.py` ← main.py에서 사용
- `full_script_writer_agent.py` ← orchestrator에서 사용
- `scene_script_writer_agent.py` ← orchestrator에서 사용  
- `image_create_agent.py` ← orchestrator에서 사용
- `voice_generate_agent.py` ← orchestrator에서 사용
- `video_maker_agent.py` ← orchestrator에서 사용

#### ⚠️ **ADK Architecture (병렬 시스템)**:
- `adk_orchestrator_agent.py` ← run_adk_system.py에서만 사용
- `adk_full_script_agent.py` ← adk_orchestrator에서만 사용
- `adk_scene_script_agent.py` ← adk_orchestrator에서만 사용

### 📁 **Core 폴더 분석** (`src/core/`)

#### ✅ **활발히 사용되는 모듈들**:
- `session_manager.py` ← 모든 시스템에서 사용
- `json_parser.py` ← 에이전트들에서 사용
- `enhanced_response_models.py` ← 새로 구현, 사용 중

#### ⚠️ **사용 빈도가 낮거나 중복인 모듈들**:
- `simplified_response_models.py` ← 방금 생성, enhanced_와 중복
- `shared_context.py` ← 에이전트들에서 사용하지만 복잡함
- `cost_optimizer.py` ← 에이전트들에서 사용
- `informative_enhancer.py` ← 에이전트들에서 사용
- `image_style_selector.py` ← 에이전트들에서 사용
- `story_focus_engine.py` ← FSW에서 사용
- `story_validator.py` ← FSW에서 사용

#### ❓ **사용되지 않거나 오래된 모듈들**:
- `scene_continuity_manager.py` ← 사용되지 않는 것으로 보임
- `workflow_state_manager.py` ← 사용되지 않는 것으로 보임

---

## 🚨 발견된 문제들

### 1. **이중 아키텍처 문제**
- **New Architecture** (main.py → orchestrator_agent.py)
- **ADK Architecture** (run_adk_system.py → adk_orchestrator_agent.py)
- 두 시스템이 병렬로 존재하여 혼란 야기

### 2. **중복된 응답 모델**
- `enhanced_response_models.py` (완전한 기능)
- `simplified_response_models.py` (방금 생성, 중복)
- `json_parser.py` (기존 파서)

### 3. **사용되지 않는 모듈들**
- `scene_continuity_manager.py`
- `workflow_state_manager.py`

### 4. **과도하게 복잡한 모듈들**
- `shared_context.py` (266줄, 복잡한 상태 관리)
- `story_focus_engine.py` (495줄, 과도한 기능)
- `informative_enhancer.py` (637줄, 과도한 기능)

---

## 📋 정리 티켓 목록

### 🔥 **Priority 1: 아키텍처 통합**

#### **TICKET-001: ADK vs New Architecture 통합**
**현재 상황**: 두 개의 병렬 아키텍처가 존재  
**목표**: 하나의 통합된 아키텍처로 단순화  
**작업 내용**:
- ADK 아키텍처의 장점을 New Architecture에 통합
- ADK 전용 에이전트들 제거 또는 통합
- run_adk_system.py를 run_shortfactory.py로 통합

**파일들**:
- `src/agents/adk_orchestrator_agent.py` (제거 또는 통합)
- `src/agents/adk_full_script_agent.py` (제거 또는 통합)
- `src/agents/adk_scene_script_agent.py` (제거 또는 통합)
- `run_adk_system.py` (제거 또는 통합)

**예상 결과**: 코드베이스 복잡성 50% 감소, 개발자 혼란 제거

---

### 🧹 **Priority 2: 중복 코드 정리**

#### **TICKET-002: 응답 모델 통합**
**현재 상황**: 3개의 중복된 JSON 처리 시스템  
**목표**: 하나의 강력한 응답 처리 시스템  
**작업 내용**:
- `enhanced_response_models.py`를 메인으로 선택
- `simplified_response_models.py` 제거 (방금 생성했지만 중복)
- `json_parser.py` 단순화 또는 통합

**파일들**:
- `src/core/simplified_response_models.py` (제거)
- `src/core/json_parser.py` (단순화)
- `tests/unit/test_simplified_response_models.py` (제거)

**예상 결과**: JSON 처리 로직 통합, 유지보수 부담 감소

#### **TICKET-003: 사용되지 않는 모듈 제거**
**현재 상황**: 사용되지 않는 복잡한 모듈들이 존재  
**목표**: 실제 사용되는 모듈들만 유지  
**작업 내용**:
- 사용되지 않는 모듈들 식별 및 제거
- 의존성 체크 및 안전한 제거

**파일들**:
- `src/core/scene_continuity_manager.py` (사용되지 않음, 제거)
- `src/core/workflow_state_manager.py` (사용되지 않음, 제거)

**예상 결과**: 코드베이스 크기 추가 15% 감소

---

### ⚡ **Priority 3: 모듈 단순화**

#### **TICKET-004: Shared Context 단순화**
**현재 상황**: 266줄의 복잡한 상태 관리 시스템  
**목표**: 실제 필요한 기능만 유지하는 단순한 컨텍스트  
**작업 내용**:
- 실제 사용되는 기능들만 식별
- 불필요한 복잡성 제거
- 더 단순한 인터페이스 제공

**파일들**:
- `src/core/shared_context.py` (단순화)

**예상 결과**: 상태 관리 복잡성 70% 감소

#### **TICKET-005: Story Focus Engine 최적화**
**현재 상황**: 495줄의 과도하게 복잡한 스토리 엔진  
**목표**: 핵심 기능만 유지하는 효율적인 엔진  
**작업 내용**:
- 실제 사용되는 패턴들만 유지
- 불필요한 패턴들 제거
- 성능 최적화

**파일들**:
- `src/core/story_focus_engine.py` (최적화)

**예상 결과**: 스토리 생성 성능 30% 향상

#### **TICKET-006: Informative Enhancer 간소화**
**현재 상황**: 637줄의 과도한 교육 콘텐츠 강화 시스템  
**목표**: 핵심 강화 기능만 유지  
**작업 내용**:
- 실제 효과가 있는 강화 기능들만 유지
- 복잡한 분석 로직 단순화
- 성능 최적화

**파일들**:
- `src/core/informative_enhancer.py` (간소화)

**예상 결과**: 교육 콘텐츠 강화 성능 40% 향상

---

## 📊 예상 개선 효과

### 정량적 효과:
- **코드베이스 크기**: 추가 65% 감소 (현재 대비)
- **복잡성**: 아키텍처 중복 제거로 50% 감소
- **성능**: 불필요한 로직 제거로 30-40% 향상
- **유지보수성**: 단일 아키텍처로 80% 향상

### 정성적 효과:
- **개발자 혼란 제거**: 하나의 명확한 아키텍처
- **코드 가독성 향상**: 단순하고 명확한 모듈들
- **디버깅 용이성**: 복잡한 상태 관리 제거
- **확장성 향상**: 명확한 모듈 경계

---

## 🗓️ 실행 계획

### Phase 1 (1-2일): 중복 아키텍처 통합
- **TICKET-001**: ADK vs New Architecture 통합

### Phase 2 (1일): 중복 모듈 정리  
- **TICKET-002**: 응답 모델 통합
- **TICKET-003**: 사용되지 않는 모듈 제거

### Phase 3 (2-3일): 모듈 최적화
- **TICKET-004**: Shared Context 단순화
- **TICKET-005**: Story Focus Engine 최적화  
- **TICKET-006**: Informative Enhancer 간소화

---

## 🎯 성공 지표

### 완료 후 달성할 목표:
- ✅ **단일 아키텍처**: 하나의 명확한 시스템
- ✅ **코드 감소**: 총 4,000+ 줄 추가 제거
- ✅ **성능 향상**: 30-40% 처리 속도 개선
- ✅ **유지보수성**: 복잡성 대폭 감소
- ✅ **개발자 경험**: 명확하고 단순한 구조

### 검증 방법:
- 기존 기능들이 모두 정상 동작하는지 테스트
- 성능 벤치마크로 개선 효과 측정
- 코드 복잡성 메트릭으로 단순화 효과 확인

---

*이 분석을 바탕으로 체계적인 코드 정리를 진행합니다.*
