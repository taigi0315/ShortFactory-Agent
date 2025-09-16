# Architecture

## System Overview

ShortFactory Agent is a **Google ADK (Agent Development Kit)** based modular AI system that creates short educational videos using a consistent character (Huh) with cosplay capabilities.

## 🏗️ ADK Architecture Components

### 1. ADK Agents
- **ADKScriptWriterAgent**: Generates 8-scene educational scripts with cosplay instructions using Gemini 2.5 Flash
- **ADKImageGenerateAgent**: Creates character-consistent images using Huh character with Gemini 2.5 Flash Image
- **ADKAudioGenerateAgent**: (Future) Text-to-speech generation
- **ADKVideoGenerateAgent**: (Future) Final video assembly

### 2. ADK Core Components
- **ADK Runner**: Central orchestrator for all agents
- **InMemorySessionService**: Session state management
- **InMemoryArtifactService**: Generated content storage
- **InMemoryMemoryService**: Agent memory and context

### 3. Core Components
- **Models**: Pydantic data structures (VideoScript, Scene, etc.)
- **Session Manager**: UUID-based file organization and metadata tracking
- **Asset Manager**: Huh character image management

### 4. ADK Data Flow
```
User Input → ADK Runner → ADKScriptWriterAgent → Script Generation → ADKImageGenerateAgent → Cosplay Generation → Scene Image Generation → Session Storage → Complete Assets
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

### Current ADK Workflow (Phase 2)
1. **Input**: User provides subject
2. **ADK Runner**: Orchestrates multi-agent workflow
3. **ADKScriptWriterAgent**: Creates 8-scene script with cosplay
4. **ADKImageGenerateAgent**: Cosplays Huh character
5. **ADKImageGenerateAgent**: Generates 8 educational images with consistent character
6. **Output**: Files saved in session directory

### Future ADK Workflow (Complete)
1. **Input**: User provides subject
2. **ADK Runner**: Orchestrates multi-agent workflow
3. **ADKScriptWriterAgent**: Creates 8-scene script with cosplay
4. **ADKImageGenerateAgent**: Cosplays Huh character and generates images
5. **ADKAudioGenerateAgent**: Generates voice-over for each scene
6. **ADKVideoGenerateAgent**: Combines images and audio into final video
7. **Output**: Complete video file

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