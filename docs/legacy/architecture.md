# Architecture

## System Overview

ShortFactory Agent is a **Google ADK (Agent Development Kit)** based modular AI system that creates short educational videos using a consistent character (Huh) with cosplay capabilities. The system features a **2-stage validation system** to ensure high-quality, engaging content.

## 🏗️ ADK Architecture Components

### 1. ADK Agents
- **ADKScriptWriterAgent**: Generates story scripts and scene plans using Gemini 2.5 Flash
- **ADKSceneWriterAgent**: Creates detailed scene scripts with comprehensive educational content
- **ADKScriptValidatorAgent**: Validates story-level quality (fun, interest, uniqueness, educational value)
- **ADKSceneScriptValidatorAgent**: Validates individual scene quality and smooth connections
- **ADKImageGenerateAgent**: Creates character-consistent images using Huh character with Gemini 2.5 Flash Image
- **ADKAudioGenerateAgent**: (Future) Text-to-speech generation
- **ADKVideoGenerateAgent**: (Future) Final video assembly

### 2. ADK Core Components
- **ADK Runner**: Central orchestrator for all agents
- **InMemorySessionService**: Session state management
- **InMemoryArtifactService**: Generated content storage
- **InMemoryMemoryService**: Agent memory and context

### 3. Core Components
- **Models**: Pydantic data structures (StoryScript, Scene, ValidationResult, etc.)
- **Session Manager**: UUID-based file organization and metadata tracking
- **Asset Manager**: Huh character image management
- **Shared Context Manager**: Maintains consistency across agents
- **Story Focus Engine**: Refines broad subjects into specific, engaging stories
- **Scene Continuity Manager**: Ensures smooth transitions between scenes
- **Image Style Selector**: Intelligently selects optimal image styles
- **Educational Enhancer**: Enriches content with educational elements

### 4. 2-Stage Validation System
- **Stage 1 - Script Validation**: Validates overall story quality before scene generation
- **Stage 2 - Scene Validation**: Validates individual scene quality before image generation
- **Feedback Loop**: Automatic revision system with detailed feedback

### 5. ADK Data Flow
```
User Input → ADK Runner → ADKScriptWriterAgent → Story Script → ADKScriptValidatorAgent → 
[PASS] → ADKSceneWriterAgent → Scene Scripts → ADKSceneScriptValidatorAgent → 
[PASS] → ADKImageGenerateAgent → Image Generation → Session Storage → Complete Assets
[REVISE] → Feedback Loop → Re-generation
```

## 🎭 Character System

### Huh Character
- **Base Image**: `src/assets/huh.png`
- **Cosplay System**: Character transforms based on subject
- **Consistency**: Same character appears in all scenes
- **Size**: Character stays small, educational content is primary

### Cosplay Process
1. Load base Huh character
2. Apply cosplay instructions from script
3. Generate cosplayed character image
4. Use cosplayed character for all scene images

## 🔧 Technical Architecture

### ADK AI Integration
- **Script Generation**: Google Gemini 2.5 Flash via ADK
- **Image Generation**: Google Gemini 2.5 Flash Image via ADK
- **Image Editing**: Text-and-image-to-image editing
- **Framework**: Google ADK (Agent Development Kit)
- **API**: Direct API calls within ADK agents

### Session Management
- **UUID-based**: Each session gets unique identifier
- **File Organization**: Structured folders for all content
- **Metadata Tracking**: Progress and file information
- **Logging**: Comprehensive logging for debugging

### Error Handling
- **Fallbacks**: Mock data when AI fails
- **Retry Logic**: Automatic retry for transient failures
- **Logging**: Detailed error logging
- **Graceful Degradation**: System continues with partial results

## 📊 Data Models

### VideoScript
```python
class VideoScript(BaseModel):
    title: str
    main_character_description: str
    character_cosplay_instructions: str  # Cosplay instructions
    overall_style: str
    scenes: List[Scene]
```

