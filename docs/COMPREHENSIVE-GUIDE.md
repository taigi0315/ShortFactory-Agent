# ShortFactory Agent - Comprehensive Guide

## 🎯 Project Overview

**ShortFactory Agent** is a **Google ADK (Agent Development Kit)** based AI-powered system that creates short educational videos using a consistent character (Huh) with cosplay capabilities. The system generates scripts, creates character-consistent images, and will eventually produce audio and video content.

### 🎬 Current Status: **Phase 2 Complete with ADK** ✅
- ✅ ADK Script Generation (with cosplay instructions)
- ✅ ADK Image Generation (Huh character with cosplay)
- ✅ Actual Gemini 2.5 Flash Image API integration
- ⏳ ADK Audio Generation (Next Phase)
- ⏳ ADK Video Generation (Final Phase)

### 🎭 Key Features
- **Huh Character**: Consistent character across all videos
- **Cosplay System**: Character transforms based on subject
- **Educational Focus**: Character stays small, content is primary
- **Session Management**: UUID-based file organization
- **Error Handling**: Robust fallbacks and comprehensive logging

---

## 📁 Project Structure

```
ShortFactory-Agent/
├── run_adk.py                      # ADK Main entry point (use this to run)
├── src/                            # Source code
│   ├── main_adk.py                 # ADK Main program logic
│   ├── agents/                     # ADK Agents
│   │   ├── adk_script_writer_agent.py  # ADK Script generation with cosplay
│   │   └── adk_image_generate_agent.py # ADK Image generation with Huh character
│   ├── core/                       # Core functionality
│   │   └── session_manager.py      # Session and file management
│   ├── model/                      # Data models
│   │   └── models.py               # Pydantic data models
│   ├── assets/                     # Static assets
│   │   └── huh.png                 # Main character image
│   └── utils/                      # Utility functions
├── docs/                           # Documentation
│   ├── ADK-ARCHITECTURE.md         # ADK Architecture guide
│   ├── ADK-MIGRATION-PLAN.md       # ADK Migration plan
│   └── ...                         # Other documentation
├── sessions/                       # Generated content (UUID-based)
│   └── [session-id]/
│       ├── script.json             # Generated script
│       ├── images/                 # Generated images
│       │   └── scene_1.png
│       ├── prompts/                # Saved prompts for debugging
│       │   ├── image/
│       │   └── video/
│       ├── audios/                 # Future: Generated audio
│       ├── videos/                 # Future: Generated video
│       └── metadata.json           # Session metadata
└── tests/                          # Test files
```

---

## 🚀 How to Run

### Prerequisites
1. **Python 3.8+**
2. **Google API Key** (set in `.env` file):
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

### Quick Start
```bash
# Run the ADK main program
python run_adk.py

# Or directly
python src/main_adk.py
```

### What Happens
1. **Input**: You provide a subject (e.g., "What is Python?")
2. **ADK Runner**: Orchestrates multi-agent workflow
3. **ADKScriptWriterAgent**: Creates 8-scene script with cosplay instructions
4. **ADKImageGenerateAgent**: Cosplays Huh character based on script
5. **ADKImageGenerateAgent**: Creates 8 educational images with Huh character
6. **Output**: All files saved in `sessions/[uuid]/` directory

---

## 🤖 AI Agents

### 1. ADK Script Writer Agent (`adk_script_writer_agent.py`)
**Purpose**: Generates comprehensive video scripts with cosplay instructions using ADK

**Features**:
- Uses Google Gemini 2.5 Flash via ADK
- Creates 8 educational scenes
- Includes character cosplay instructions
- Generates detailed image prompts
- Specifies character poses and backgrounds
- Built-in error handling and fallbacks

**Output**: `VideoScript` object with:
- `title`: Video title
- `main_character_description`: Character description
- `character_cosplay_instructions`: How to dress the character
- `scenes[]`: Array of 8 scenes with dialogue, poses, backgrounds

### 2. ADK Image Generate Agent (`adk_image_generate_agent.py`)
**Purpose**: Generates character-consistent images using Huh character with ADK

