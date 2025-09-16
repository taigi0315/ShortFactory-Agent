# Architecture

## System Overview

ShortFactory Agent is a modular AI system that creates short educational videos using a consistent character (Huh) with cosplay capabilities.

## 🏗️ Architecture Components

### 1. AI Agents
- **Script Writer Agent**: Generates 8-scene educational scripts with cosplay instructions
- **Huh Image Agent**: Creates character-consistent images using Huh character
- **Audio Agent**: (Future) Text-to-speech generation
- **Video Agent**: (Future) Final video assembly

### 2. Core Components
- **Models**: Pydantic data structures (VideoScript, Scene, etc.)
- **Session Manager**: UUID-based file organization and metadata tracking
- **Asset Manager**: Huh character image management

### 3. Data Flow
```
Subject Input → Script Generation → Character Cosplay → Image Generation → Audio Generation → Video Assembly
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

### AI Integration
- **Script Generation**: Google Gemini 2.0 Flash
- **Image Generation**: Google Flash 2.5 (Nano Banana)
- **Image Editing**: Text-and-image-to-image editing
- **API**: `google-generativeai` SDK

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

### Current Workflow (Phase 2)
1. **Input**: User provides subject
2. **Script Generation**: AI creates 8-scene script with cosplay
3. **Character Creation**: Huh character is cosplayed
4. **Image Generation**: 8 educational images with consistent character
5. **Output**: Files saved in session directory

### Future Workflow (Complete)
1. **Input**: User provides subject
2. **Script Generation**: AI creates 8-scene script with cosplay
3. **Character Creation**: Huh character is cosplayed
4. **Image Generation**: 8 educational images with consistent character
5. **Audio Generation**: Voice-over for each scene
6. **Video Assembly**: Combine images and audio into final video
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