### Scene
```python
class Scene(BaseModel):
    scene_number: int
    scene_type: SceneType  # hook, explanation, visual_demo, etc.
    dialogue: str
    voice_tone: VoiceTone
    image_style: ImageStyle
    image_create_prompt: str
    character_pose: Optional[str]        # What character is doing
    background_description: Optional[str] # Educational background
    # ... other fields
```

## 🚀 Workflow

### Current ADK Workflow with 2-Stage Validation
1. **Input**: User provides subject
2. **ADK Runner**: Orchestrates multi-agent workflow
3. **ADKScriptWriterAgent**: Creates story script and scene plan
4. **ADKScriptValidatorAgent**: Validates story quality
   - **PASS**: Continue to scene generation
   - **REVISE**: Return to Script Writer with feedback
5. **ADKSceneWriterAgent**: Creates detailed scene scripts
6. **ADKSceneScriptValidatorAgent**: Validates all scene quality
   - **PASS**: Continue to image generation
   - **REVISE**: Return specific scenes to Scene Writer with feedback
7. **ADKImageGenerateAgent**: Generates educational images with consistent character
8. **Output**: Files saved in session directory

### Future ADK Workflow (Complete)
1. **Input**: User provides subject
2. **ADK Runner**: Orchestrates multi-agent workflow
3. **ADKScriptWriterAgent**: Creates story script and scene plan
4. **ADKScriptValidatorAgent**: Validates story quality
5. **ADKSceneWriterAgent**: Creates detailed scene scripts
6. **ADKSceneScriptValidatorAgent**: Validates all scene quality
7. **ADKImageGenerateAgent**: Generates educational images with consistent character
8. **ADKAudioGenerateAgent**: Generates voice-over for each scene
9. **ADKVideoGenerateAgent**: Combines images and audio into final video
10. **Output**: Complete video file

## 🔍 Validation System Details

### Stage 1: Script Validator Agent
**Purpose**: Validates overall story quality before scene generation

**Validation Criteria**:
- **Fun Factor**: Is the story entertaining and engaging?
- **Interest Level**: Will viewers want to continue watching?
- **Uniqueness**: Is the story angle uncommon and distinctive?
- **Educational Value**: Does it provide meaningful learning content?
- **Narrative Coherence**: Does the story flow logically?

**Output**:
- **PASS**: Story meets quality standards, proceed to scene generation
- **REVISE**: Story needs improvement, return to Script Writer with detailed feedback

### Stage 2: Scene Script Validator Agent
**Purpose**: Validates individual scene quality and smooth connections

**Validation Criteria**:
- **Scene Quality**: Is each scene sufficiently engaging?
- **Visual Potential**: Can the scene be effectively visualized?
- **Educational Density**: Does it contain sufficient learning elements?
- **Character Utilization**: Is the character effectively used?
- **Smooth Connection**: Do scenes flow well together?

**Output**:
- **PASS**: All scenes meet quality standards, proceed to image generation
- **REVISE**: Specific scenes need improvement, return to Scene Writer with feedback

### Feedback Loop System
**Automatic Revision**: Failed validations trigger automatic re-generation with detailed feedback
**State Management**: Tracks revision attempts and prevents infinite loops
**Learning System**: Improves validation criteria based on successful patterns

## 🔒 Security & Reliability

### API Security
- API keys stored in environment variables
- No hardcoded credentials
- Secure API communication

### Error Recovery
- Comprehensive error handling
- Fallback to mock data when needed
- Detailed logging for debugging
- Graceful degradation

### Performance
- Efficient file management
- Optimized API calls
- Rate limiting compliance
- Memory management

## 📈 Scalability

### Current Limitations
- Single session processing
- Sequential image generation
- Local file storage

### Future Improvements
- Concurrent session processing
- Parallel image generation
- Cloud storage integration
- Caching system

## 🛠️ Development Guidelines

### Code Organization
- Modular agent-based architecture
- Clear separation of concerns
- Consistent error handling
- Comprehensive logging

### Testing Strategy
- Unit tests for each agent
- Integration tests for workflows
- Mock data for testing
- Error scenario testing

### Documentation
- Comprehensive code documentation
- API documentation
- User guides
- Development guides