**Features**:
- Uses Google Gemini 2.5 Flash Image via ADK
- Loads Huh character from `assets/huh.png`
- Applies cosplay transformations using actual API
- Creates educational, meaningful images
- Character stays small in images (not dominating)
- Actual image generation (not mock)

**Process**:
1. **Step 1**: Create cosplayed Huh character using Gemini 2.5 Flash Image
2. **Step 2**: Generate scene images using cosplayed Huh + scene info

**Output**: PNG images in `sessions/[uuid]/images/scene_X.png`

---

## 📊 Data Models

### VideoScript Model
```python
class VideoScript(BaseModel):
    title: str
    main_character_description: str
    character_cosplay_instructions: str  # NEW: Cosplay instructions
    overall_style: str
    scenes: List[Scene]
```

### Scene Model
```python
class Scene(BaseModel):
    scene_number: int
    scene_type: SceneType  # hook, explanation, visual_demo, etc.
    dialogue: str
    voice_tone: VoiceTone
    image_style: ImageStyle
    image_create_prompt: str
    character_pose: Optional[str]        # NEW: What character is doing
    background_description: Optional[str] # NEW: Educational background
    # ... other fields
```

---

## 🎭 Character System

### Huh Character
- **Base Image**: `assets/huh.png`
- **Cosplay System**: Character can be dressed/transformed based on subject
- **Consistency**: Same character appears in all scenes
- **Size**: Character stays small in images (educational focus)

### Cosplay Examples
- **Tech Topic**: "Dress as a programmer with glasses and hoodie"
- **Science Topic**: "Wear a lab coat and safety glasses"
- **History Topic**: "Dress in period-appropriate clothing"

---

## 🔧 Technical Details

### Google ADK Integration
- **Script Generation**: Gemini 2.5 Flash via ADK
- **Image Generation**: Gemini 2.5 Flash Image via ADK
- **Image Editing**: Text-and-image-to-image editing
- **Framework**: Google ADK (Agent Development Kit)
- **API**: Direct API calls within ADK agents

### Session Management
- **UUID-based**: Each session gets unique identifier
- **File Organization**: Structured folders for all content
- **Metadata Tracking**: Progress and file information
- **Logging**: Comprehensive logging for debugging

### Image Generation Process
1. **Load Huh**: Read `assets/huh.png`
2. **Apply Cosplay**: Transform Huh based on script instructions
3. **Generate Scenes**: Use cosplayed Huh + scene information
4. **Save Images**: Store in session directory

---

## 📈 Current Capabilities

### ✅ Working Features
1. **ADK Script Generation**: 8-scene educational scripts via ADK
2. **ADK Character Cosplay**: Huh character transformation via ADK
3. **ADK Image Generation**: Character-consistent educational images via ADK
4. **Actual API Integration**: Real Gemini 2.5 Flash Image API usage
5. **Session Management**: UUID-based file organization
6. **Comprehensive Logging**: Full process tracking

### 🎯 Image Quality Features
- **Character Consistency**: Same Huh character in all scenes
- **Educational Focus**: Images support learning content
- **Character Size**: Huh stays small, content is primary
- **Scene Information**: Uses character_pose and background_description
- **Meaningful Content**: Not just decorative, but educational

---

## 🚧 Next Development Phases

### Phase 3: ADK Audio Generation (Next)
**Goal**: Generate voice-over audio for each scene using ADK

**Requirements**:
- ADK-based text-to-speech integration
- Voice tone matching (excited, calm, etc.)
- Audio file generation (WAV/MP3)
- Sync with scene dialogue

**Implementation Plan**:
1. Create `ADKAudioGenerateAgent` class
2. Integrate with ElevenLabs or similar TTS service
3. Use `voice_tone` and `elevenlabs_settings` from scenes
4. Generate audio files in `sessions/[uuid]/audios/`

### Phase 4: ADK Video Generation (Final)
**Goal**: Combine images and audio into final video using ADK

**Requirements**:
- ADK-based image-to-video generation
- Audio synchronization
- Transition effects
- Final video output (MP4)

