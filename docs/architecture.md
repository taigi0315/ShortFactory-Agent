# ShortFactory Agent - New Multi-Agent Architecture

*Last updated: September 17, 2025*

## 🎯 Project Overview

**ShortFactory Agent** has been completely redesigned with a **true multi-agent architecture** that separates concerns, improves quality, and enables production-ready video generation. The new system transforms a simple topic into a polished, narrated short video with multiple frames per scene.

## 🏗️ New Architecture Design

### Core Principles

1. **True Autonomous Agents**: Each agent has a clear, specific role
2. **Strict Data Contracts**: JSON schemas enforce consistency
3. **Production-Ready Output**: Rich scene details, grounded facts, valid prompts
4. **Validation Loops**: Multiple validation layers ensure quality
5. **Separation of Concerns**: High-level planning vs. detailed execution

---

## 🤖 Agent Roster & Responsibilities

### A) Full Script Writer (FSW)
**File**: `src/agents/full_script_writer_agent.py`

**Mission**: Draft the whole story and high-level pacing. Decide on scene count, type, and macro flags.

**Inputs**:
- `topic` (string)
- `length_preference` (e.g., "60-90s")
- `style_profile` (tone, target audience)
- `knowledge_refs` (optional citations)

**Outputs** (follows `schemas/FullScript.json`):
- `title`, `logline`, `overall_style`, `main_character`, `cosplay_instructions`
- `story_summary` (120-500 words)
- `scenes[]`: High-level beats, learning objectives, animation needs, transitions, importance levels

**Key Features**:
- Does NOT specify low-level prompts or TTS settings
- Focuses on narrative flow and educational value
- Uses story focus engine for engagement
- Validates story feasibility and complexity

---

### B) Scene Script Writer (SSW)
**File**: `src/agents/scene_script_writer_agent.py`

**Mission**: Take each FSW scene beat and expand it into a production-ready scene package.

**Inputs**:
- Single `scene` object from FSW
- `global_context` (characters, style, constraints)
- `educational_enhancement_guidelines`
- `previous_scenes` (for continuity)

**Outputs** (follows `schemas/ScenePackage.json`):
- `scene_number`
- `narration_script` (timed chunks with pauses)
- `dialogue[]` (speaker, line, on-screen text)
- `visuals[]` (detailed storyboard frames):
  - Frame specifications: shot_type, camera_motion, character_pose, expression
  - Image generation: detailed prompts, negative prompts, model hints
  - Technical specs: aspect_ratio, seed, guidance_scale
- `tts` (engine, voice, elevenlabs_settings)
- `sfx_cues[]`, `on_screen_text[]`
- `timing` (total_ms, per-line timings)
- `continuity` (transitions, callback_tags)
- `safety_checks` (validation results)

**Key Features**:
- Performs ELABORATION (adds hooks, facts, metaphors)
- Creates 3-8 visual frames per scene for rich storytelling
- Maintains character and visual consistency
- Handles all production-level details

---

### C) Image Create Agent (ICA)
**File**: `src/agents/image_create_agent.py`

**Mission**: Generate images that exactly match SSW frame specifications.

**Inputs**:
- SSW `visuals[]` with prompts, negative prompts, seeds, style, aspect ratio

**Outputs** (follows `schemas/ImageAsset.json`):
- `frame_id`, `image_uri`, `thumbnail_uri`
- `prompt_used`, `negative_prompt_used`
- `model`, `sampler`, `cfg`, `steps`, `seed`
- `safety_result`, `generation_time_ms`
- `metadata` (dimensions, file size, format)

**Key Features**:
- Echoes back final prompts with resolved variables
- Performs prompt sanitation (no PII/NSFW)
- Maintains character consistency with Huh reference
- Supports cost-saving mode with mock images

---

### D) Voice Generate Agent (VGA)
**File**: `src/agents/voice_generate_agent.py`

**Mission**: Generate high-quality TTS audio files for each scene using ElevenLabs API.

**Inputs**:
- SSW scene packages with `narration_script` and `elevenlabs_settings`

**Outputs**:
- MP3 audio files saved to `sessions/{session_id}/voices/`
- Voice asset metadata with generation details
- Ordered filenames: `scene_01_voice.mp3`, `scene_02_voice.mp3`, etc.

**Key Features**:
- ElevenLabs TTS integration with scene-specific settings
- Automatic text extraction from narration scripts
- Default voice fallback for free accounts
- Comprehensive metadata logging
- Error handling with detailed API response logging

---

### E) Orchestrator Agent
**File**: `src/agents/orchestrator_agent.py`

**Mission**: State machine controlling the entire pipeline. Manages retries, validation, and fallbacks.

**Responsibilities**:
- Pipeline orchestration and flow control
- JSON schema validation for all outputs
- Error handling and retry mechanisms
- Build reporting and timing analysis
- Session management and file organization

**Outputs**:
- Complete build report with timing and model usage
- Session artifacts (scripts, images, metadata)
- Error tracking and failure analysis

---

## 🔄 System Architecture & Data Flow

```
User Topic → FSW → SSW (per scene) → ICA (per frame) → Final Assembly
            ↓       ↓                  ↓
         Schema   Schema            Schema
       Validation Validation      Validation
```

