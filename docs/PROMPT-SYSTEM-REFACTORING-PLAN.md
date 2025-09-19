# 프롬프트 시스템 리팩토링 계획서

## 개요
ShortFactory-Agent의 프롬프트 시스템을 단순화하고 확장 가능하게 만들기 위한 리팩토링 계획입니다. 현재 시스템의 문제점을 분석하고 개선 방안을 제시합니다.

## 현재 시스템 분석

### 1. 현재 프롬프트 구조
- **Full Script Writer Agent**: 전체 스크립트 구조 생성 (6개 씬)
- **Scene Script Writer Agent**: 개별 씬을 상세한 제작 패키지로 확장
- **스키마**: FullScript.json, ScenePackage.json으로 구조화

### 2. 식별된 문제점

#### A. 불필요한 타이밍 복잡성
- `at_ms` 파라미터가 narration_script에 포함되어 있음
- 실제로는 오디오 파일을 concat하는 방식이므로 불필요
- 타이밍 계산의 복잡성만 증가시킴

#### B. 제한적인 음성 제어
- 현재 TTS 설정이 기본적인 speed만 제공
- lemonfox 엔진의 다양한 음성 톤 활용 불가
- 감정 표현이나 강조를 위한 음성 변화 부족

#### C. 이미지 프롬프트의 한계
- `image_prompt`에 캐릭터 설명이 매번 반복됨
- 일관성 있는 캐릭터 유지의 어려움
- 이미지 생성 가이드라인 부족으로 품질 편차 발생

#### D. 스토리 깊이 부족
- 현재 Minecraft 구리 업데이트 예시가 너무 일반적
- 실제 예시나 비교 설명 부족
- 교육적 깊이가 얕음

## 개선 계획

### Phase 1: 스키마 단순화 및 최적화

#### 1.1 narration_script 구조 개선
**현재:**
```json
"narration_script": [
  {
    "line": "텍스트",
    "at_ms": 0,
    "pause_ms": 500
  }
]
```

**개선 후:**
```json
"narration_script": [
  {
    "line": "텍스트",
    "voice_settings": {
      "speed": 1.1,
      "emphasis": "normal",
      "pause_after": "short"
    }
  }
]
```

#### 1.2 음성 제어 확장
**추가할 voice_settings 옵션:**
- `speed`: 0.7-1.3 (현재 유지)
- `emphasis`: "normal", "strong", "gentle"
- `pause_after`: "none", "short", "medium", "long"
- `tone`: "conversational", "excited", "explanatory", "dramatic"

### Phase 2: 이미지 생성 개선

#### 2.1 캐릭터 설명 분리
**현재:**
```json
"visuals": [
  {
    "frame_id": "scene4_frame1",
    "image_prompt": "Glowbie character with cheerful expression, standing in workshop..."
  }
]
```

**개선 후:**
```json
"visuals": [
  {
    "frame_id": "scene4_frame1",
    "character": {
      "name": "Glowbie",
      "expression": "cheerful",
      "pose": "gesturing energetically",
      "outfit": "default"
    },
    "scene_prompt": "vibrant futuristic workshop with floating holographic schematics",
    "camera": {
      "shot_type": "medium shot",
      "angle": "eye level",
      "focus": "character and background"
    },
    "style_hints": ["dynamic lighting", "high detail", "sci-fi fantasy"]
  }
]
```

#### 2.2 이미지 생성 가이드라인 강화
- 캐릭터 일관성 유지 규칙
- 배경과 소품의 세부 지침
- 조명과 색상 팔레트 가이드
- 카메라 앵글과 구도 표준

### Phase 3: 스토리 깊이 향상

#### 3.1 교육 콘텐츠 강화 전략
**현재 문제:**
- "구리 산화" 설명이 게임 내 기능에만 집중
- 실제 과학적 배경 설명 부족

