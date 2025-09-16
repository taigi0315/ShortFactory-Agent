# ShortFactory Agent - ADK 이해 가이드 (한국어)

## 🎯 ADK란 무엇인가요?

**ADK (Agent Development Kit)**는 Google에서 제공하는 AI 에이전트 개발 프레임워크입니다. 여러 AI 에이전트들이 협력해서 복잡한 작업을 수행할 수 있도록 도와주는 도구입니다.

### 🤔 왜 ADK를 사용하나요?

**이전 방식 (직접 API 호출)**:
```python
# 각 에이전트가 개별적으로 API를 호출
client = genai.Client(api_key=api_key)
response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt])
```

**ADK 방식**:
```python
# ADK가 에이전트들을 관리하고 조율
class ADKScriptWriterAgent(Agent):
    async def generate_script(self, subject: str) -> VideoScript:
        response = await self.generate_content(prompt)  # ADK가 API 호출 관리
```

## 🏗️ ADK 아키텍처 이해

### 1. ADK의 핵심 구성요소

```
┌─────────────────────────────────────────────────────────────┐
│                    ADK 시스템 구조                           │
├─────────────────────────────────────────────────────────────┤
│  ADK Runner (중앙 관리자)                                    │
│  ├── 세션 관리 (Session Service)                            │
│  ├── 아티팩트 저장 (Artifact Service)                       │
│  └── 메모리 관리 (Memory Service)                           │
├─────────────────────────────────────────────────────────────┤
│  ADK Agents (작업 수행자들)                                  │
│  ├── ADKScriptWriterAgent (스크립트 생성)                   │
│  ├── ADKImageGenerateAgent (이미지 생성)                    │
│  ├── ADKAudioGenerateAgent (오디오 생성) - 미래              │
│  └── ADKVideoGenerateAgent (비디오 생성) - 미래              │
└─────────────────────────────────────────────────────────────┘
```

### 2. ADK 에이전트의 기본 구조

```python
from google.adk.agents import Agent

class ADKScriptWriterAgent(Agent):
    def __init__(self):
        super().__init__(
            name="script_writer",           # 에이전트 이름
            description="스크립트 생성",     # 에이전트 설명
            model="gemini-2.5-flash",       # 사용할 AI 모델
            instruction=self._get_instruction(),  # 에이전트 지시사항
            tools=[],                       # 사용할 도구들
            generate_content_config={       # 생성 설정
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
```

## 🔄 ADK 워크플로우 이해

### 1. 전체 워크플로우 다이어그램

```mermaid
graph TD
    A[사용자 입력: "K-pop이 뭐야?"] --> B[ADK Runner 시작]
    B --> C[세션 생성]
    C --> D[ADKScriptWriterAgent 호출]
    D --> E[스크립트 생성]
    E --> F[ADKImageGenerateAgent 호출]
    F --> G[코스플레이 이미지 생성]
    G --> H[씬 이미지들 생성]
    H --> I[결과 저장]
    I --> J[완료]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style D fill:#fff3e0
    style F fill:#fff3e0
    style J fill:#e8f5e8
```

### 2. 단계별 상세 설명

#### **1단계: 사용자 입력**
```python
# 사용자가 주제를 입력
subject = "K-pop이 뭐야?"
```

#### **2단계: ADK Runner 초기화**
```python
class ADKShortFactoryRunner:
    def __init__(self):
        # ADK 서비스들 초기화
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        self.memory_service = InMemoryMemoryService()
        
        # ADK 에이전트들 생성
        self.script_writer_agent = ADKScriptWriterAgent()
        self.image_generate_agent = ADKImageGenerateAgent(self.session_manager)
        
        # ADK Runner 생성
        self.runner = Runner(
            app_name="shortfactory",
            agent=self.script_writer_agent,  # 주 에이전트
            session_service=self.session_service,
            artifact_service=self.artifact_service,
            memory_service=self.memory_service
        )
```

#### **3단계: 스크립트 생성**
```python
# ADKScriptWriterAgent가 스크립트 생성
script = await self.script_writer_agent.generate_script(
    subject="K-pop이 뭐야?",
    language="Korean",
    max_video_scenes=6
)
```

#### **4단계: 이미지 생성**
```python
# ADKImageGenerateAgent가 이미지들 생성
image_results = await self.image_generate_agent.generate_images_for_session(
    session_id=session_id,
    script=script
)
```

## 🎭 ADK 에이전트 상세 분석

### 1. ADKScriptWriterAgent (스크립트 생성 에이전트)

