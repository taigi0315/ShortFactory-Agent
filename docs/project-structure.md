# Project Structure

## 📁 Directory Structure

```
ShortFactory-Agent/
├── run.py                          # Main entry point (use this to run)
├── src/                            # Source code
│   ├── main.py                     # Main program logic
│   ├── agents/                     # AI Agents
│   │   ├── script_writer_agent.py  # Generates video scripts with cosplay
│   │   └── huh_image_agent.py      # Generates images using Huh character
│   ├── core/                       # Core functionality
│   │   ├── models.py               # Pydantic data models
│   │   └── session_manager.py      # Session and file management
│   ├── assets/                     # Static assets
│   │   └── huh.png                 # Main character image
│   └── utils/                      # Utility functions
├── docs/                           # Documentation
├── examples/                       # Example scripts
├── sessions/                       # Generated content (UUID-based)
│   └── [session-id]/
│       ├── script.json             # Generated script
│       ├── images/                 # Generated images
│       │   └── scene_1.png
│       ├── audios/                 # Future: Generated audio
│       ├── videos/                 # Future: Generated video
│       └── metadata.json           # Session metadata
└── tests/                          # Test files
```

## 🎯 Key Files

### Entry Points
- **`run.py`** - Main entry point (recommended)
- **`src/main.py`** - Main program logic

### AI Agents
- **`src/agents/script_writer_agent.py`** - Generates video scripts with cosplay instructions
- **`src/agents/huh_image_agent.py`** - Generates images using Huh character

### Core Components
- **`src/core/models.py`** - Pydantic data models (VideoScript, Scene, etc.)
- **`src/core/session_manager.py`** - Session and file management

### Assets
- **`src/assets/huh.png`** - Main character image for cosplay system

## 🚀 How to Run

```bash
# Recommended way
python run.py

# Alternative way
python src/main.py
```

## 📊 Session Structure

Each session creates a UUID-based directory with:
- `script.json` - Generated video script
- `images/scene_X.png` - Generated images for each scene
- `audios/` - Future: Generated audio files
- `videos/` - Future: Generated video files
- `metadata.json` - Session progress and file information
- `logs/session.log` - Detailed execution logs

## 🔧 Development Guidelines

### Adding New Agents
1. Create agent file in `src/agents/`
2. Follow existing patterns (error handling, logging)
3. Update documentation
4. Add tests in `tests/`

### File Organization
- **Agents**: `src/agents/`
- **Core Logic**: `src/core/`
- **Utilities**: `src/utils/`
- **Assets**: `src/assets/`
- **Documentation**: `docs/`
- **Examples**: `examples/`
- **Tests**: `tests/`

### Import Structure
```python
# For agents
from ..models.models import VideoScript
from ..core.session_manager import SessionManager

# For main program
from session_manager import SessionManager
from script_writer_agent import ScriptWriterAgent
from huh_image_agent import HuhImageAgent
```

## 📈 Current Status

### ✅ Completed
- Script generation with cosplay instructions
- Image generation using Huh character
- Session management system
- Comprehensive documentation

### 🚧 Next Phase
- Audio generation agent
- Video generation agent
- Final video assembly

## 🎭 Character System

The project uses a consistent character system:
- **Base Character**: Huh (from `src/assets/huh.png`)
- **Cosplay System**: Character can be transformed based on subject
- **Consistency**: Same character appears in all scenes
- **Educational Focus**: Character stays small, content is primary