**Implementation Plan**:
1. Create `ADKVideoGenerateAgent` class
2. Integrate with video generation service
3. Combine images + audio + transitions
4. Generate final video in `sessions/[uuid]/videos/`

---

## 🛠️ Development Guidelines

### File Creation Rules
1. **Follow Structure**: Use `src/agents/`, `src/core/`, `src/utils/`
2. **Documentation**: Update docs for every change
3. **Testing**: Create test files in `tests/`
4. **Logging**: Use comprehensive logging
5. **Error Handling**: Robust error handling with fallbacks

### Code Standards
- **Python 3.8+**: Use modern Python features
- **Type Hints**: Use Pydantic models and type hints
- **Error Handling**: Try-catch with meaningful messages
- **Logging**: Use Python logging module
- **Documentation**: Docstrings for all functions

### Import Structure
```python
# For agents in src/agents/
from ..models.models import VideoScript
from ..core.session_manager import SessionManager

# For main program
from session_manager import SessionManager
from script_writer_agent import ScriptWriterAgent
from huh_image_agent import HuhImageAgent
```

---

## 🐛 Troubleshooting

### Common Issues
1. **API Key Error**: Check `.env` file has `GEMINI_API_KEY`
2. **Import Errors**: Ensure Python path includes `src/`
3. **Image Generation Fails**: Check API quota and network
4. **Character Not Loading**: Verify `assets/huh.png` exists

### Debug Mode
- Check logs in `sessions/[uuid]/logs/session.log`
- Use `logging.getLogger().setLevel(logging.DEBUG)`
- Verify API responses in console output

---

## 📚 API Reference

### ADK Script Writer Agent
```python
from agents.adk_script_writer_agent import ADKScriptWriterAgent

agent = ADKScriptWriterAgent()
script = await agent.generate_script(
    subject="Your topic here",
    language="English",
    max_video_scenes=8
)
```

### ADK Image Generate Agent
```python
from agents.adk_image_generate_agent import ADKImageGenerateAgent
from core.session_manager import SessionManager

session_manager = SessionManager()
image_agent = ADKImageGenerateAgent(session_manager)
results = await image_agent.generate_images_for_session(session_id, script)
```

### Session Manager
```python
from core.session_manager import SessionManager

session_manager = SessionManager()
session_id = session_manager.create_session(subject, language)
script_path = session_manager.save_script(session_id, script)
```

---

## 🎯 Success Metrics

### Current Achievements
- ✅ **ADK Script Quality**: 8-scene educational scripts with cosplay via ADK
- ✅ **ADK Character Consistency**: Huh character appears in all images via ADK
- ✅ **ADK Image Quality**: Educational, meaningful images via ADK
- ✅ **Actual API Integration**: Real Gemini 2.5 Flash Image API usage
- ✅ **System Reliability**: Robust error handling and logging
- ✅ **File Organization**: Clean UUID-based session structure

### Future Goals
- 🎯 **Audio Quality**: Natural-sounding voice-over
- 🎯 **Video Quality**: Smooth, professional video output
- 🎯 **Performance**: Faster generation times
- 🎯 **Scalability**: Handle multiple concurrent sessions

---

## 📞 Support

### For Next Developer
This document provides complete context for continuing development. Key points:

1. **Current State**: Script + Image generation working with Huh character
2. **Next Phase**: Audio generation using scene dialogue and voice settings
3. **Architecture**: Modular agent-based system with session management
4. **Character System**: Huh character with cosplay capabilities
5. **File Structure**: Organized, documented, and ready for extension

### Key Files to Understand
- `src/agents/adk_script_writer_agent.py` - ADK Script generation logic
- `src/agents/adk_image_generate_agent.py` - ADK Image generation with Huh
- `src/model/models.py` - Data structures
- `src/core/session_manager.py` - File management
- `src/main_adk.py` - ADK Main program logic
- `run_adk.py` - ADK Main entry point

### Development Environment
- Python 3.8+
- Google API key required
- All dependencies in requirements.txt
- Comprehensive logging enabled

---

**Last Updated**: September 2024  
**Status**: Phase 2 Complete with ADK (Script + Image Generation)  
**Next Phase**: ADK Audio Generation