```python
class ADKScriptWriterAgent(Agent):
    def __init__(self):
        super().__init__(
            name="script_writer",
            description="교육용 비디오 스크립트를 생성합니다",
            model="gemini-2.5-flash",
            instruction=self._get_instruction(),
            tools=[],
            generate_content_config={
                "temperature": 0.7,  # 창의성 수준
                "top_p": 0.8,       # 다양성 수준
                "top_k": 40,        # 선택 범위
                "max_output_tokens": 8192,  # 최대 토큰 수
            }
        )
    
    def _get_instruction(self) -> str:
        return """
        당신은 교육용 비디오 스크립트를 생성하는 전문가입니다.
        
        요구사항:
        - 6-8개의 씬으로 구성
        - 각 씬은 8초 길이
        - Huh 캐릭터 사용
        - 코스플레이 지시사항 포함
        - 교육적이고 재미있는 내용
        """
    
    async def generate_script(self, subject: str, language: str = "Korean", max_video_scenes: int = 8) -> VideoScript:
        # ADK의 generate_content 메서드 사용
        response = await self.generate_content(prompt)
        
        # 응답을 VideoScript 객체로 변환
        script_data = json.loads(response.text)
        script = VideoScript(**script_data)
        
        return script
```

### 2. ADKImageGenerateAgent (이미지 생성 에이전트)

```python
class ADKImageGenerateAgent(Agent):
    def __init__(self, session_manager: SessionManager):
        super().__init__(
            name="image_generator",
            description="Huh 캐릭터를 사용한 이미지를 생성합니다",
            model="gemini-2.5-flash-image-preview",  # 이미지 생성 모델
            instruction=self._get_instruction(),
            tools=[image_tool],
            generate_content_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
    
    async def generate_images_for_session(self, session_id: str, script: VideoScript) -> Dict[str, Any]:
        results = {
            "generated_images": [],
            "total_images": 0,
            "failed_images": 0,
            "time_taken": 0,
            "model_used": "Gemini 2.5 Flash Image",
            "character": "Huh"
        }
        
        start_time = time.time()
        
        # 각 씬에 대해 이미지 생성
        for scene in script.scenes:
            try:
                # 코스플레이 이미지 생성
                cosplayed_huh_image = await self._create_cosplayed_huh(
                    script.character_cosplay_instructions
                )
                
                # 씬 이미지 생성
                image_data = await self._generate_scene_with_huh(
                    cosplayed_huh_image, 
                    scene.image_create_prompt
                )
                
                # 이미지 저장
                image_path = self.session_manager.save_image(
                    session_id=session_id,
                    scene_number=scene.scene_number,
                    image_data=image_data,
                    format="png"
                )
                
                results["generated_images"].append(str(image_path))
                results["total_images"] += 1
                
            except Exception as e:
                logger.error(f"이미지 생성 실패: {str(e)}")
                results["failed_images"] += 1
        
        results["time_taken"] = time.time() - start_time
        return results
```

## 🔧 ADK의 핵심 기능들

### 1. 세션 관리 (Session Management)

```python
# ADK가 자동으로 세션을 관리
session_service = InMemorySessionService()

# 세션 생성
session_id = session_service.create_session()

# 세션 상태 추적
session_state = session_service.get_session(session_id)

# 세션 종료
session_service.close_session(session_id)
```

### 2. 아티팩트 저장 (Artifact Storage)

```python
# 생성된 결과물들을 자동으로 저장
artifact_service = InMemoryArtifactService()

# 스크립트 저장
artifact_service.store_artifact(
    session_id=session_id,
    artifact_type="script",
    content=script_data
)

# 이미지 저장
artifact_service.store_artifact(
    session_id=session_id,
    artifact_type="image",
    content=image_data
)
```

### 3. 메모리 관리 (Memory Management)

```python
# 에이전트들이 이전 작업을 기억할 수 있도록 도움
memory_service = InMemoryMemoryService()

# 메모리 저장
memory_service.store_memory(
    session_id=session_id,
    key="previous_script",
    value=script_data
)

# 메모리 조회
previous_script = memory_service.get_memory(
    session_id=session_id,
    key="previous_script"
)
```

## 🚀 ADK의 장점들

### 1. **자동화된 관리**
- API 호출 자동 관리
- 에러 처리 자동화
- 재시도 로직 내장

### 2. **에이전트 간 협력**
- 여러 에이전트가 순차적으로 작업 수행
- 결과물을 다음 에이전트에게 전달
- 상태 공유 및 동기화

### 3. **확장성**
- 새로운 에이전트 쉽게 추가
- 기존 에이전트 수정 용이
- 모듈화된 구조

### 4. **디버깅 및 모니터링**
- 상세한 로깅
- 작업 진행 상황 추적
- 에러 발생 시점 파악

## 📊 ADK vs 직접 API 호출 비교