### Pipeline Stages

1. **Stage 1**: Full Script Writer generates high-level story structure                                                               
2. **Stage 2**: Scene Script Writer expands each scene into detailed packages                                                         
3. **Stage 3**: Image Create Agent generates images for all frames                                                                    
4. **Stage 4**: Voice Generate Agent creates TTS audio files
5. **Stage 5**: Final assembly and build report generation

### Data Contracts

- **Strict JSON Schemas**: Each handoff uses validated JSON structures
- **Idempotency**: Deterministic seeds for reproducible results
- **Caching**: Potential for caching by content hash
- **Validation Gates**: Schema → Semantic → Safety checks

---

## 📁 File Structure

```
src/
├── agents/
│   ├── full_script_writer_agent.py      # FSW - High-level story planning
│   ├── scene_script_writer_agent.py     # SSW - Detailed scene packages
│   ├── image_create_agent.py            # ICA - Image generation
│   ├── voice_generate_agent.py          # VGA - TTS voice generation
│   ├── orchestrator_agent.py            # Pipeline management
│   └── [legacy agents...]               # Old architecture (to be cleaned)
├── schemas/
│   ├── FullScript.json                  # FSW output schema
│   ├── ScenePackage.json               # SSW output schema
│   └── ImageAsset.json                 # ICA output schema
├── main_new_architecture.py            # New architecture main
└── [core modules...]                   # Shared utilities

sessions/YYYYMMDD-{uuid}/
├── full_script.json                    # FSW output
├── scene_package_{N}.json             # SSW outputs
├── image_assets.json                   # ICA metadata
├── voice_assets.json                   # VGA metadata
├── build_report.json                   # Complete build info
├── prompts/                            # All agent prompts/responses
│   ├── full_script_writer_*
│   ├── scene_script_writer_*
│   ├── image_create_agent_*
│   └── voice_generate_scene_*_metadata.json
├── images/                             # Generated images
│   ├── 1a.png, 1b.png, ...            # Scene 1 frames
│   ├── 2a.png, 2b.png, ...            # Scene 2 frames
│   └── ...
└── voices/                             # Generated voice files
    ├── scene_01_voice.mp3              # Scene 1 TTS audio
    ├── scene_02_voice.mp3              # Scene 2 TTS audio
    └── ...
```

---

## 🔬 Validation & Quality Control

### Static Validators
- **JSON Schema Validation**: Enforces structure compliance
- **Field Validation**: Required fields, data types, value ranges
- **Content Safety**: Prompt sanitation, NSFW detection

### Semantic Validators
- **Continuity Checks**: Character, props, visual consistency
- **Educational Quality**: Learning objectives, fact grounding
- **Narrative Flow**: Story progression, engagement hooks

### Runtime Validators
- **Image-Text Matching**: CLIP similarity scoring
- **Timing Validation**: Speech duration vs. visual duration
- **Safety Results**: Content safety and appropriateness

---

## 🚀 Usage

### Basic Usage
```bash
python run_new_architecture.py "Your Topic Here" --cost
```

### Advanced Options
```bash
python run_new_architecture.py "Climate Change" \
  --length "2-3min" \
  --style "serious and informative" \
  --audience "university students" \
  --cost
```

### Test Mode
```bash
python run_new_architecture.py --test --cost
```

---

## 📈 Performance Metrics

**Typical Generation (5 scenes, 25 images)**:
- **Full Script Writer**: ~25 seconds
- **Scene Script Writer**: ~300 seconds (5 scenes × ~60s each)
- **Image Generation**: <1 second (cost-saving mode)
- **Total Time**: ~5-6 minutes

**Output Quality**:
- Rich narrative structure with educational depth
- 3-8 visual frames per scene for cinematic storytelling
- Production-ready TTS settings and timing
- Comprehensive metadata and build reporting

---

## 🔄 Migration from Legacy

The new architecture completely replaces the old system:

**Old System** (deprecated):
- `src/main_adk.py` → Single monolithic workflow
- `src/agents/adk_script_writer_agent.py` → Combined script+scene generation
- Mixed responsibilities and unclear data flow

**New System**:
- Clear separation of concerns
- Standardized JSON contracts
- Comprehensive validation
- Production-ready output quality

---

## 🎯 Next Steps

1. **Video Assembly**: Implement FFmpeg timeline composition
2. **Advanced Validation**: Semantic consistency checks
3. **Performance Optimization**: Parallel scene processing
4. **Web Interface**: Scene preview and editing tools
5. **Advanced Models**: Integration with specialized image/audio models

---

## 📊 Current Implementation Status

✅ **Completed (100%)**:
- Multi-agent architecture design
- JSON schema definitions
- Full Script Writer implementation
- Scene Script Writer implementation
- Image Create Agent implementation
- Voice Generate Agent implementation
- Orchestrator implementation
- Session management with date prefixes
- Comprehensive prompt/response logging
- Cost-saving mode support

🔄 **In Progress (0%)**:
- Video assembly pipeline
- Advanced semantic validation
- Performance optimization

📋 **Planned**:
- Web interface for content review
- Advanced model integrations
- Batch processing capabilities
