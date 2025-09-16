# ShortFactory-Agent Knowledge Transfer Document

## 📋 Project Overview

**ShortFactory-Agent** is an AI-powered video creation system that generates short educational videos using multiple specialized agents. The system creates videos with a consistent cartoon character "Huh" and applies various cosplay styles based on the subject matter.

## 🏗️ Architecture

### Core Components
- **Script Writer Agent**: Generates video scripts using Google Gemini AI
- **Image Generate Agent**: Creates images using Google Flash 2.5 (Nano Banana) with character consistency
- **Audio Generate Agent**: (Planned) Text-to-speech generation
- **Video Generate Agent**: (Planned) Final video assembly

### Key Technologies
- **Google Generative AI SDK**: For script generation and image creation
- **Google Flash 2.5 (Nano Banana)**: Image generation model
- **Pydantic Models**: Structured data validation
- **Session Management**: UUID-based file organization
- **Character Consistency**: Using base character + image editing

## 📁 Project Structure

```
ShortFactory-Agent/
├── src/
│   ├── agents/
│   │   ├── script_writer_agent.py      # Script generation
│   │   └── image_generate_agent.py     # Image generation
│   ├── core/
│   │   ├── session_manager.py          # Session management
│   │   └── __init__.py
│   ├── model/
│   │   └── models.py                   # Pydantic data models
│   └── main.py                         # Main entry point
├── assets/
│   └── huh.png                         # Main character image
├── sessions/                           # Generated content storage
│   └── [uuid]/                         # Session folders
│       ├── prompts/
│       │   ├── image/                  # Image generation prompts
│       │   └── video/                  # Video generation prompts (future)
│       ├── images/                     # Generated images
│       ├── audios/                     # Generated audio (future)
│       ├── videos/                     # Generated videos (future)
│       ├── script.json                 # Generated script
│       └── metadata.json               # Session metadata
├── docs/
│   └── DEVELOPMENT-PLAN.md             # Development roadmap
├── .env                                # Environment variables
├── run.py                              # Simple runner script
├── test_auto.py                        # Automated testing
└── KT.md                               # This knowledge transfer document
```

## 🔧 Environment Configuration

### Required Environment Variables
```env
GEMINI_API_KEY="your_google_api_key_here"
IMAGE_RATIO=vertical                    # 'vertical' (9:16) or 'horizontal' (16:9)
NUMBER_OF_IMAGE_TO_VIDEO=5             # Future use for video generation
```

### Image Ratio Options
- **vertical**: 720x1280 (9:16) - Mobile/social media format
- **horizontal**: 1280x720 (16:9) - Desktop/widescreen format

## 🎭 Character System

### Huh Character
- **Base Image**: `assets/huh.png`
- **Type**: Cute, blob-like cartoon character
- **Usage**: Appears in all scenes with consistent style
- **Cosplay**: Can be dressed up for different topics (e.g., "cosplay like Elon Musk")

### Character Consistency Strategy
1. **Base Character**: Load `huh.png` as base image
2. **Cosplay Transformation**: Apply cosplay instructions using image editing
3. **Scene Generation**: Use cosplayed character in all scene images
4. **Style Preservation**: Maintain Huh's original design and personality

## 🤖 Agent Details

### Script Writer Agent (`script_writer_agent.py`)
- **Purpose**: Generate video scripts with scene-by-scene breakdown
- **AI Model**: Google Gemini
- **Output**: JSON structure with scenes, dialogue, and image prompts
- **Key Features**:
  - Enforces Huh character usage
  - Includes emotional expressions
  - Adds speech bubbles/text boxes
  - Preserves character style
  - Supports various scene types and transitions

### Image Generate Agent (`image_generate_agent.py`)
- **Purpose**: Generate all images for the video
- **AI Model**: Google Flash 2.5 (Nano Banana)
- **Key Features**:
  - Character consistency through image editing
  - Cosplay transformation
  - Scene-specific image generation
  - Prompt saving for debugging
  - Support for vertical/horizontal ratios
  - Mock generation for testing
  - **Status**: ✅ Fully functional and tested

## 📊 Data Models

### Core Models (`src/model/models.py`)
- **VideoScript**: Main script structure
- **Scene**: Individual scene with dialogue, image prompts, etc.
- **SceneType**: Enum for scene types (hook, content, transition, conclusion)
- **ImageStyle**: Enum for image styles
- **VoiceTone**: Enum for voice characteristics
- **TransitionType**: Enum for scene transitions
- **HookTechnique**: Enum for opening techniques

### Key Fields Added
- **character_expression**: Emotional expressions (smiling, winking, etc.)
- **character_pose**: Character actions (pointing, thinking, etc.)
- **background_description**: Scene background details
- **character_cosplay_instructions**: How to dress up Huh

