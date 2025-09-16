# System Architecture - ShortFactory Agent

## Overview

ShortFactory Agent follows a multi-agent architecture where four specialized agents work together to create short educational videos. Each agent has specific responsibilities and communicates through well-defined interfaces.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    ShortFactory Orchestrator                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Google ADK Orchestration                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Communication                      │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Script    │───▶│   Image     │───▶│   Video     │         │
│  │   Writer    │    │  Generator  │    │  Generator  │         │
│  │   Agent     │    │   Agent     │    │   Agent     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │               │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Audio     │◀───│   Shared    │───▶│   Final     │         │
│  │  Generator  │    │   Assets    │    │   Video     │         │
│  │   Agent     │    │   Storage   │    │  Assembly   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Responsibilities

### 1. Script Writer Agent

**Primary Role**: Master story creator and video director

**Responsibilities**:
- Transform subjects into compelling video scripts
- Design story arc structure (Hook → Setup → Development → Climax → Resolution)
- Create detailed scene descriptions with visual and audio direction
- Specify character consistency and visual styles
- Plan transitions and animation requirements
- Generate voice tone and dialogue specifications

**Input**:
```python
{
    "subject": str,           # Topic for the video
    "language": str,          # Target language (e.g., "Korean", "English")
    "max_video_scenes": int   # Maximum number of scenes (5-8 recommended)
}
```

**Output**:
```python
VideoScript {
    title: str,
    main_character_description: str,
    overall_style: str,
    scenes: List[Scene] {
        scene_type: SceneType,
        image_style: ImageStyle,
        image_create_prompt: str,
        dialogue: str,
        voice_tone: VoiceTone,
        needs_animation: bool,
        video_prompt: Optional[str],
        transition_type: TransitionType,
        hook_technique: Optional[HookTechnique]  # Only for first scene
    }
}
```

**Integration Points**:
- Uses Google ADK for AI model access
- Outputs structured data for other agents
- Coordinates with image agent for visual consistency

### 2. Image Generate Agent

**Primary Role**: Visual content creator

**Responsibilities**:
- Generate images based on script descriptions
- Maintain character consistency across all scenes
- Apply appropriate visual styles (educational, cinematic, cartoon)
- Create special effects and overlays
- Optimize images for video composition
- Handle different image formats and resolutions

**Input**:
```python
{
    "script": VideoScript,
    "scene_index": int,
    "character_reference": str,  # For consistency
    "style_requirements": ImageStyle
}
```

**Output**:
```python
{
    "image_path": str,
    "image_metadata": {
        "style": ImageStyle,
        "character_consistency": bool,
        "resolution": tuple,
        "format": str
    }
}
```

**Integration Points**:
- Receives detailed prompts from script writer
- Provides images to video generator
- Maintains character consistency database
- Uses Google Vision API for quality validation

### 3. Video Generate Agent

**Primary Role**: Animation and video composition specialist

**Responsibilities**:
- Combine static images with animations
- Implement scene transitions
- Add visual effects and motion
- Synchronize timing with audio
- Create smooth video sequences
- Optimize for different platforms

**Input**:
```python
{
    "script": VideoScript,
    "images": List[ImageData],
    "animation_requirements": List[AnimationSpec],
    "transition_specs": List[TransitionSpec]
}
```

**Output**:
```python
{
    "video_path": str,
    "video_metadata": {
        "duration": float,
        "resolution": tuple,
        "fps": int,
        "format": str,
        "file_size": int
    }
}
```

**Integration Points**:
- Receives images from image generator
- Coordinates timing with audio agent
- Uses Google Video Intelligence API
- Outputs final video for assembly

### 4. Audio Generate Agent

**Primary Role**: Voice and sound production specialist

**Responsibilities**:
- Generate voice narration from script dialogue
- Apply emotional tones and voice characteristics
- Create background music and sound effects
- Synchronize audio with video timing
- Handle multiple languages and accents
- Optimize audio quality and compression

**Input**:
```python
{
    "script": VideoScript,
    "voice_requirements": {
        "tone": VoiceTone,
        "language": str,
        "speed": float,
        "pitch": float
    }
}
```

