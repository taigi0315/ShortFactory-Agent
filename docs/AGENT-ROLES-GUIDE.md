# ShortFactory Agent - 에이전트 역할 가이드

*작성일: 2025년 9월 18일*  
*시니어 기술 리드 엔지니어 작성*

## 🎯 개요

ShortFactory Agent는 **다중 에이전트 아키텍처**를 사용하여 토픽을 완성된 비디오 패키지로 변환하는 시스템입니다. 각 에이전트는 명확한 역할과 책임을 가지고 있으며, 파이프라인을 통해 협력하여 고품질 교육 비디오를 생성합니다.

---

## 🏗️ 에이전트 아키텍처 개요

```
사용자 토픽 → FSW → SSW → ICA → VGA → VMA → 완성된 비디오
             ↓     ↓     ↓     ↓     ↓
          스토리  씬   이미지  음성  비디오
          구조   상세   생성   생성  조립
```

---

## 🤖 핵심 에이전트들

### 1. Full Script Writer (FSW) 📖
**파일**: `src/agents/full_script_writer_agent.py`  
**역할**: **스토리 설계자** - 고수준 내러티브 구조 생성

#### 🎯 **주요 책임**:
- 입력 토픽을 분석하여 매력적인 스토리 프레임워크 생성
- 최적의 씬 수량 결정 (3-8개 씬)
- 씬 타입, 순서, 내러티브 흐름 정의
- 각 씬의 학습 목표 설정
- 중요도 레벨 (1-5) 및 애니메이션 요구사항 할당
- 씬 간 전환 계획

#### 📥 **입력**:
- `topic` (문자열): 비디오 주제
- `length_preference` (예: "60-90s"): 원하는 길이
- `style_profile` (예: "교육적이고 매력적인"): 톤과 스타일
- `target_audience` (예: "일반인"): 대상 청중
- `knowledge_refs` (선택사항): 참고 자료

#### 📤 **출력**:
```json
{
  "title": "비디오 제목",
  "logline": "한 줄 요약",
  "overall_style": "전체적인 톤과 스타일",
  "main_character": "주인공 설명",
  "cosplay_instructions": "캐릭터 코스프레 지시사항",
  "story_summary": "120-500단어 스토리 요약",
  "scenes": [
    {
      "scene_number": 1,
      "scene_type": "hook",
      "beats": ["스토리 비트들"],
      "learning_objectives": ["학습 목표들"],
      "needs_animation": true,
      "transition_to_next": "fade",
      "scene_importance": 5
    }
  ]
}
```

#### ❌ **하지 않는 것**:
- 상세한 나레이션 스크립트
- 구체적인 이미지 프롬프트
- TTS/음성 설정
- 캐릭터 포즈나 표정
- 저수준 프로덕션 디테일

---

### 2. Scene Script Writer (SSW) 🎬
**파일**: `src/agents/scene_script_writer_agent.py`  
**역할**: **프로덕션 디자이너** - 씬 비트를 프로덕션 준비 패키지로 변환

#### 🎯 **주요 책임**:
- FSW의 고수준 씬 비트를 받아서 상세 확장
- 정확한 타이밍의 나레이션 스크립트 생성
- 포괄적인 비주얼 스토리보드 생성 (씬당 3-8개 프레임)
- 기술적 사양을 포함한 구체적인 이미지 프롬프트 설계
- TTS 설정 및 음성 매개변수 구성
- 씬 연속성 및 비주얼 일관성 관리
- 교육적 콘텐츠 강화

#### 📥 **입력**:
- FSW의 `scene_data` (씬 비트 정보)
- `global_context` (캐릭터, 스타일, 제약사항)
- `previous_scenes` (연속성을 위한 이전 씬들)

#### 📤 **출력**:
```json
{
  "scene_number": 1,
  "narration_script": [
    {
      "line": "나레이션 텍스트",
      "at_ms": 0,
      "pause_ms": 500
    }
  ],
  "visuals": [
    {
      "frame_id": "1A",
      "shot_type": "medium",
      "image_prompt": "상세한 이미지 생성 프롬프트 (40자 이상)",
      "negative_prompt": "원하지 않는 요소들",
      "aspect_ratio": "16:9",
      "character_pose": "캐릭터 포즈",
      "expression": "표정",
      "background": "배경 설명",
      "lighting": "조명 설명"
    }
  ],
  "tts": {
    "engine": "lemonfox",
    "voice": "sarah",
    "language": "en-US",
    "speed": 1.0
  },
  "timing": {
    "total_ms": 45000,
    "estimated": true
  },
  "dialogue": [],
  "on_screen_text": []
}
```

