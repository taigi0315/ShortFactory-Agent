# 🎬 ShortFactory Agent

AI-powered short video creation system using Huh character with cosplay capabilities.

## 🚀 Quick Start

```bash
# 1. Set up environment
pip install -r requirements.txt

# 2. Set API key in .env file
echo "GEMINI_API_KEY=your-api-key-here" > .env

# 3. Run the system
python run.py
```

## ✨ What It Does

1. **Input**: Subject (e.g., "What is Python?")
2. **Script**: AI generates 8-scene educational script with cosplay instructions
3. **Character**: Huh character transforms based on subject (e.g., "dress as programmer")
4. **Images**: 8 educational images with consistent Huh character
5. **Output**: All files in `sessions/[uuid]/` directory

## 🎭 Huh Character System

- **Base**: `src/assets/huh.png`
- **Cosplay**: Character transforms based on subject
- **Consistency**: Same character in all scenes
- **Size**: Character stays small, educational content is primary

**Examples**:
- Tech: "Dress as programmer with glasses and hoodie"
- Science: "Wear lab coat and safety glasses"
- History: "Period-appropriate clothing"

## 📁 Project Structure

```
ShortFactory-Agent/
├── run.py                          # Main entry point
├── src/                            # Source code
│   ├── main.py                     # Main program
│   ├── agents/                     # AI Agents
│   │   ├── script_writer_agent.py  # Script generation
│   │   └── huh_image_agent.py      # Image generation
│   ├── core/                       # Core functionality
│   │   ├── models.py               # Data models
│   │   └── session_manager.py      # File management
│   └── assets/                     # Static assets
│       └── huh.png                 # Main character
├── docs/                           # Documentation
├── sessions/                       # Generated content
└── tests/                          # Test files
```

## 🔧 Technical Details

- **AI Models**: Google Gemini 2.0 Flash (script) + Google Flash 2.5 (images)
- **Image Editing**: Text-and-image-to-image for character consistency
- **Session Management**: UUID-based file organization
- **Error Handling**: Robust fallbacks and logging

## 📊 Current Status

**✅ Phase 2 Complete**: Script + Image Generation
- Script generation with cosplay instructions
- Image generation with Huh character
- Session management system

**🚧 Next Phase**: Audio Generation
- Text-to-speech for each scene
- Voice tone matching
- Audio file generation

## 🛠️ Development

### Prerequisites
- Python 3.8+
- Google API key
- All dependencies in `requirements.txt`

### Adding New Agents
1. Create agent file in `src/agents/`
2. Follow existing patterns (error handling, logging)
3. Update documentation
4. Add tests in `tests/`

## 📚 Documentation

- **[Development Plan](docs/DEVELOPMENT-PLAN.md)** - Complete development roadmap with checkboxes
- **[Comprehensive Guide](docs/COMPREHENSIVE-GUIDE.md)** - Complete development guide
- **[Architecture](docs/architecture.md)** - System design
- **[Project Structure](docs/project-structure.md)** - File organization

## 🤝 Contributing

1. Follow the established file structure
2. Document all changes
3. Add tests for new features
4. Use comprehensive logging
5. Follow Python best practices

---

**Last Updated**: September 2024  
**Status**: Phase 2 Complete (Script + Image Generation)  
**Next Phase**: Audio Generation