**Output**:
```python
{
    "audio_path": str,
    "audio_metadata": {
        "duration": float,
        "format": str,
        "sample_rate": int,
        "channels": int,
        "voice_tone": VoiceTone
    }
}
```

**Integration Points**:
- Receives dialogue and tone from script writer
- Coordinates timing with video generator
- Uses Google Text-to-Speech API
- Provides final audio for video assembly

## Data Flow

### 1. Initial Request Processing
```
User Input → Orchestrator → Script Writer Agent
```

### 2. Script Generation
```
Script Writer Agent → VideoScript Object → Shared Storage
```

### 3. Parallel Asset Generation
```
VideoScript → Image Agent (parallel) → Image Assets
VideoScript → Audio Agent (parallel) → Audio Assets
```

### 4. Video Assembly
```
Image Assets + Audio Assets → Video Agent → Final Video
```

### 5. Quality Assurance
```
Final Video → Quality Check → User Output
```

## Communication Patterns

### Synchronous Communication
- **Script Generation**: Must complete before other agents start
- **Quality Validation**: Final step before delivery

### Asynchronous Communication
- **Asset Generation**: Image and audio generation can run in parallel
- **Background Processing**: Non-critical tasks can be queued

### Event-Driven Communication
- **Progress Updates**: Agents notify orchestrator of completion
- **Error Handling**: Failures trigger retry or fallback mechanisms

## Error Handling and Resilience

### Agent-Level Error Handling
```python
class AgentError(Exception):
    """Base exception for agent errors"""
    pass

class ScriptGenerationError(AgentError):
    """Script writer specific errors"""
    pass

class ImageGenerationError(AgentError):
    """Image generator specific errors"""
    pass
```

### Orchestration-Level Error Handling
- **Retry Logic**: Failed agents can retry with different parameters
- **Fallback Mechanisms**: Alternative approaches for critical failures
- **Graceful Degradation**: Partial results when full pipeline fails

### Monitoring and Logging
```python
# Each agent logs its activities
logger.info(f"Agent {self.name} started processing {request_id}")
logger.info(f"Agent {self.name} completed processing {request_id}")
logger.error(f"Agent {self.name} failed: {error_message}")
```

## Scalability Considerations

### Horizontal Scaling
- Each agent can be deployed as separate microservices
- Multiple instances of each agent can handle concurrent requests
- Load balancing across agent instances

### Vertical Scaling
- Individual agents can be optimized for specific workloads
- Resource allocation based on agent requirements
- Caching strategies for frequently used assets

### Performance Optimization
- **Caching**: Store frequently generated assets
- **Preprocessing**: Prepare common elements in advance
- **Batch Processing**: Handle multiple requests efficiently

## Security and Privacy

### Data Protection
- **Input Validation**: Sanitize all user inputs
- **Output Filtering**: Ensure generated content is appropriate
- **Data Retention**: Clear temporary files and sensitive data

### API Security
- **Authentication**: Secure access to Google APIs
- **Rate Limiting**: Prevent abuse of external services
- **Monitoring**: Track usage and detect anomalies

## Deployment Architecture

### Development Environment
```
Local Development → Docker Containers → Local Testing
```

### Production Environment
```
Load Balancer → Kubernetes Cluster → Google Cloud Services
```

### Monitoring and Observability
- **Metrics**: Performance, error rates, resource usage
- **Logging**: Structured logging across all agents
- **Tracing**: End-to-end request tracking
- **Alerting**: Proactive issue detection

## Future Extensibility

### Plugin Architecture
- **Custom Agents**: Easy addition of new agent types
- **Tool Integration**: Flexible tool and service integration
- **Format Support**: Extensible output format support

### AI Model Flexibility
- **Model Agnostic**: Support for different AI models
- **Fine-tuning**: Custom model training capabilities
- **A/B Testing**: Compare different model approaches

This architecture provides a solid foundation for the ShortFactory Agent system while maintaining flexibility for future enhancements and scaling.