| 기능 | 직접 API 호출 | ADK |
|------|---------------|-----|
| **코드 복잡도** | 높음 | 낮음 |
| **에러 처리** | 수동 구현 | 자동 처리 |
| **에이전트 협력** | 수동 구현 | 자동 관리 |
| **세션 관리** | 수동 구현 | 자동 관리 |
| **확장성** | 어려움 | 쉬움 |
| **디버깅** | 어려움 | 쉬움 |
| **유지보수** | 어려움 | 쉬움 |

## 🎯 실제 사용 예시

### 1. 간단한 ADK 에이전트 생성

```python
from google.adk.agents import Agent

class SimpleADKAgent(Agent):
    def __init__(self):
        super().__init__(
            name="simple_agent",
            description="간단한 작업을 수행하는 에이전트",
            model="gemini-2.5-flash",
            instruction="사용자의 요청을 정확히 수행하세요.",
            tools=[],
            generate_content_config={
                "temperature": 0.5,
                "max_output_tokens": 1000,
            }
        )
    
    async def process_request(self, request: str) -> str:
        # ADK의 generate_content 메서드 사용
        response = await self.generate_content(request)
        return response.text
```

### 2. ADK 에이전트 사용

```python
# 에이전트 생성
agent = SimpleADKAgent()

# 요청 처리
result = await agent.process_request("안녕하세요!")
print(result)  # "안녕하세요! 무엇을 도와드릴까요?"
```

## 🔍 ADK 디버깅 팁

### 1. 로그 확인
```python
import logging

# 로그 레벨 설정
logging.basicConfig(level=logging.DEBUG)

# ADK 에이전트 로그 확인
logger = logging.getLogger("agents.adk_script_writer_agent")
logger.debug("스크립트 생성 시작")
```

### 2. 세션 상태 확인
```python
# 세션 정보 확인
session_info = session_service.get_session(session_id)
print(f"세션 상태: {session_info.status}")
print(f"생성된 아티팩트: {session_info.artifacts}")
```

### 3. 에러 처리
```python
try:
    result = await agent.generate_content(prompt)
except Exception as e:
    logger.error(f"ADK 에이전트 에러: {str(e)}")
    # 폴백 처리
    result = fallback_method()
```

## 🎓 ADK 학습 단계

### 1단계: 기본 이해
- [ ] ADK의 개념 이해
- [ ] 에이전트 기본 구조 파악
- [ ] 간단한 에이전트 생성

### 2단계: 실습
- [ ] 기존 ADKScriptWriterAgent 코드 분석
- [ ] ADKImageGenerateAgent 코드 분석
- [ ] 간단한 테스트 에이전트 생성

### 3단계: 고급 활용
- [ ] 새로운 ADK 에이전트 생성
- [ ] 에이전트 간 데이터 전달
- [ ] 복잡한 워크플로우 구현

## 📚 추가 학습 자료

### 1. 공식 문서
- [Google ADK 공식 문서](https://ai.google.dev/adk)
- [ADK 에이전트 가이드](https://ai.google.dev/adk/agents)
- [ADK 예제 코드](https://github.com/google/adk-examples)

### 2. 프로젝트 내 문서
- `docs/ADK-ARCHITECTURE.md` - 상세한 아키텍처 설명
- `docs/ADK-MIGRATION-PLAN.md` - 마이그레이션 계획
- `src/agents/adk_*_agent.py` - 실제 구현 코드

### 3. 실습 방법
```bash
# 프로젝트 실행
python run_adk.py

# 로그 확인
tail -f sessions/[session-id]/logs/session.log

# 생성된 결과 확인
ls -la sessions/[session-id]/
```

## 🎯 요약

ADK는 **AI 에이전트들을 관리하고 조율하는 프레임워크**입니다. 

**핵심 개념**:
1. **에이전트**: 특정 작업을 수행하는 AI 모듈
2. **Runner**: 에이전트들을 관리하는 중앙 관리자
3. **세션**: 작업 단위를 관리하는 컨테이너
4. **아티팩트**: 생성된 결과물들

**장점**:
- 코드가 간단해짐
- 에러 처리가 자동화됨
- 에이전트 간 협력이 쉬워짐
- 확장성이 좋아짐

**이 프로젝트에서의 역할**:
- 스크립트 생성 에이전트
- 이미지 생성 에이전트
- 향후 오디오/비디오 생성 에이전트들

ADK를 사용하면 복잡한 AI 워크플로우를 훨씬 쉽게 관리할 수 있습니다! 🚀

---

**작성일**: 2024년 9월  
**버전**: 1.0  
**대상**: ADK 초보자  
**언어**: 한국어