## 🔄 Workflow

### End-to-End Process
1. **Session Creation**: Generate UUID and create session folder
2. **Script Generation**: Create video script with Huh character
3. **Character Cosplay**: Transform Huh based on cosplay instructions
4. **Image Generation**: Create scene images using cosplayed character
5. **Prompt Saving**: Save all prompts for debugging and tracing
6. **File Organization**: Store all outputs in structured session folder

### Session Management
- **UUID-based**: Each session gets unique identifier
- **Structured Storage**: Organized folders for different content types
- **Metadata Tracking**: Session information and timestamps
- **Prompt Archiving**: All generation prompts saved for analysis

## 🚀 Usage

### Running the System
```bash
# Manual execution
python run.py

# Automated testing
python test_auto.py
```

### Input
- **Subject**: Topic for the video (e.g., "What is all about K-pop demon hunters?")
- **Language**: Currently supports English

### Output
- **Script**: JSON file with scene breakdown
- **Images**: PNG files for each scene
- **Prompts**: Text files with generation prompts
- **Metadata**: Session information

## 🐛 Known Issues & Solutions

### Import Path Issues
- **Problem**: Relative imports causing module not found errors
- **Solution**: Use absolute imports within `src/` directory
- **Files Affected**: All agent files, core modules

### Character Path Issues
- **Problem**: Huh character image not found
- **Solution**: Use `Path("src/assets/huh.png")` for correct path
- **Location**: `image_generate_agent.py`

### Mock vs Real Generation
- **Mock Mode**: Used when API key is missing or for testing
- **Real Mode**: Uses Google AI models for actual generation
- **Toggle**: Automatically switches based on API key availability

## 🔮 Future Development

### Planned Features
- **Audio Generation Agent**: Text-to-speech for dialogue
- **Video Generation Agent**: Final video assembly
- **Performance Optimization**: Speed and API usage improvements
- **Multi-language Support**: Beyond English
- **Advanced Character Customization**: More cosplay options

### Technical Debt
- **Error Handling**: More robust error recovery
- **API Rate Limiting**: Handle Google AI API limits
- **Image Quality**: Optimize image generation parameters
- **Testing Coverage**: More comprehensive test suite

## 📚 Key Learnings

### Google AI Integration
- **SDK**: Use `google-generativeai` package
- **Models**: Gemini for text, Flash 2.5 for images
- **Image Editing**: Text-and-image-to-image for character consistency
- **API Keys**: Store in `.env` file for security

### Character Consistency
- **Base Image**: Always start with same character
- **Image Editing**: Use base + prompt for transformations
- **Style Preservation**: Explicit instructions to maintain character design
- **Cosplay System**: Flexible character customization

### Session Management
- **UUID**: Unique identifiers for each session
- **Structured Storage**: Organized file system
- **Prompt Archiving**: Save all generation prompts
- **Metadata Tracking**: Session information and timestamps

## 🎯 Success Metrics

### Completed Features
- ✅ Script generation with AI
- ✅ Character consistency system
- ✅ Image generation with cosplay
- ✅ Session management
- ✅ Prompt saving and tracing
- ✅ Vertical/horizontal ratio support
- ✅ Emotional expressions and speech bubbles
- ✅ Style preservation
- ✅ File cleanup and organization
- ✅ Git repository optimization

### Quality Indicators
- **Character Consistency**: Huh appears in all scenes with same style
- **Educational Content**: Meaningful, informative images
- **Prompt Quality**: Detailed, specific generation prompts
- **File Organization**: Clean, structured session folders
- **Error Handling**: Graceful fallbacks and logging

## 🔧 Maintenance Notes

### Regular Tasks
- **API Key Management**: Keep Google API keys updated
- **Model Updates**: Monitor Google AI model changes
- **File Cleanup**: Remove old session folders periodically
- **Documentation**: Update this KT document with changes

### Troubleshooting
- **Import Errors**: Check Python path and import statements
- **Image Generation**: Verify API keys and model availability
- **File Paths**: Ensure correct relative/absolute paths
- **Session Issues**: Check UUID generation and folder creation

## 📞 Contact & Support

### Development Team
- **Primary Developer**: AI Assistant (Claude)
- **Project Owner**: User (changikchoi)
- **Repository**: ShortFactory-Agent

### Resources
- **Documentation**: `docs/DEVELOPMENT-PLAN.md`
- **Code**: `src/` directory
- **Examples**: `sessions/` directory
- **Configuration**: `.env` file

---

**Last Updated**: End of development session
**Version**: 1.1
**Status**: Image Generation System Complete - Ready for Audio/Video Agents

This knowledge transfer document should provide comprehensive context for any developer taking over this project. All major components, workflows, and technical decisions are documented here.