#### 🔧 **핵심 기능**:
- **ELABORATION**: 풍부한 디테일, 사실, 매력적인 내러티브 추가
- **HOOKING**: 주의를 끄는 요소와 호기심 갭 포함
- **TIMING**: 나레이션과 효과의 정밀한 밀리초 타이밍
- **VISUAL DETAIL**: 샷 타입, 카메라 움직임, 조명, 색상 분위기
- **CONTINUITY**: 씬 간 콜백 태그와 비주얼 모티프

---

### 3. Image Create Agent (ICA) 🖼️
**파일**: `src/agents/image_create_agent.py`  
**역할**: **비주얼 아티스트** - 정확한 사양에 맞는 이미지 생성

#### 🎯 **주요 책임**:
- SSW의 비주얼 프레임 사양 처리
- 캐릭터 일관성 요소로 프롬프트 강화
- 프롬프트 정화 및 안전성 검사
- AI 모델을 사용한 이미지 생성 (또는 cost-saving 모드에서 Mock 이미지)
- 각 에셋에 대한 포괄적인 메타데이터 생성
- 파일 구성 및 썸네일 관리

#### 📥 **입력**:
- SSW의 `scene_package.visuals[]` (프레임 사양, 프롬프트, 설정)

#### 📤 **출력**:
```json
{
  "frame_id": "1A",
  "image_uri": "sessions/20250918-xxx/images/1a.png",
  "thumbnail_uri": "sessions/20250918-xxx/images/1a_thumb.png",
  "prompt_used": "실제 사용된 프롬프트",
  "negative_prompt_used": "실제 사용된 네거티브 프롬프트",
  "model": "사용된 AI 모델",
  "safety_result": "안전성 검사 결과",
  "generation_time_ms": 1500,
  "metadata": {
    "width": 1920,
    "height": 1080,
    "file_size_bytes": 245760,
    "format": "PNG"
  }
}
```

#### 🔧 **핵심 기능**:
- **캐릭터 일관성**: Glowbie 캐릭터 참조로 일관된 외관 유지
- **프롬프트 강화**: 스타일 키워드 및 품질 수정자 추가
- **안전성 검증**: 콘텐츠 안전성 및 적절성 검사
- **메타데이터 추적**: 생성 매개변수, 타이밍, 파일 정보
- **비용 제어**: 개발/테스트용 Mock 이미지 모드

---

### 4. Voice Generate Agent (VGA) 🎤
**파일**: `src/agents/voice_generate_agent.py`  
**역할**: **음성 아티스트** - 고품질 TTS 오디오 파일 생성

#### 🎯 **주요 책임**:
- Scene Script Writer 패키지에서 나레이션 텍스트 추출
- LemonFox AI API를 사용한 TTS 생성 (ElevenLabs 대비 90% 비용 절약)
- 순서가 있는 명명으로 MP3 오디오 파일 생성
- 포괄적인 음성 에셋 메타데이터 생성
- 실제 TTS 길이를 기반으로 정확한 타이밍 계산

#### 📥 **입력**:
- SSW의 `ScenePackage[].json` (narration_script, tts 설정)

#### 📤 **출력**:
```json
{
  "scene_number": 1,
  "voice_file": "sessions/20250918-xxx/voices/scene_01_voice.mp3",
  "duration_ms": 45230,
  "text_used": "실제 TTS에 사용된 텍스트",
  "voice_settings": {
    "engine": "lemonfox",
    "voice": "sarah",
    "speed": 1.0
  },
  "generation_time_ms": 3200,
  "file_size_bytes": 1048576,
  "estimated_cost": 0.002
}
```

#### 🔧 **핵심 기능**:
- **LemonFox 통합**: 전문 TTS, 음성 커스터마이징
- **정확한 타이밍**: 실제 생성된 오디오 길이 측정
- **기본 음성 Fallback**: 커스텀 음성 불가 시 무료 Sarah 음성 사용
- **메타데이터 추적**: 생성 매개변수, 파일 크기, 타이밍
- **에러 처리**: 상세한 API 응답 로깅 및 fallback 메커니즘

---

### 5. Video Maker Agent (VMA) 🎞️
**파일**: `src/agents/video_maker_agent.py`  
**역할**: **비디오 편집자** - 모든 에셋을 최종 비디오로 조립

#### 🎯 **주요 책임**:
- 이미지, 음성, 타이밍 정보를 최종 비디오로 조립
- FFmpeg를 사용한 비디오 타임라인 구성
- 나레이션 타이밍과 오디오 동기화
- 씬 전환 효과 구현
- 최종 비디오 내보내기 및 최적화

#### 📥 **입력**:
- 모든 씬의 이미지 파일들
- 모든 씬의 음성 파일들
- 정확한 타이밍 정보
- 전환 효과 사양

