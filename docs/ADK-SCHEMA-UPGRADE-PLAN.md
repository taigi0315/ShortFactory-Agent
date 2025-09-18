# ADK 스키마 업그레이드 계획

*작성일: 2025년 9월 18일*  
*참조: [ADK 공식 문서 - Structuring Data](https://google.github.io/adk-docs/agents/llm-agents/#structuring-data-input_schema-output_schema-output_key)*

## 🎯 업그레이드 목표

현재 시스템을 **ADK 공식 패턴**에 맞게 업그레이드하여 더 안정적이고 구조화된 데이터 처리를 구현합니다.

### 핵심 개념 (ADK 문서 기반):
- **`input_schema`**: 에이전트가 받는 입력 데이터의 구조 정의
- **`output_schema`**: 에이전트가 출력하는 데이터의 구조 강제
- **`output_key`**: 세션 상태에 결과를 저장할 키 이름

---

## 🏗️ 현재 상황 분석

### ✅ **이미 부분적으로 구현됨**:
```python
# src/agents/adk_full_script_agent.py
self.input_schema = self._load_input_schema()
self.output_schema = self._load_output_schema()
```

### ⚠️ **개선 필요사항**:
1. **Pydantic 모델 기반 스키마 생성** - 현재는 수동으로 딕셔너리 작성
2. **모든 에이전트에 일관된 스키마 적용** - 현재는 일부만 적용
3. **output_key 활용** - 세션 상태 관리 개선
4. **타입 안전성 강화** - Pydantic 검증 활용

---

## 📋 작업 태스크 목록

### **TASK-A: Pydantic 기반 스키마 모델 구축**

#### **A1: 입력 스키마 모델들**
```python
# src/schemas/input_models.py

class FullScriptInput(BaseModel):
    """Full Script Writer 입력 스키마"""
    topic: str = Field(min_length=5, description="비디오 주제")
    length_preference: Literal["30-45s", "60-90s", "2-3min", "3-5min"] = Field(description="원하는 비디오 길이")
    style_profile: str = Field(description="전체적인 스타일과 톤")
    target_audience: str = Field(description="대상 청중")
    language: str = Field(default="English", description="콘텐츠 언어")
    knowledge_refs: Optional[List[str]] = Field(default=None, description="참고 자료")

class SceneExpansionInput(BaseModel):
    """Scene Script Writer 입력 스키마"""
    scene_data: Dict[str, Any] = Field(description="FSW에서 생성된 씬 데이터")
    global_context: Dict[str, Any] = Field(description="글로벌 컨텍스트")
    previous_scenes: Optional[List[Dict[str, Any]]] = Field(default=None, description="이전 씬들")

class ImageGenerationInput(BaseModel):
    """Image Create Agent 입력 스키마"""
    visual_specs: List[Dict[str, Any]] = Field(description="비주얼 프레임 사양들")
    session_id: str = Field(description="세션 ID")
    cost_saving_mode: bool = Field(default=False, description="비용 절약 모드")
```

#### **A2: 출력 스키마 모델들**
```python
# src/schemas/output_models.py

class FullScriptOutput(BaseModel):
    """Full Script Writer 출력 스키마 - ADK output_schema 준수"""
    title: str = Field(min_length=5, description="비디오 제목")
    logline: Optional[str] = Field(description="한 줄 요약")
    overall_style: str = Field(description="전체적인 톤과 스타일")
    main_character: Optional[str] = Field(description="주인공 설명")
    cosplay_instructions: Optional[str] = Field(description="캐릭터 코스프레 지시사항")
    story_summary: str = Field(min_length=60, max_length=2000, description="스토리 요약")
    scenes: List[SceneBeat] = Field(min_length=3, max_length=10, description="씬 비트들")

class ScenePackageOutput(BaseModel):
    """Scene Script Writer 출력 스키마 - ADK output_schema 준수"""
    scene_number: int = Field(ge=1, description="씬 번호")
    narration_script: List[NarrationLine] = Field(description="나레이션 스크립트")
    visuals: List[VisualFrame] = Field(min_length=1, description="비주얼 프레임들")
    tts: TTSSettings = Field(description="TTS 설정")
    timing: TimingInfo = Field(description="타이밍 정보")
    
    # SFX 제거 (실제 사용하지 않음)
    # on_screen_text는 선택사항으로 유지
    on_screen_text: Optional[List[OnScreenTextElement]] = Field(default=None)

class ImageAssetOutput(BaseModel):
    """Image Create Agent 출력 스키마"""
    frame_id: str = Field(description="프레임 식별자")
    image_uri: str = Field(description="이미지 파일 경로")
    generation_metadata: Dict[str, Any] = Field(description="생성 메타데이터")
```

#### **A3: 스키마 변환 유틸리티**
```python
# src/core/schema_converter.py

class PydanticToADKSchema:
    """Pydantic 모델을 ADK 스키마로 변환"""
    
    @staticmethod
    def convert_model_to_schema(model_class: Type[BaseModel]) -> Dict[str, Any]:
        """Pydantic 모델을 ADK input_schema/output_schema 형식으로 변환"""
        
    @staticmethod
    def validate_with_schema(data: Dict[str, Any], model_class: Type[BaseModel]) -> BaseModel:
        """ADK 스키마로 검증 후 Pydantic 모델 반환"""
```

---

### **TASK-B: 에이전트별 스키마 적용**

#### **B1: ADK Full Script Agent 업그레이드**
```python
# src/agents/enhanced_adk_full_script_agent.py

class EnhancedADKFullScriptAgent:
    def __init__(self):
        # Pydantic 모델에서 자동 스키마 생성
        self.input_schema = PydanticToADKSchema.convert_model_to_schema(FullScriptInput)
        self.output_schema = PydanticToADKSchema.convert_model_to_schema(FullScriptOutput)
        self.output_key = "full_script_result"
        
    async def generate_script(self, input_data: FullScriptInput) -> FullScriptOutput:
        # 타입 안전한 입력/출력
```

#### **B2: ADK Scene Script Agent 업그레이드**
```python
# src/agents/enhanced_adk_scene_script_agent.py

class EnhancedADKSceneScriptAgent:
    def __init__(self):
        self.input_schema = PydanticToADKSchema.convert_model_to_schema(SceneExpansionInput)
        self.output_schema = PydanticToADKSchema.convert_model_to_schema(ScenePackageOutput)
        self.output_key = "scene_package_result"
        
    async def expand_scene(self, input_data: SceneExpansionInput) -> ScenePackageOutput:
        # 타입 안전한 입력/출력
```

#### **B3: 다른 에이전트들도 동일한 패턴 적용**
- Image Create Agent
- Voice Generate Agent  
- Video Maker Agent

---

### **TASK-C: 통합 및 테스트**

#### **C1: Enhanced ADK Orchestrator 구현**
```python
# src/agents/enhanced_adk_orchestrator_agent.py

class EnhancedADKOrchestratorAgent:
    """완전한 ADK 패턴을 사용하는 오케스트레이터"""
    
    def __init__(self):
        # 모든 에이전트가 Pydantic 기반 스키마 사용
        self.full_script_agent = EnhancedADKFullScriptAgent()
        self.scene_script_agent = EnhancedADKSceneScriptAgent()
        # ...
        
    async def create_video_package(self, topic: str, **kwargs) -> Dict[str, Any]:
        # 1. 타입 안전한 입력 생성
        full_script_input = FullScriptInput(
            topic=topic,
            length_preference=kwargs.get('length_preference', '60-90s'),
            # ...
        )
        
        # 2. 스키마 기반 안전한 호출
        full_script_result = await self.full_script_agent.generate_script(full_script_input)
        
        # 3. 다음 에이전트에 타입 안전한 전달
        for scene in full_script_result.scenes:
            scene_input = SceneExpansionInput(
                scene_data=scene.model_dump(),
                global_context=context
            )
            scene_result = await self.scene_script_agent.expand_scene(scene_input)
```

---

## 🔧 구현 세부사항

### **1. ADK 패턴 준수**:
```python
# ADK 공식 패턴
agent = LlmAgent(
    model="gemini-2.5-flash",
    name="agent_name",
    description="Agent description",
    instruction="Detailed instructions...",
    input_schema=input_schema,      # ← Pydantic에서 자동 생성
    output_schema=output_schema,    # ← Pydantic에서 자동 생성  
    output_key="result_key"         # ← 세션 상태 저장 키
)
```

### **2. 타입 안전성 강화**:
```python
# 현재 (타입 불안전)
def process_scene(scene_data: Dict[str, Any]) -> Dict[str, Any]:
    # 딕셔너리 키 에러 위험
    scene_number = scene_data['scene_number']  # KeyError 가능
    
# 개선 후 (타입 안전)
def process_scene(scene_input: SceneExpansionInput) -> ScenePackageOutput:
    # 컴파일 타임에 타입 체크
    scene_number = scene_input.scene_data.scene_number  # 타입 안전
```

### **3. 자동 스키마 생성**:
```python
# Pydantic 모델에서 자동으로 ADK 스키마 생성
def pydantic_to_adk_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """Pydantic 모델을 ADK 스키마로 변환"""
    schema = model.model_json_schema()
    
    # ADK 형식으로 변환
    return {
        "type": "object",
        "properties": schema["properties"],
        "required": schema.get("required", []),
        "description": schema.get("description", "")
    }
```

---

## 📅 실행 계획

### **Phase 1 (1일): 스키마 모델 구축**
1. `src/schemas/input_models.py` 생성
2. `src/schemas/output_models.py` 생성  
3. `src/core/schema_converter.py` 생성
4. 기본 테스트 작성

### **Phase 2 (2일): 에이전트 업그레이드**
1. Enhanced ADK Full Script Agent 구현
2. Enhanced ADK Scene Script Agent 구현
3. 다른 에이전트들 순차 업그레이드

### **Phase 3 (1일): 통합 및 테스트**
1. Enhanced ADK Orchestrator 구현
2. 기존 시스템과 호환성 테스트
3. 성능 및 안정성 검증

---

## 🎯 예상 효과

### **개발자 경험 향상**:
- **타입 안전성**: 컴파일 타임 에러 감지
- **자동완성**: IDE에서 완벽한 자동완성 지원
- **문서화**: 스키마가 곧 문서가 됨

### **시스템 안정성 향상**:
- **구조화된 데이터**: ADK가 강제하는 JSON 구조 준수
- **자동 검증**: 입력/출력 데이터 자동 검증
- **에러 감소**: 타입 불일치로 인한 런타임 에러 대폭 감소

### **성능 향상**:
- **최적화된 프롬프트**: ADK의 구조화된 출력으로 더 효율적인 LLM 호출
- **캐싱 가능**: 타입이 명확하므로 결과 캐싱 용이
- **병렬 처리**: 타입 안전한 데이터로 병렬 처리 안전

---

## 🔧 기술적 세부사항

### **1. Pydantic → ADK 스키마 변환**:
```python
from pydantic import BaseModel, Field
from typing import Dict, Any, Type

class FullScriptInput(BaseModel):
    topic: str = Field(min_length=5, description="비디오 주제")
    length_preference: str = Field(description="원하는 길이")

# 자동 변환 결과:
{
    "type": "object",
    "required": ["topic", "length_preference"],
    "properties": {
        "topic": {
            "type": "string", 
            "minLength": 5,
            "description": "비디오 주제"
        },
        "length_preference": {
            "type": "string",
            "description": "원하는 길이"
        }
    }
}
```

### **2. ADK Agent 패턴 적용**:
```python
# 현재 방식 (수동 스키마)
class ADKFullScriptAgent:
    def _load_output_schema(self):
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                # ... 수동으로 모든 필드 정의
            }
        }

# 개선된 방식 (Pydantic 자동 생성)
class EnhancedADKFullScriptAgent:
    def __init__(self):
        self.input_schema = PydanticToADKSchema.convert(FullScriptInput)
        self.output_schema = PydanticToADKSchema.convert(FullScriptOutput)
        self.output_key = "full_script_result"
```

### **3. 타입 안전한 에이전트 호출**:
```python
# 현재 방식 (타입 불안전)
async def generate_script(self, topic: str, length: str, style: str) -> Dict[str, Any]:
    # 매개변수 실수 가능, 반환 타입 불명확

# 개선된 방식 (타입 안전)
async def generate_script(self, input_data: FullScriptInput) -> FullScriptOutput:
    # 타입 안전, 자동완성, 검증
```

---

## 📊 성공 지표

### **완료 후 달성할 목표**:
- ✅ **100% 타입 안전성**: 모든 에이전트 입/출력이 타입 검증됨
- ✅ **ADK 패턴 준수**: 공식 문서의 best practices 적용
- ✅ **자동 스키마 생성**: Pydantic 모델에서 ADK 스키마 자동 생성
- ✅ **런타임 에러 90% 감소**: 타입 불일치 에러 사전 방지
- ✅ **개발 속도 50% 향상**: 자동완성과 타입 체크로 개발 효율성 증대

### **검증 방법**:
- 기존 모든 기능이 정상 동작하는지 테스트
- 타입 체커(mypy)로 타입 안전성 검증
- 성능 벤치마크로 개선 효과 측정
- 개발자 경험 개선 정도 평가

---

## 🚀 즉시 시작

이제 **TASK-A1: 입력 스키마 모델들** 구축부터 시작하겠습니다!

---

*이 계획은 ADK 공식 문서의 best practices를 완전히 준수하여 구현됩니다.*
