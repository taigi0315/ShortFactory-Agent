# 🎬 ShortFactory Agent

**Production-Ready Multi-Agent Video Creation System**

Transform any topic into a polished, narrated short video with rich visual storytelling using our advanced multi-agent architecture.

## 🚀 Quick Start

```bash
# 1. Set up environment
pip install -r requirements.txt

# 2. Set API key in .env file
echo "GEMINI_API_KEY=your-api-key-here" > .env

# 3. Run the new architecture system
python run_shortfactory.py "Your Topic Here" --cost
```

## ✨ What It Does

**New Multi-Agent Architecture** creates production-ready video content:

1. **📖 Story Planning**: AI analyzes topic and creates engaging narrative structure (3-8 scenes)
2. **🎬 Scene Production**: Each scene expanded into detailed production package with timing
3. **🖼️ Visual Creation**: 3-8 visual frames per scene for rich storytelling (15-40 images total)
4. **🎭 Character Consistency**: Huh character maintains cosplay throughout all frames
5. **📊 Quality Control**: Multi-layer validation and comprehensive build reporting

## 🏗️ New Architecture Overview

### **True Multi-Agent System**:
- **Full Script Writer (FSW)**: High-level story structure and scene planning
- **Scene Script Writer (SSW)**: Production-ready scene packages with timing
- **Image Create Agent (ICA)**: Visual asset generation with metadata
- **Orchestrator**: Pipeline management and validation

### **Production-Ready Output**:
- Detailed narration scripts with millisecond timing
- Complete TTS settings (ElevenLabs configuration)
- Rich visual specifications (shot types, camera motion, lighting)
- Comprehensive metadata and build reports

## 🎯 Usage Examples

### Basic Usage
```bash
# Generate video about any topic
python run_shortfactory.py "Climate Change" --cost

# Educational content
python run_shortfactory.py "Why are dachshunds short?" --cost

# Technology topics
python run_shortfactory.py "Quantum Computing" --cost
```

### Advanced Options
```bash
# Specify length and style
python run_shortfactory.py "Artificial Intelligence" \
  --length "2-3min" \
  --style "serious and informative" \
  --audience "university students" \
  --cost

# With knowledge references
python run_shortfactory.py "Blockchain Technology" \
  --refs "https://bitcoin.org/bitcoin.pdf" \
  --cost
```

### Test Mode
```bash
# Run with sample content
python run_shortfactory.py --test --cost
```

## 📁 Output Structure

Each generation creates a comprehensive session:

```
sessions/20250916-{uuid}/
├── full_script.json              # High-level story structure
├── scene_package_1.json          # Detailed scene 1 package
├── scene_package_2.json          # Detailed scene 2 package
├── scene_package_N.json          # Additional scenes
├── image_assets.json             # All image metadata
├── build_report.json             # Generation metrics & errors
├── prompts/                      # Complete audit trail
│   ├── full_script_writer_*      # Story planning prompts/responses
│   ├── scene_script_writer_*     # Scene expansion prompts/responses
│   └── image_create_agent_*      # Image generation prompts/metadata
└── images/                       # Generated visual assets
    ├── 1a.png, 1b.png, 1c.png   # Scene 1 frames
    ├── 2a.png, 2b.png, 2c.png   # Scene 2 frames
    └── ...                      # Additional scene frames
```

## 🎭 Huh Character System

- **Base Character**: `src/assets/huh.png` - Cute, blob-like cartoon character
- **Dynamic Cosplay**: Character transforms based on topic (e.g., scientist, historian, programmer)
- **Visual Consistency**: Same character appearance maintained across all frames
- **Rich Expressions**: Multiple poses and expressions for engaging storytelling

## 🔧 Technical Features

### **JSON Schema Validation**
- Strict data contracts between agents
- Runtime validation with detailed error reporting
- Graceful degradation on validation warnings

### **Comprehensive Logging**
- All agent prompts and responses saved
- Complete build reports with timing and metrics
- Error tracking and debugging information

### **Cost Control**
- `--cost` flag uses mock images for development
- AI text generation (inexpensive) always enabled
- Full AI mode available for production

### **Session Management**
- Date-prefixed session IDs (YYYYMMDD-UUID)
- Organized file structure for easy navigation
- Metadata tracking for all generated content

## 📊 Performance

**Typical Generation** (5 scenes, 25 images):
- **Story Planning**: ~25 seconds
- **Scene Expansion**: ~300 seconds
- **Image Generation**: <1 second (cost-saving) / ~60 seconds (AI)
- **Total**: ~5-6 minutes for complete video package

## 🔄 Migration Guide

### From Legacy System:
- **Old**: `python run_adk.py "Topic" --cost`
- **New**: `python run_shortfactory.py "Topic" --cost`

### Key Improvements:
- 🎯 **Separation of Concerns**: Each agent has a clear, specific role
- 📊 **Rich Output**: 3-8 frames per scene vs. 1 image per scene
- 🔍 **Quality Control**: Multi-layer validation and safety checks
- 📁 **Organization**: Structured sessions with comprehensive metadata
- 🐛 **Debugging**: Complete audit trail for troubleshooting

## 📚 Documentation

- **[New Architecture Guide](docs/NEW-ARCHITECTURE.md)**: Complete system overview
- **[Architecture Diagrams](docs/NEW-ARCHITECTURE-DIAGRAM.md)**: Visual system design
- **[Agents & Validators](docs/AGENTS-AND-VALIDATORS.md)**: Detailed component guide
- **[Project Status](docs/PROJECT-STATUS-2025.md)**: Current implementation status

## 🎉 Recent Achievements

**September 16, 2025**: ✅ **Major Architecture Milestone**
- Complete multi-agent system implementation
- Production-ready output quality
- Comprehensive validation and error handling
- Rich visual storytelling with multiple frames per scene

## 🚀 Next Steps

1. **Video Assembly**: FFmpeg integration for final video compilation
2. **Web Interface**: Content preview and editing tools
3. **Performance**: Parallel processing and optimization
4. **Advanced Models**: Specialized audio and video generation

---

**Ready to create amazing educational videos? Start with:**
```bash
python run_shortfactory.py "Your Fascinating Topic" --cost
```