#### 📤 **출력**:
```json
{
  "video_path": "sessions/20250918-xxx/final_video.mp4",
  "duration_ms": 180500,
  "resolution": "1920x1080",
  "fps": 30,
  "file_size_bytes": 15728640,
  "scenes_count": 5,
  "total_frames": 150,
  "audio_sync": "perfect",
  "generation_time_ms": 8500
}
```

#### 🔧 **핵심 기능**:
- **FFmpeg 통합**: 비디오 타임라인 구성을 위한 FFmpeg
- **오디오 동기화**: 나레이션 타이밍과 자동 동기화
- **전환 효과**: 씬 간 부드러운 전환 구현
- **품질 최적화**: 최종 비디오 압축 및 최적화

---

### 6. Orchestrator Agent 🎼
**파일**: `src/agents/orchestrator_agent.py`  
**역할**: **파이프라인 매니저** - 전체 워크플로우 제어 및 품질 관리

#### 🎯 **주요 책임**:
- 완전한 비디오 프로덕션 파이프라인 관리
- 에이전트 상호작용 및 데이터 흐름 조정
- 각 단계에서 JSON 스키마 검증 수행
- 에러, 재시도, fallback 메커니즘 처리
- 타이밍, 모델 사용량, 성능 메트릭 추적
- 포괄적인 빌드 보고서 생성
- 세션 라이프사이클 및 파일 구성 관리

#### 📥 **입력**:
- `topic`: 비디오 주제
- `preferences`: 길이, 스타일, 청중 선호도
- `options`: 비용 절약 모드, 언어 등

#### 📤 **출력**:
```json
{
  "session_id": "20250918-uuid",
  "full_script": { /* FSW 출력 */ },
  "scene_packages": [ /* SSW 출력들 */ ],
  "image_assets": [ /* ICA 출력들 */ ],
  "voice_assets": [ /* VGA 출력들 */ ],
  "video_metadata": { /* VMA 출력 */ },
  "build_report": {
    "success": true,
    "total_time_seconds": 180.5,
    "stages": {
      "full_script_writer": {"status": "success", "time_ms": 25000},
      "scene_script_writer": {"status": "success", "time_ms": 300000},
      "image_create_agent": {"status": "success", "time_ms": 1000},
      "voice_generate_agent": {"status": "success", "time_ms": 65000},
      "video_maker_agent": {"status": "success", "time_ms": 8500}
    },
    "performance_metrics": {
      "overall_success_rate": 1.0,
      "json_parsing_success_rate": 0.95,
      "total_scenes": 5,
      "successful_scenes": 5
    }
  }
}
```

#### 🔧 **핵심 기능**:
- **상태 머신**: 파이프라인 진행을 단계별로 제어
- **검증 게이트**: 각 단계 진행 전 스키마 검증
- **에러 처리**: 상세한 에러 추적과 graceful failure 처리
- **성능 모니터링**: 타이밍 분석 및 리소스 사용량 추적
- **빌드 리포팅**: 성공/실패 메트릭이 포함된 포괄적인 보고서

---

## 🔄 에이전트 간 데이터 흐름

### Stage 1: 스토리 계획
```
사용자 토픽 → FSW → FullScript.json
```
- 토픽 분석 및 스토리 구조화
- 씬 수량 및 타입 결정
- 학습 목표 설정

### Stage 2: 씬 상세화
```
FullScript.json → SSW (씬별) → ScenePackage.json × N
```
- 각 씬 비트를 상세한 프로덕션 패키지로 확장
- 나레이션 스크립트 및 타이밍 생성
- 비주얼 프레임 및 이미지 프롬프트 설계

### Stage 3: 이미지 생성
```
ScenePackage[].visuals → ICA → ImageAsset.json
```
- 모든 프레임에 대한 이미지 생성
- 캐릭터 일관성 유지
- 메타데이터 및 파일 관리

### Stage 4: 음성 생성
```
ScenePackage[].narration_script → VGA → voice_assets.json
```
- 모든 씬에 대한 TTS 오디오 생성
- 실제 오디오 길이 측정 및 타이밍 업데이트
- 음성 파일 구성

### Stage 5: 비디오 조립
```
모든 에셋 → VMA → final_video.mp4
```
- 이미지, 음성, 타이밍을 최종 비디오로 조립
- 씬 전환 및 효과 적용
- 최종 비디오 내보내기

---

## 📊 에이전트별 성능 특성

### 처리 시간 (일반적인 5씬 비디오):
- **FSW**: ~25초 (스토리 계획)
- **SSW**: ~300초 (씬별 상세화, 5씬 × 60초)
- **ICA**: <1초 (cost-saving 모드) / ~60초 (AI 모드)
- **VGA**: ~65초 (5씬 음성 생성)
- **VMA**: ~8초 (비디오 조립)
- **총 시간**: ~6-7분 (완전한 비디오 패키지)

