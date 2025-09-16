# Project Overview - ShortFactory Agent

## Mission Statement

Create an AI-powered system that automatically generates engaging short educational videos from any given subject, using a multi-agent approach to ensure high-quality content production.

## Core Features

### 1. Script Writer Agent
- **Purpose**: Transform subjects into compelling video scripts
- **Capabilities**:
  - Story arc structure (Hook → Setup → Development → Climax → Resolution)
  - Scene-by-scene breakdown with detailed descriptions
  - Character consistency and visual direction
  - Voice tone and animation decisions
  - Transition planning between scenes

### 2. Image Generate Agent
- **Purpose**: Create visual content for each scene
- **Capabilities**:
  - Generate images based on detailed prompts
  - Maintain character consistency across scenes
  - Support multiple visual styles (educational, cinematic, cartoon)
  - Handle special effects and overlays

### 3. Video Generate Agent
- **Purpose**: Create animated video sequences
- **Capabilities**:
  - Combine static images with animations
  - Implement scene transitions
  - Add visual effects and motion
  - Synchronize with audio timing

### 4. Audio Generate Agent
- **Purpose**: Generate voice narration and sound effects
- **Capabilities**:
  - Text-to-speech with emotional tones
  - Background music and sound effects
  - Audio synchronization with video
  - Multiple voice options and languages

## Technical Stack

- **Language**: Python
- **AI Framework**: LangChain
- **Google Services**: Google SDK (to be researched and documented)
- **Output Format**: Structured video scripts with Pydantic models
- **Integration**: Multi-agent orchestration

## Target Output

Each video will be:
- 5-8 scenes for optimal pacing
- 30-60 seconds duration
- Educational and engaging content
- Consistent character and visual style
- Professional quality with smooth transitions

## Success Metrics

- [ ] Generate coherent video scripts from any subject
- [ ] Produce visually consistent images across scenes
- [ ] Create smooth video animations and transitions
- [ ] Generate natural-sounding voice narration
- [ ] Complete end-to-end video production pipeline
- [ ] Maintain character consistency throughout videos
- [ ] Support multiple languages and voice tones

## Current Implementation Status

### Completed
- [x] Basic script writer agent structure
- [x] Pydantic models for video script structure
- [x] Dynamic prompt generation system
- [x] Enum-based configuration system

### In Progress
- [ ] Documentation framework
- [ ] Google SDK integration research
- [ ] Agent architecture design

### Planned
- [ ] Image generation agent implementation
- [ ] Video generation agent implementation
- [ ] Audio generation agent implementation
- [ ] End-to-end pipeline integration
- [ ] Testing and quality assurance
- [ ] Deployment and scaling

## Next Steps

1. Complete documentation framework
2. Research and document Google SDK integration
3. Design agent communication architecture
4. Implement remaining agents
5. Create end-to-end testing pipeline
