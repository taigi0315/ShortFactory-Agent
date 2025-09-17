# Project Structure

## 📁 Directory Structure

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

## 🎯 Key Files

### Entry Points
- **`run_adk.py`** - ADK Main entry point (recommended)
- **`src/main_adk.py`** - ADK Main program logic

### ADK Agents
- **`src/agents/adk_script_writer_agent.py`** - ADK Script generation with cosplay instructions
- **`src/agents/adk_image_generate_agent.py`** - ADK Image generation using Huh character

### Core Components
- **`src/model/models.py`** - Pydantic data models (VideoScript, Scene, etc.)
- **`src/core/session_manager.py`** - Session and file management

### Assets
- **`src/assets/huh.png`** - Main character image for cosplay system

## 🚀 How to Run

```bash
# Recommended way
python run_adk.py

# Alternative way
python src/main_adk.py
```

## 📊 Session Structure

Each session creates a UUID-based directory with:
- `script.json` - Generated video script
- `images/scene_X.png` - Generated images for each scene
- `prompts/` - Saved prompts for debugging
  - `image/scene_X.txt` - Image generation prompts
  - `video/scene_X.txt` - Video generation prompts (future)
- `audios/` - Future: Generated audio files
- `videos/` - Future: Generated video files
- `metadata.json` - Session progress and file information
- `logs/session.log` - Detailed execution logs

## 🔧 Development Guidelines

### Adding New ADK Agents
1. Create ADK agent file in `src/agents/` (e.g., `adk_audio_generate_agent.py`)
2. Follow ADK patterns (inherit from `Agent` class)
3. Implement error handling and logging
4. Update documentation
5. Add tests in `tests/`

### File Organization
- **ADK Agents**: `src/agents/`
- **Core Logic**: `src/core/`
- **Data Models**: `src/model/`
- **Utilities**: `src/utils/`
- **Assets**: `src/assets/`
- **Documentation**: `docs/`
- **Tests**: `tests/`

### Import Structure
```python
# For ADK agents
from ..model.models import VideoScript
from ..core.session_manager import SessionManager

# For main ADK program
from core.session_manager import SessionManager
from agents.adk_script_writer_agent import ADKScriptWriterAgent
from agents.adk_image_generate_agent import ADKImageGenerateAgent
```

## 📈 Current Status

### ✅ Completed
- ADK Script generation with cosplay instructions
- ADK Image generation using Huh character
- Actual Gemini 2.5 Flash Image API integration
- Session management system
- Comprehensive documentation

### 🚧 Next Phase
- ADK Audio generation agent
- ADK Video generation agent
- Final video assembly

## 🎭 Character System

The project uses a consistent character system:
- **Base Character**: Huh (from `src/assets/huh.png`)
- **Cosplay System**: Character can be transformed based on subject
- **Consistency**: Same character appears in all scenes
- **Educational Focus**: Character stays small, content is primary