### 출력 품질:
- **씬**: 풍부한 내러티브 구조를 가진 3-8개 씬
- **이미지**: 총 15-40개 이미지 (씬당 3-8개 프레임)
- **콘텐츠 깊이**: 구체적인 사실들과 교육적 강화
- **프로덕션 준비**: 완전한 TTS, 타이밍, 비주얼 사양

---

## 🔧 지원 컴포넌트들

### Session Manager
**파일**: `src/core/session_manager.py`  
**역할**: 세션 라이프사이클 및 파일 구성 관리
- 날짜 접두사 세션 ID (YYYYMMDD-UUID)
- 구조화된 디렉토리 생성
- 스크립트, 이미지, 메타데이터, 프롬프트, 빌드 보고서 관리

### Shared Context Manager
**파일**: `src/core/shared_context.py`  
**역할**: 모든 에이전트 간 일관성 유지
- 캐릭터 상태, 비주얼 스타일, 내러티브 컨텍스트 관리
- 기술적 제약사항 추적
- 씬 생성 후 연속성을 위한 업데이트

### Enhanced Response Models
**파일**: `src/core/enhanced_response_models.py`  
**역할**: LLM 응답의 변동성 흡수
- 자동 필드명 매핑 (sfx_name→cue, start_ms→at_ms)
- 타입 자동 변환 ('3s'→3000ms)
- 필수 필드 누락 시 기본값 설정
- Graceful fallback 시스템

---

## 🎯 실제 사용되는 기능들

### ✅ **현재 활발히 사용**:
- **나레이션 스크립트**: 정확한 타이밍의 텍스트
- **이미지 생성**: 씬당 다중 프레임
- **TTS 음성**: LemonFox AI 사용
- **비디오 조립**: FFmpeg 기반
- **캐릭터 일관성**: Glowbie 캐릭터 시스템

### ❌ **사용하지 않음 (제거 대상)**:
- **SFX 큐**: 사운드 이펙트 사용 안 함
- **ElevenLabs**: LemonFox로 대체됨 (90% 비용 절약)
- **복잡한 Continuity**: 단순한 전환만 사용
- **On-screen Text**: 현재 활용도 낮음
- **Dialogue**: 주로 나레이션 중심

---

## 🔄 에이전트 협력 패턴

### 1. **순차적 파이프라인**:
각 에이전트는 이전 에이전트의 출력을 입력으로 받아 처리

### 2. **검증 게이트**:
Orchestrator가 각 단계에서 출력 품질 검증

### 3. **Fallback 시스템**:
에이전트 실패 시 최소 유효 데이터로 계속 진행

### 4. **상태 공유**:
Shared Context Manager를 통한 일관성 유지

---

## 🚀 에이전트 확장성

### 새 에이전트 추가 시:
1. **Base Agent Interface** 구현
2. **입력/출력 스키마** 정의
3. **Orchestrator에 등록**
4. **테스트 작성**

### 기존 에이전트 수정 시:
1. **스키마 호환성** 확인
2. **하위 호환성** 유지
3. **성능 영향** 측정
4. **통합 테스트** 업데이트

---

## 📝 에이전트별 개발 가이드라인

### 모든 에이전트 공통:
- **Single Responsibility**: 하나의 명확한 책임
- **Schema Compliance**: 정의된 입력/출력 스키마 준수
- **Error Handling**: Graceful failure 및 fallback 지원
- **Logging**: 상세한 디버깅 정보 제공
- **Testing**: 단위 테스트 및 통합 테스트 포함

### 성능 고려사항:
- **API 효율성**: 불필요한 호출 최소화
- **메모리 관리**: 대용량 데이터 스트리밍 처리
- **병렬 처리**: 가능한 곳에서 비동기 처리
- **캐싱**: 재사용 가능한 결과 캐시

---

## 🎉 결론

ShortFactory Agent의 다중 에이전트 시스템은 **명확한 역할 분리**와 **강력한 협력 메커니즘**을 통해 복잡한 비디오 생성 작업을 효율적으로 처리합니다.

### 핵심 장점:
1. **모듈성**: 각 에이전트를 독립적으로 개선 가능
2. **확장성**: 새로운 에이전트 쉽게 추가 가능
3. **디버깅**: 완전한 감사 추적 및 로깅
4. **품질 제어**: 다층 검증 및 안전성 검사
5. **성능**: 병렬 처리 잠재력을 가진 최적화된 파이프라인

**각 에이전트는 자신의 전문 분야에 집중하면서, 전체 시스템의 일부로서 완벽하게 협력합니다.** 🚀

---

*이 문서는 시스템 발전에 따라 정기적으로 업데이트됩니다.*