**개선 방안:**
- 실제 구리 산화 과정과 연결
- 역사적 맥락 (구리 시대, 청동기 시대)
- 실생활 응용 사례 (자유의 여신상, 구리 지붕 등)
- 비교 학습 (다른 금속의 산화 과정)

#### 3.2 스토리텔링 구조 개선
**새로운 씬 구조 제안:**
1. **Hook**: 흥미로운 질문이나 현상 제시
2. **Context**: 실제 과학/역사적 배경
3. **Game Connection**: 게임 내 구현 방식
4. **Real World Examples**: 실생활 사례
5. **Deeper Dive**: 심화 학습 내용
6. **Summary**: 핵심 내용 정리 및 다음 학습 연결

### Phase 4: 프롬프트 템플릿 체계화

#### 4.1 프롬프트 모듈화
현재 agent 파일 내 하드코딩된 instruction을 외부 템플릿으로 분리:

```
agent_prompt_template/
├── full_script_writer/
│   ├── base_instruction.md
│   ├── scene_types_guide.md
│   └── educational_content_guide.md
├── scene_script_writer/
│   ├── base_instruction.md
│   ├── narration_guide.md
│   ├── visual_guide.md
│   └── character_consistency_guide.md
└── shared/
    ├── character_profiles.md
    ├── style_guidelines.md
    └── quality_standards.md
```

#### 4.2 동적 프롬프트 생성
- 콘텐츠 타입별 특화 프롬프트
- 대상 연령대별 언어 조정
- 주제별 전문 용어 및 설명 방식 조정

## 구현 우선순위

### 우선순위 1 (즉시 구현)
1. ✅ **at_ms 제거**: narration_script에서 타이밍 정보 제거
2. ✅ **voice_settings 추가**: 기본적인 음성 제어 옵션 추가
3. ✅ **character 분리**: image_prompt에서 캐릭터 정보 분리

### 우선순위 2 (단기 구현)
4. **이미지 가이드라인**: 더 상세한 이미지 생성 지침
5. **스토리 깊이**: 교육 콘텐츠 강화 및 실제 사례 연결

### 우선순위 3 (중기 구현)
6. **프롬프트 템플릿화**: 외부 템플릿 파일로 분리
7. **동적 프롬프트**: 콘텐츠 타입별 특화

## 예상 효과

### 1. 개발 효율성 향상
- 프롬프트 수정이 코드 변경 없이 가능
- A/B 테스트를 통한 프롬프트 최적화
- 새로운 콘텐츠 타입 추가 용이성

### 2. 콘텐츠 품질 향상
- 더 일관성 있는 캐릭터 표현
- 교육적 깊이가 있는 콘텐츠
- 다양한 음성 표현으로 몰입도 증가

### 3. 확장성 개선
- 새로운 언어나 스타일 쉽게 추가
- 다른 주제 영역으로 확장 용이
- 사용자 맞춤형 콘텐츠 생성 가능

## 위험 요소 및 대응 방안

### 1. 기존 시스템 호환성
**위험**: 기존 생성된 콘텐츠와의 호환성 문제
**대응**: 점진적 마이그레이션 및 하위 호환성 유지

### 2. 프롬프트 복잡도 증가
**위험**: 과도한 세분화로 인한 관리 복잡성
**대응**: 명확한 문서화 및 기본값 설정

### 3. 성능 영향
**위험**: 더 복잡한 프롬프트로 인한 응답 시간 증가
**대응**: 프롬프트 길이 최적화 및 성능 모니터링

## 다음 단계

1. **Phase 1 구현**: 스키마 변경 및 기본 기능 개선
2. **테스트 및 검증**: 기존 콘텐츠와 품질 비교
3. **문서화**: 새로운 프롬프트 가이드라인 작성
4. **점진적 롤아웃**: 단계별 기능 배포
5. **피드백 수집**: 사용자 및 개발자 피드백 반영

---

*작성일: 2025-09-19*
*작성자: LLM Prompt Agent*
*버전: 1.0*
